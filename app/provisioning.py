"""Provision paid clients from successful Stripe purchases."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.intake_tokens import assign_intake_token
from app.lifecycle import record_lifecycle_event, transition_customer_lifecycle
from app.models import (
    CustomerLifecycle,
    IntakeStatus,
    PipelineStatus,
    Project,
    Purchase,
    PurchaseStatus,
    Client,
    new_public_id,
    utcnow,
)
from app.package_config import get_package
from app.metrics_service import record_purchased
from app.intake_notify import maybe_send_intake_reminder_email
from app.services import log_change, seed_project_defaults


def _placeholder_name(email: str | None) -> str:
    if email and "@" in email:
        return email.split("@", 1)[0].replace(".", " ").title() or "Pending Intake"
    return "Pending Intake"


def provision_client_from_purchase(
    db: Session,
    purchase: Purchase,
    *,
    customer_email: str | None,
    stripe_customer_id: str | None,
    stripe_payment_intent_id: str | None,
) -> tuple[Client, str]:
    """Create client + project from paid purchase. Returns client and plaintext intake token."""
    if purchase.client_id:
        client = db.get(Client, purchase.client_id)
        if client:
            token = ""
            if (
                client.intake_status == IntakeStatus.PENDING.value
                and not purchase.intake_link_delivered
                and (client.email or purchase.customer_email)
            ):
                token = assign_intake_token(client)
                maybe_send_intake_reminder_email(db, purchase, client, token)
            return client, token

    package = get_package(purchase.package_slug)
    email = (customer_email or purchase.customer_email or "").strip().lower() or None
    now = utcnow()

    purchase.status = PurchaseStatus.PAID.value
    purchase.paid_at = now
    purchase.customer_email = email
    purchase.stripe_customer_id = stripe_customer_id
    purchase.stripe_payment_intent_id = stripe_payment_intent_id

    client = Client(
        name=_placeholder_name(email),
        target_role="Pending intake",
        experience_summary="Pending intake",
        skills="Pending intake",
        package_tier=package.display_name,
        package_slug=package.slug,
        email=email,
        public_id=new_public_id(),
        customer_lifecycle=CustomerLifecycle.INTAKE_PENDING.value,
        intake_status=IntakeStatus.PENDING.value,
        paid_at=now,
        purchase_id=purchase.id,
    )
    db.add(client)
    db.flush()

    purchase.client_id = client.id

    project = Project(client_id=client.id, status=PipelineStatus.INTAKE)
    db.add(project)
    db.flush()

    log_change(
        db,
        entity_type="project",
        entity_id=project.id,
        previous_state=None,
        new_state=PipelineStatus.INTAKE.value,
    )
    seed_project_defaults(db, project, package_slug=package.slug)

    intake_token = assign_intake_token(client)
    record_lifecycle_event(
        db,
        client_id=client.id,
        previous_state=CustomerLifecycle.PURCHASED.value,
        new_state=CustomerLifecycle.INTAKE_PENDING.value,
    )
    log_change(
        db,
        entity_type="purchase",
        entity_id=purchase.id,
        previous_state=PurchaseStatus.PAYMENT_PENDING.value,
        new_state=PurchaseStatus.PAID.value,
    )
    record_purchased(db, client, purchase)

    db.flush()
    maybe_send_intake_reminder_email(db, purchase, client, intake_token)
    return client, intake_token


def find_purchase_by_session_id(db: Session, session_id: str) -> Purchase | None:
    from sqlalchemy import select

    return db.scalar(select(Purchase).where(Purchase.stripe_session_id == session_id))


def find_purchase_by_payment_intent(db: Session, payment_intent_id: str) -> Purchase | None:
    from sqlalchemy import select

    return db.scalar(
        select(Purchase).where(Purchase.stripe_payment_intent_id == payment_intent_id)
    )


def archive_client_after_refund(db: Session, purchase: Purchase) -> None:
    purchase.status = PurchaseStatus.REFUNDED.value
    purchase.refunded_at = utcnow()
    if not purchase.client_id:
        return

    client = db.get(Client, purchase.client_id)
    if not client:
        return

    from app.intake_tokens import invalidate_intake_token

    previous = client.customer_lifecycle
    invalidate_intake_token(client)
    transition_customer_lifecycle(db, client, CustomerLifecycle.ARCHIVED.value)
    log_change(
        db,
        entity_type="purchase",
        entity_id=purchase.id,
        previous_state=PurchaseStatus.PAID.value,
        new_state=PurchaseStatus.REFUNDED.value,
    )
    if previous != CustomerLifecycle.ARCHIVED.value:
        record_lifecycle_event(
            db,
            client_id=client.id,
            previous_state=previous,
            new_state=CustomerLifecycle.ARCHIVED.value,
        )
