"""Phase 4B sales layer tests."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Lead, LeadStatus
from tests.conftest import OPS_AUTH


def test_landing_page_returns_200(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Take it with you" in response.text
    assert "Doggybagg" in response.text
    assert "career changers" in response.text.lower()
    assert "Alex Rivera" in response.text
    assert "Jordan Kim" in response.text
    assert "Foundation" in response.text
    assert "Launch" in response.text
    assert "Accelerator" in response.text
    assert "yourname.me" in response.text
    assert "why-me" in response.text


def test_start_hub_lists_edu_prerequisites(client: TestClient) -> None:
    response = client.get("/start")
    assert response.status_code == 200
    assert "Students (.edu)" in response.text
    assert "Why students claim a .me" in response.text
    assert "education.github.com/pack" in response.text
    assert "nc.me/github/auth" in response.text


def test_demo_page_marked_as_example(client: TestClient) -> None:
    response = client.get("/demo")
    assert response.status_code == 200
    assert "Fictional example." in response.text
    assert "Alex Rivera" in response.text


def test_contact_form_stores_lead(client: TestClient, db_session: Session) -> None:
    response = client.post(
        "/contact",
        data={
            "name": "Jordan Lee",
            "email": "jordan@example.com",
            "target_role": "Software Engineer Intern",
            "current_status": "Strayer student, graduating 2026",
            "interested_package": "launch",
        },
    )
    assert response.status_code == 200
    assert "Thank you, Jordan Lee" in response.text

    lead = db_session.scalar(select(Lead).where(Lead.email == "jordan@example.com"))
    assert lead is not None
    assert lead.lead_status == LeadStatus.NEW_LEAD.value
    assert lead.interested_package == "launch"


def test_contact_validation_rejects_bad_email(client: TestClient, db_session: Session) -> None:
    response = client.post(
        "/contact",
        data={
            "name": "Bad Email",
            "email": "not-an-email",
            "target_role": "Analyst",
            "current_status": "Student",
            "interested_package": "unsure",
        },
    )
    assert response.status_code == 422
    assert db_session.scalar(select(Lead).where(Lead.name == "Bad Email")) is None


def test_dashboard_moved_to_ops_route(client: TestClient) -> None:
    response = client.get("/dashboard", auth=OPS_AUTH)
    assert response.status_code == 200
    assert "Operations Dashboard" in response.text
    assert "Lead pipeline" in response.text


def test_lead_status_update(client: TestClient, db_session: Session) -> None:
    client.post(
        "/contact",
        data={
            "name": "Sam Park",
            "email": "sam@example.com",
            "target_role": "Data Analyst",
            "current_status": "Career changer",
            "interested_package": "foundation",
        },
    )
    lead = db_session.scalar(select(Lead).where(Lead.email == "sam@example.com"))
    assert lead is not None

    response = client.post(
        f"/leads/{lead.id}/status",
        data={"lead_status": LeadStatus.CONTACTED.value},
        follow_redirects=False,
        auth=OPS_AUTH,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/dashboard#leads"

    db_session.refresh(lead)
    assert lead.lead_status == LeadStatus.CONTACTED.value


def test_dashboard_shows_lead_pipeline_counts(client: TestClient) -> None:
    client.post(
        "/contact",
        data={
            "name": "Casey Kim",
            "email": "casey@example.com",
            "target_role": "Business Analyst",
            "current_status": "Student",
            "interested_package": "launch",
        },
    )
    response = client.get("/dashboard", auth=OPS_AUTH)
    assert response.status_code == 200
    assert "casey@example.com" in response.text
    assert "New Lead" in response.text
