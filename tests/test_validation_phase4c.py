"""Phase 4C validation layer tests."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.metrics_service import (
    record_checkout_started,
    record_delivered,
    record_intake_completed,
    record_lead_created,
    record_purchased,
)
from app.models import (
    BusinessMetrics,
    Client,
    ClientOutcome,
    Lead,
    LeadStatus,
    Purchase,
    PurchaseStatus,
    utcnow,
)
from app.outcome_service import upsert_client_outcome
from tests.conftest import OPS_AUTH


def test_metrics_creation_full_funnel(db_session: Session) -> None:
    lead = Lead(
        name="Jordan Lee",
        email="jordan@example.com",
        target_role="Analyst Intern",
        current_status="Student",
        interested_package="launch",
        lead_status=LeadStatus.NEW_LEAD.value,
        created_at=utcnow(),
    )
    db_session.add(lead)
    db_session.flush()
    record_lead_created(db_session, lead)

    purchase = Purchase(
        package_slug="launch",
        amount=19900,
        status=PurchaseStatus.PAYMENT_PENDING.value,
        created_at=utcnow(),
    )
    db_session.add(purchase)
    db_session.flush()
    record_checkout_started(db_session, purchase)

    client = Client(
        name="Jordan Lee",
        target_role="Analyst Intern",
        experience_summary="Pending",
        skills="Python",
        package_slug="launch",
        package_tier="Launch",
        purchase_id=purchase.id,
    )
    db_session.add(client)
    db_session.flush()
    purchase.client_id = client.id
    purchase.status = PurchaseStatus.PAID.value
    purchase.paid_at = utcnow()
    record_purchased(db_session, client, purchase)

    client.intake_completed_at = utcnow()
    record_intake_completed(db_session, client)

    record_delivered(db_session, client)

    db_session.commit()

    lead_metrics = db_session.scalar(select(BusinessMetrics).where(BusinessMetrics.lead_id == lead.id))
    purchase_metrics = db_session.scalar(
        select(BusinessMetrics).where(BusinessMetrics.purchase_id == purchase.id)
    )
    assert lead_metrics is not None
    assert lead_metrics.lead_created_at is not None
    assert purchase_metrics is not None
    assert purchase_metrics.checkout_started_at is not None
    assert purchase_metrics.purchased_at is not None
    assert purchase_metrics.intake_completed_at is not None
    assert purchase_metrics.delivered_at is not None
    assert purchase_metrics.package_slug == "launch"
    assert purchase_metrics.revenue_amount == 19900


def test_outcome_creation(db_session: Session) -> None:
    client = Client(
        name="Casey Kim",
        target_role="Data Analyst",
        experience_summary="Summary",
        skills="SQL",
    )
    db_session.add(client)
    db_session.commit()

    outcome = upsert_client_outcome(
        db_session,
        client_id=client.id,
        before_problem="Had class projects but no public portfolio for applications.",
        after_result="Live portfolio, aligned resume, and LinkedIn notes shipped in two weeks.",
        testimonial="I finally had something professional to send recruiters after graduation.",
        display_permission=True,
    )

    stored = db_session.scalar(select(ClientOutcome).where(ClientOutcome.client_id == client.id))
    assert stored is not None
    assert stored.id == outcome.id
    assert stored.display_permission is True


def test_dashboard_requires_authentication(client: TestClient) -> None:
    response = client.get("/dashboard")
    assert response.status_code == 401


def test_dashboard_authenticated(client: TestClient) -> None:
    response = client.get("/dashboard", auth=OPS_AUTH)
    assert response.status_code == 200
    assert "Operations Dashboard" in response.text


def test_clients_route_requires_authentication(client: TestClient, db_session: Session) -> None:
    project_client = Client(
        name="Protected Client",
        target_role="Engineer",
        experience_summary="x",
        skills="y",
    )
    db_session.add(project_client)
    db_session.commit()

    response = client.get(f"/clients/{project_client.id}")
    assert response.status_code == 401

    authed = client.get(f"/clients/{project_client.id}", auth=OPS_AUTH)
    assert authed.status_code == 200
    assert "Protected Client" in authed.text


def test_public_routes_remain_open(client: TestClient) -> None:
    assert client.get("/").status_code == 200
    assert client.get("/demo").status_code == 200
    assert client.get("/contact").status_code == 200
