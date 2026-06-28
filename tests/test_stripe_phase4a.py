"""Phase 4A Stripe revenue layer tests."""

from __future__ import annotations

from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.intake_tokens import assign_intake_token
from app.models import (
    Client,
    CustomerLifecycle,
    IntakeStatus,
    PipelineStatus,
    Project,
    Purchase,
    PurchaseStatus,
    StripeWebhookEvent,
    utcnow,
)
from app.services import IntakeAccessError, complete_token_intake
from app.stripe_webhook import handle_stripe_event, process_webhook


def _sample_intake_kwargs(**overrides):
    data = {
        "name": "Alex Student",
        "email": "student@example.com",
        "target_role": "Data Analyst",
        "experience_education": "BS Information Systems at Strayer University",
        "experience_projects": "Built a portfolio tracker using Python and FastAPI",
        "experience_work": "Retail associate with inventory reporting duties",
        "skills": "Python, SQL, Excel",
        "linkedin_url": "https://linkedin.com/in/alex",
        "github_url": "https://github.com/alex",
        "career_goals": "Target healthcare analytics roles after graduation.",
        "attestation_checked": True,
        "prerequisites_attestation_checked": True,
    }
    data.update(overrides)
    return data


def _checkout_completed_event(
    *,
    event_id: str = "evt_test_checkout_1",
    session_id: str = "cs_test_session_1",
    purchase_id: int = 1,
    package_slug: str = "launch",
    email: str = "student@example.com",
    payment_intent: str = "pi_test_1",
) -> dict:
    return {
        "id": event_id,
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": session_id,
                "payment_status": "paid",
                "customer": "cus_test_1",
                "customer_email": email,
                "customer_details": {"email": email},
                "payment_intent": payment_intent,
                "metadata": {
                    "package_slug": package_slug,
                    "source": "csos_checkout",
                    "purchase_id": str(purchase_id),
                },
            }
        },
    }


def _make_pending_purchase(db: Session, *, session_id: str = "cs_test_session_1") -> Purchase:
    purchase = Purchase(
        package_slug="launch",
        amount=19900,
        status=PurchaseStatus.PAYMENT_PENDING.value,
        stripe_session_id=session_id,
    )
    db.add(purchase)
    db.commit()
    db.refresh(purchase)
    return purchase


def test_successful_payment_creates_client(db_session: Session) -> None:
    purchase = _make_pending_purchase(db_session)
    event = _checkout_completed_event(purchase_id=purchase.id)

    handle_stripe_event(db_session, event)

    db_session.refresh(purchase)
    assert purchase.status == PurchaseStatus.PAID.value
    assert purchase.client_id is not None

    client = db_session.get(Client, purchase.client_id)
    assert client is not None
    assert client.package_slug == "launch"
    assert client.customer_lifecycle == CustomerLifecycle.INTAKE_PENDING.value
    assert client.intake_status == IntakeStatus.PENDING.value
    project = db_session.scalar(select(Project).where(Project.client_id == client.id))
    assert project is not None
    assert project.status == PipelineStatus.INTAKE

    webhook_count = db_session.scalar(select(func.count()).select_from(StripeWebhookEvent))
    assert webhook_count == 1


def test_duplicate_webhook_creates_only_one_client(db_session: Session) -> None:
    purchase = _make_pending_purchase(db_session)
    event = _checkout_completed_event(purchase_id=purchase.id)

    handle_stripe_event(db_session, event)
    handle_stripe_event(db_session, event)

    clients = db_session.scalars(select(Client)).all()
    assert len(clients) == 1

    webhook_count = db_session.scalar(select(func.count()).select_from(StripeWebhookEvent))
    assert webhook_count == 1


def test_invalid_webhook_rejected(client: TestClient, db_session: Session) -> None:
    response = client.post(
        "/webhooks/stripe",
        content=b'{"id":"evt_bad"}',
        headers={"Stripe-Signature": "bad-signature"},
    )
    assert response.status_code == 400

    webhook_count = db_session.scalar(select(func.count()).select_from(StripeWebhookEvent))
    assert webhook_count == 0


def test_failed_payment_creates_no_client(db_session: Session) -> None:
    purchase = _make_pending_purchase(db_session)
    purchase.stripe_payment_intent_id = "pi_test_failed"
    db_session.commit()

    event = {
        "id": "evt_failed_1",
        "type": "payment_intent.payment_failed",
        "data": {"object": {"id": "pi_test_failed"}},
    }
    handle_stripe_event(db_session, event)

    db_session.refresh(purchase)
    assert purchase.status == PurchaseStatus.FAILED.value
    assert db_session.scalar(select(func.count()).select_from(Client)) == 0


def test_refund_archives_client_and_blocks_intake(db_session: Session) -> None:
    purchase = _make_pending_purchase(db_session)
    handle_stripe_event(db_session, _checkout_completed_event(purchase_id=purchase.id))
    db_session.refresh(purchase)

    client = db_session.get(Client, purchase.client_id)
    assert client is not None
    token = assign_intake_token(client)
    db_session.commit()

    refund_event = {
        "id": "evt_refund_1",
        "type": "charge.refunded",
        "data": {"object": {"payment_intent": "pi_test_1"}},
    }
    handle_stripe_event(db_session, refund_event)

    db_session.refresh(purchase)
    db_session.refresh(client)
    assert purchase.status == PurchaseStatus.REFUNDED.value
    assert client.customer_lifecycle == CustomerLifecycle.ARCHIVED.value
    assert client.intake_token_hash is None

    with pytest.raises(IntakeAccessError):
        complete_token_intake(
            db_session,
            client,
            token=token,
            **_sample_intake_kwargs(linkedin_url=None, github_url=None),
        )


def test_completed_intake_activates_customer_advances_to_analysis(db_session: Session) -> None:
    purchase = _make_pending_purchase(db_session)
    handle_stripe_event(db_session, _checkout_completed_event(purchase_id=purchase.id))
    db_session.refresh(purchase)

    client = db_session.get(Client, purchase.client_id)
    assert client is not None
    token = assign_intake_token(client)
    db_session.commit()

    complete_token_intake(
        db_session,
        client,
        token=token,
        **_sample_intake_kwargs(),
    )

    db_session.refresh(client)
    project = db_session.scalar(select(Project).where(Project.client_id == client.id))
    assert client.customer_lifecycle == CustomerLifecycle.ACTIVE.value
    assert client.intake_status == IntakeStatus.COMPLETE.value
    assert project is not None
    assert project.status == PipelineStatus.ANALYSIS


def test_incomplete_intake_expired_token_rejected(db_session: Session) -> None:
    purchase = _make_pending_purchase(db_session)
    handle_stripe_event(db_session, _checkout_completed_event(purchase_id=purchase.id))
    db_session.refresh(purchase)

    client = db_session.get(Client, purchase.client_id)
    assert client is not None
    token = assign_intake_token(client)
    client.intake_token_expires_at = utcnow() - timedelta(days=1)
    db_session.commit()

    with pytest.raises(IntakeAccessError, match="expired"):
        complete_token_intake(
            db_session,
            client,
            token=token,
            **_sample_intake_kwargs(),
        )
