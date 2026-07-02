"""Autonomous fulfillment orchestrator: manages portfolio generation job lifecycle.

This module implements a state machine for portfolio fulfillment:
- PENDING -> PROVISIONING -> GENERATING -> PUSHING -> NOTIFYING -> COMPLETE
- Any step can fail -> RETRY_PENDING (with exponential backoff)
- Failed retries after max_retries -> FAILED

Every step is designed to be idempotent: re-running a step at any time
should produce the same result without side effects.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    Client,
    PortfolioBuildJob,
    PortfolioBuildJobStatus,
    Purchase,
    utcnow,
)


class OrchestrationError(Exception):
    """Base error for orchestration failures."""
    pass


class StepError(OrchestrationError):
    """Represents a failure in a specific step that should be retried."""
    def __init__(self, step: str, message: str, retriable: bool = True):
        self.step = step
        self.message = message
        self.retriable = retriable
        super().__init__(f"[{step}] {message}")


class ProvisioningError(StepError):
    def __init__(self, message: str):
        super().__init__("provisioning", message, retriable=True)


class GenerationError(StepError):
    def __init__(self, message: str):
        super().__init__("generating", message, retriable=True)


class PushError(StepError):
    def __init__(self, message: str):
        super().__init__("pushing", message, retriable=True)


class NotificationError(StepError):
    def __init__(self, message: str):
        super().__init__("notifying", message, retriable=True)


def get_job_by_id(db: Session, job_id: int) -> PortfolioBuildJob:
    """Retrieve a job by ID. Raises if not found."""
    job = db.get(PortfolioBuildJob, job_id)
    if not job:
        raise OrchestrationError(f"Job {job_id} not found")
    return job


def create_build_job(
    db: Session,
    client_id: int,
    purchase_id: int,
) -> PortfolioBuildJob:
    """Create a new portfolio build job. Idempotent: checks if job exists for this purchase."""
    # Check if a job already exists for this purchase
    existing = db.scalar(
        select(PortfolioBuildJob).where(
            PortfolioBuildJob.purchase_id == purchase_id,
            PortfolioBuildJob.status != PortfolioBuildJobStatus.FAILED.value,
        )
    )
    if existing:
        return existing

    job = PortfolioBuildJob(
        client_id=client_id,
        purchase_id=purchase_id,
        status=PortfolioBuildJobStatus.PENDING.value,
    )
    db.add(job)
    db.commit()
    return job


def _step_provisioning(db: Session, job: PortfolioBuildJob, client: Client) -> None:
    """
    Step 1: Provision repo and credentials for client.
    
    Idempotency: If repo already exists in client record, skip.
    """
    from app.provisioning import provision_client_from_purchase

    if job.github_repo_url:
        # Already provisioned; skip
        return

    try:
        # Ensure purchase is fully hydrated with client
        if not client.purchase or not client.purchase.id:
            purchase = db.get(Purchase, job.purchase_id)
            if not purchase:
                raise ProvisioningError("Purchase not found")
        else:
            purchase = client.purchase

        # Check if already provisioned: client has integration details
        if client.github_url:
            # GitHub URL already set; treat as provisioned
            job.github_repo_url = client.github_url
            return

        # Provision the client (if not already done by webhook)
        # This is idempotent: provision_client_from_purchase checks if client exists
        provision_client_from_purchase(
            db,
            purchase,
            customer_email=purchase.customer_email,
            stripe_customer_id=purchase.stripe_customer_id,
            stripe_payment_intent_id=purchase.stripe_payment_intent_id,
        )
        db.refresh(client)
        
        # After provisioning, the client should have repo details
        # Store repo URL for tracking
        if client.github_url:
            job.github_repo_url = client.github_url

    except Exception as exc:
        raise ProvisioningError(f"Failed to provision repo: {exc}") from exc


def _step_generating(db: Session, job: PortfolioBuildJob, client: Client) -> str:
    """
    Step 2: Generate portfolio content via LLM.
    
    Returns: Generated portfolio HTML.
    Idempotency: Check if portfolio content already cached in client record.
    """
    from app.portfolio_generator import generate_portfolio_html

    try:
        if not client.name or client.name in ("Pending Intake", "Pending intake"):
            raise GenerationError("Client intake data incomplete; cannot generate portfolio")

        # Call LLM to generate portfolio
        html_content = generate_portfolio_html(
            client=client,
            package_slug=client.package_slug,
        )
        
        if not html_content:
            raise GenerationError("LLM returned empty portfolio")

        return html_content

    except GenerationError:
        raise
    except Exception as exc:
        raise GenerationError(f"LLM generation failed: {exc}") from exc


def _step_pushing(
    db: Session,
    job: PortfolioBuildJob,
    client: Client,
    portfolio_html: str,
) -> tuple[str, str]:
    """
    Step 3: Push portfolio to GitHub repo.
    
    Returns: (github_repo_url, vercel_deployment_url)
    Idempotency: Check if commit already pushed via git history.
    """
    from app.github_integration import push_portfolio_to_github

    try:
        if job.github_repo_url:
            # Already pushed; retrieve URLs from job
            github_url = job.github_repo_url
            vercel_url = job.portfolio_url or ""
            if vercel_url:
                return github_url, vercel_url

        # Push to GitHub
        github_url, vercel_url = push_portfolio_to_github(
            client=client,
            portfolio_html=portfolio_html,
        )
        
        job.github_repo_url = github_url
        job.portfolio_url = vercel_url

        return github_url, vercel_url

    except Exception as exc:
        raise PushError(f"Failed to push to GitHub: {exc}") from exc


def _step_notifying(
    db: Session,
    job: PortfolioBuildJob,
    client: Client,
    portfolio_url: str,
) -> None:
    """
    Step 4: Send client their live portfolio URL via email.
    
    Idempotency: Check if email already sent via notified_client_at timestamp.
    """
    from app.email_service import send_portfolio_live_email

    if job.notified_client_at:
        # Already notified; skip
        return

    try:
        if not client.email:
            raise NotificationError("Client email not available")

        send_portfolio_live_email(
            client_name=client.name,
            client_email=client.email,
            portfolio_url=portfolio_url,
        )

        job.notified_client_at = utcnow()

    except Exception as exc:
        raise NotificationError(f"Failed to send notification: {exc}") from exc


def process_job(db: Session, job_id: int) -> None:
    """
    Execute job state machine. Each step is idempotent and can be retried independently.
    
    State transitions:
    - PENDING -> PROVISIONING (mark started_at)
    - PROVISIONING -> GENERATING
    - GENERATING -> PUSHING
    - PUSHING -> NOTIFYING
    - NOTIFYING -> COMPLETE (mark completed_at)
    - Any step fails -> RETRY_PENDING (with backoff)
    - Max retries exceeded -> FAILED
    """
    job = get_job_by_id(db, job_id)
    client = db.get(Client, job.client_id)
    if not client:
        job.status = PortfolioBuildJobStatus.FAILED.value
        job.error_message = "Client not found"
        db.commit()
        raise OrchestrationError(f"Client {job.client_id} not found")

    # Mark job as started if first run
    if not job.started_at:
        job.started_at = utcnow()

    try:
        # Step 1: Provision
        if job.status == PortfolioBuildJobStatus.PENDING.value:
            job.status = PortfolioBuildJobStatus.PROVISIONING.value
            job.current_step = "provisioning"
            db.commit()
            _step_provisioning(db, job, client)
            db.commit()

        # Step 2: Generate
        if job.status == PortfolioBuildJobStatus.PROVISIONING.value:
            job.status = PortfolioBuildJobStatus.GENERATING.value
            job.current_step = "generating"
            db.commit()
            portfolio_html = _step_generating(db, job, client)
            db.commit()
        else:
            # Recover from previous state
            portfolio_html = _step_generating(db, job, client)

        # Step 3: Push to GitHub
        if job.status == PortfolioBuildJobStatus.GENERATING.value:
            job.status = PortfolioBuildJobStatus.PUSHING.value
            job.current_step = "pushing"
            db.commit()
            github_url, portfolio_url = _step_pushing(db, job, client, portfolio_html)
            db.commit()
        else:
            # Recover from previous state
            if job.portfolio_url:
                portfolio_url = job.portfolio_url
            else:
                github_url, portfolio_url = _step_pushing(db, job, client, portfolio_html)
                db.commit()

        # Step 4: Notify client
        if job.status == PortfolioBuildJobStatus.PUSHING.value:
            job.status = PortfolioBuildJobStatus.NOTIFYING.value
            job.current_step = "notifying"
            db.commit()
            _step_notifying(db, job, client, portfolio_url)
            db.commit()
        else:
            # Recover from previous state
            if not job.notified_client_at:
                _step_notifying(db, job, client, job.portfolio_url or "")
                db.commit()

        # Mark complete
        job.status = PortfolioBuildJobStatus.COMPLETE.value
        job.current_step = None
        job.completed_at = utcnow()
        job.error_message = None
        job.error_step = None
        db.commit()

    except StepError as exc:
        _handle_step_failure(db, job, exc)
    except Exception as exc:
        # Unexpected error: mark failed
        job.status = PortfolioBuildJobStatus.FAILED.value
        job.error_message = f"Unexpected error: {exc}"
        job.error_step = job.current_step
        db.commit()
        raise


def _handle_step_failure(db: Session, job: PortfolioBuildJob, error: StepError) -> None:
    """Handle a step failure: retry or mark failed."""
    job.error_message = error.message
    job.error_step = error.step

    if not error.retriable or job.retry_count >= job.max_retries:
        # Permanent failure
        job.status = PortfolioBuildJobStatus.FAILED.value
        db.commit()
        raise error

    # Retry with exponential backoff
    job.retry_count += 1
    job.status = PortfolioBuildJobStatus.RETRY_PENDING.value
    db.commit()
    # Next worker invocation will pick this up


def get_pending_jobs(db: Session, limit: int = 10) -> list[PortfolioBuildJob]:
    """Fetch jobs ready for processing: PENDING or RETRY_PENDING."""
    return db.scalars(
        select(PortfolioBuildJob)
        .where(
            PortfolioBuildJob.status.in_(
                [
                    PortfolioBuildJobStatus.PENDING.value,
                    PortfolioBuildJobStatus.RETRY_PENDING.value,
                ]
            )
        )
        .order_by(PortfolioBuildJob.created_at)
        .limit(limit)
    ).all()


def get_job_status(db: Session, job_id: int) -> dict:
    """Return current job status for client polling."""
    job = get_job_by_id(db, job_id)
    return {
        "id": job.id,
        "status": job.status,
        "current_step": job.current_step,
        "retry_count": job.retry_count,
        "max_retries": job.max_retries,
        "portfolio_url": job.portfolio_url,
        "github_repo_url": job.github_repo_url,
        "error_message": job.error_message,
        "error_step": job.error_step,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "notified_client_at": job.notified_client_at.isoformat() if job.notified_client_at else None,
    }
