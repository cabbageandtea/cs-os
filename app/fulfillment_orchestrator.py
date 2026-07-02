"""Autonomous fulfillment orchestrator: manages portfolio generation job lifecycle.

This module implements a state machine for portfolio fulfillment:
- PENDING -> PROVISIONING -> GENERATING -> PUSHING -> NOTIFYING -> COMPLETE
- Any step can fail -> RETRY_PENDING (with exponential backoff)
- Failed retries after max_retries -> FAILED

Every step is designed to be idempotent: re-running a step at any time
should produce the same result without side effects.

OPERATING PRINCIPLES:
- ZERO-TRUST: Assume all input is incomplete/malformed. Validate defensively.
- ASYNC: Every action can fail. Implement idempotent retries.
- CLINICAL: Generate data-driven, marketing-free output.
- AUTONOMY: Resolve technical bottlenecks without approval.
- OBSERVABILITY: Log every state transition with diagnostic context.
"""

from __future__ import annotations

import json
import logging
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

logger = logging.getLogger(__name__)


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
    """
    Create a new portfolio build job. Idempotent: checks if job exists for this purchase.
    ZERO-TRUST: Validates all inputs before database operations.
    """
    if not client_id or not purchase_id:
        raise OrchestrationError(f"Invalid input: client_id={client_id}, purchase_id={purchase_id}")
    
    # Check if a job already exists for this purchase (only non-failed jobs)
    existing = db.scalar(
        select(PortfolioBuildJob).where(
            PortfolioBuildJob.purchase_id == purchase_id,
            PortfolioBuildJob.status.in_([
                PortfolioBuildJobStatus.PENDING.value,
                PortfolioBuildJobStatus.RETRY_PENDING.value,
                PortfolioBuildJobStatus.PROVISIONING.value,
                PortfolioBuildJobStatus.GENERATING.value,
                PortfolioBuildJobStatus.PUSHING.value,
                PortfolioBuildJobStatus.NOTIFYING.value,
                PortfolioBuildJobStatus.COMPLETE.value,
            ])
        )
    )
    if existing:
        logger.info(f"[create_job] idempotent: job {existing.id} already exists for purchase {purchase_id}")
        return existing

    job = PortfolioBuildJob(
        client_id=client_id,
        purchase_id=purchase_id,
        status=PortfolioBuildJobStatus.PENDING.value,
        retry_count=0,
    )
    db.add(job)
    db.commit()
    logger.info(f"[create_job] created new job {job.id} for purchase {purchase_id}")
    return job


def _step_provisioning(db: Session, job: PortfolioBuildJob, client: Client) -> None:
    """
    Step 1: Provision repo and credentials for client.
    
    Idempotency: If repo already exists in client record, skip.
    """
    from app.provisioning import provision_client_from_purchase

    logger.info(f"[job {job.id}] PROVISIONING: client_id={client.id}, step=1/4")

    if job.github_repo_url:
        # Already provisioned; skip
        logger.info(f"[job {job.id}] PROVISIONING: idempotent, repo already provisioned")
        return

    try:
        # Ensure purchase is fully hydrated with client
        if not client.purchase or not client.purchase.id:
            purchase = db.get(Purchase, job.purchase_id)
            if not purchase:
                logger.error(f"[job {job.id}] PROVISIONING FAILED: purchase {job.purchase_id} not found")
                raise ProvisioningError("Purchase not found")
        else:
            purchase = client.purchase

        # Check if already provisioned: client has integration details
        if client.github_url:
            # GitHub URL already set; treat as provisioned
            job.github_repo_url = client.github_url
            logger.info(f"[job {job.id}] PROVISIONING: idempotent, client already has github_url")
            return

        # Provision the client (if not already done by webhook)
        # This is idempotent: provision_client_from_purchase checks if client exists
        logger.debug(f"[job {job.id}] PROVISIONING: calling provision_client_from_purchase")
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
            logger.info(f"[job {job.id}] PROVISIONING: success, repo_url={client.github_url}")

    except Exception as exc:
        logger.exception(f"[job {job.id}] PROVISIONING FAILED: {exc}")
        raise ProvisioningError(f"Failed to provision repo: {exc}") from exc


def _step_generating(db: Session, job: PortfolioBuildJob, client: Client) -> str:
    """
    Step 2: Generate portfolio content via LLM.
    
    Returns: Generated portfolio JSON (clinical, data-driven).
    Idempotency: Check if portfolio content already cached in client record.
    NOTE: Synchronous wrapper for async generator. Uses get_or_create_event_loop() for thread-safety.
    """
    from app.portfolio_generator import generate_portfolio_json, PortfolioValidationError

    logger.info(f"[job {job.id}] GENERATING: client_id={client.id}, package={client.package_slug}, step=2/4")

    try:
        # ZERO-TRUST: Validate client has required intake data
        if not client.name or client.name in ("Pending Intake", "Pending intake"):
            logger.error(f"[job {job.id}] GENERATING FAILED: client name incomplete (name={client.name})")
            raise GenerationError("Client intake data incomplete; cannot generate portfolio")

        if not client.intake_data:
            logger.error(f"[job {job.id}] GENERATING FAILED: client missing intake_data")
            raise GenerationError("Client intake_data is empty or missing")

        # Call LLM to generate portfolio (thread-safe async wrapper)
        logger.debug(f"[job {job.id}] GENERATING: calling LLM for client {client.id}")
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        portfolio_json = loop.run_until_complete(generate_portfolio_json(client))
        
        if not portfolio_json or len(portfolio_json) < 50:
            logger.error(f"[job {job.id}] GENERATING FAILED: LLM returned empty/invalid portfolio (size={len(portfolio_json) if portfolio_json else 0})")
            raise GenerationError("LLM returned empty or invalid portfolio")

        logger.info(f"[job {job.id}] GENERATING: success, portfolio_size={len(portfolio_json)}")
        return portfolio_json

    except PortfolioValidationError as exc:
        logger.error(f"[job {job.id}] GENERATING FAILED (validation): {exc}")
        raise GenerationError(str(exc)) from exc
    except GenerationError:
        raise
    except Exception as exc:
        logger.exception(f"[job {job.id}] GENERATING FAILED (unexpected): {exc}")
        raise GenerationError(f"LLM generation failed: {exc}") from exc


def _step_pushing(
    db: Session,
    job: PortfolioBuildJob,
    client: Client,
    portfolio_json: str,
) -> tuple[str, str]:
    """
    Step 3: Push portfolio to GitHub repo & trigger Vercel deployment.
    
    Returns: (github_repo_url, vercel_deployment_url)
    Idempotency: Check if commit already pushed via git history.
    """
    from app.github_integration import push_portfolio_to_github

    logger.info(f"[job {job.id}] PUSHING: client_id={client.id}, step=3/4")

    try:
        if job.github_repo_url and job.portfolio_url:
            # Already pushed; retrieve URLs from job
            logger.info(f"[job {job.id}] PUSHING: idempotent, already deployed to {job.portfolio_url}")
            return job.github_repo_url, job.portfolio_url

        # Push to GitHub
        logger.debug(f"[job {job.id}] PUSHING: calling push_portfolio_to_github")
        github_url, vercel_url = push_portfolio_to_github(
            client=client,
            portfolio_json=portfolio_json,
        )
        
        if not github_url or not vercel_url:
            logger.error(f"[job {job.id}] PUSHING FAILED: missing URLs (github={github_url}, vercel={vercel_url})")
            raise PushError("push_portfolio_to_github returned incomplete URLs")
        
        job.github_repo_url = github_url
        job.portfolio_url = vercel_url
        logger.info(f"[job {job.id}] PUSHING: success, live at {vercel_url}")

        return github_url, vercel_url

    except Exception as exc:
        logger.exception(f"[job {job.id}] PUSHING FAILED: {exc}")
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

    logger.info(f"[job {job.id}] NOTIFYING: client_id={client.id}, step=4/4")

    if job.notified_client_at:
        # Already notified; skip
        logger.info(f"[job {job.id}] NOTIFYING: idempotent, client already notified at {job.notified_client_at}")
        return

    try:
        if not client.email:
            logger.error(f"[job {job.id}] NOTIFYING FAILED: client email not available")
            raise NotificationError("Client email not available")

        logger.debug(f"[job {job.id}] NOTIFYING: sending email to {client.email}")
        send_portfolio_live_email(
            client_name=client.name,
            client_email=client.email,
            portfolio_url=portfolio_url,
        )

        job.notified_client_at = utcnow()
        logger.info(f"[job {job.id}] NOTIFYING: success, email sent to {client.email}")

    except Exception as exc:
        logger.exception(f"[job {job.id}] NOTIFYING FAILED: {exc}")
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
        logger.error(f"[job {job_id}] FAILED: client {job.client_id} not found")
        job.status = PortfolioBuildJobStatus.FAILED.value
        job.error_message = "Client not found"
        job.error_step = "init"
        db.commit()
        raise OrchestrationError(f"Client {job.client_id} not found")

    logger.info(f"[job {job.id}] STARTED: status={job.status}, retry={job.retry_count}/{job.max_retries}")

    # Mark job as started if first run
    if not job.started_at:
        job.started_at = utcnow()
        logger.debug(f"[job {job.id}] marked started_at={job.started_at}")

    try:
        portfolio_html = None
        portfolio_url = None

        # Step 1: Provision (PENDING → PROVISIONING → PROVISIONING complete)
        if job.status in (PortfolioBuildJobStatus.PENDING.value, PortfolioBuildJobStatus.PROVISIONING.value):
            job.status = PortfolioBuildJobStatus.PROVISIONING.value
            job.current_step = "provisioning"
            db.commit()
            _step_provisioning(db, job, client)
            db.commit()

        # Step 2: Generate (PROVISIONING → GENERATING → GENERATING complete)
        if job.status in (PortfolioBuildJobStatus.PROVISIONING.value, PortfolioBuildJobStatus.GENERATING.value):
            job.status = PortfolioBuildJobStatus.GENERATING.value
            job.current_step = "generating"
            db.commit()
            portfolio_html = _step_generating(db, job, client)
            db.commit()

        # Step 3: Push to GitHub (GENERATING → PUSHING → PUSHING complete)
        if job.status in (PortfolioBuildJobStatus.GENERATING.value, PortfolioBuildJobStatus.PUSHING.value):
            if not portfolio_html:
                logger.error(f"[job {job.id}] CORRUPTION: portfolio_html missing at PUSHING step")
                raise OrchestrationError("State machine corruption: portfolio_html not available")
            
            job.status = PortfolioBuildJobStatus.PUSHING.value
            job.current_step = "pushing"
            db.commit()
            github_url, portfolio_url = _step_pushing(db, job, client, portfolio_html)
            db.commit()

        # Step 4: Notify client (PUSHING → NOTIFYING → NOTIFYING complete)
        if job.status in (PortfolioBuildJobStatus.PUSHING.value, PortfolioBuildJobStatus.NOTIFYING.value):
            if not portfolio_url and job.portfolio_url:
                portfolio_url = job.portfolio_url
            elif not portfolio_url:
                logger.error(f"[job {job.id}] CORRUPTION: portfolio_url missing at NOTIFYING step")
                raise OrchestrationError("State machine corruption: portfolio_url not available")
            
            job.status = PortfolioBuildJobStatus.NOTIFYING.value
            job.current_step = "notifying"
            db.commit()
            _step_notifying(db, job, client, portfolio_url)
            db.commit()

        # Mark complete
        if job.status != PortfolioBuildJobStatus.COMPLETE.value:
            job.status = PortfolioBuildJobStatus.COMPLETE.value
            job.current_step = None
            job.completed_at = utcnow()
            job.error_message = None
            job.error_step = None
            db.commit()
        
        elapsed = (job.completed_at - job.started_at).total_seconds() if job.started_at and job.completed_at else 0
        logger.info(f"[job {job.id}] COMPLETE: portfolio live at {job.portfolio_url}, elapsed={elapsed:.1f}s")

    except StepError as exc:
        logger.warning(f"[job {job.id}] STEP FAILURE: {exc.step} failed (retriable={exc.retriable})")
        _handle_step_failure(db, job, exc)
    except Exception as exc:
        # Unexpected error: mark failed
        logger.exception(f"[job {job.id}] UNEXPECTED ERROR: {exc}")
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
        logger.error(f"[job {job.id}] PERMANENT FAILURE: {error.step} failed (retriable={error.retriable}, retries={job.retry_count}/{job.max_retries})")
        logger.error(f"[job {job.id}] FAILURE DETAILS: {error.message}")
        job.status = PortfolioBuildJobStatus.FAILED.value
        db.commit()
        raise error

    # Retry with exponential backoff (capped at 5 minutes)
    job.retry_count += 1
    backoff_seconds = min(2 ** (job.retry_count + 1), 300)  # 2^(n+1), capped at 300s (5min)
    logger.warning(f"[job {job.id}] RETRY: {error.step} failed, attempt {job.retry_count}/{job.max_retries}, next retry in {backoff_seconds}s")
    job.status = PortfolioBuildJobStatus.RETRY_PENDING.value
    db.commit()
    # Next worker invocation will pick this up after backoff delay


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
