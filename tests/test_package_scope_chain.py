"""Front-to-back scope chain — marketing, checkout, terms, ops templates."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.package_config import PACKAGES, package_display_order
from app.package_scope import (
    assert_scope_chain,
    collect_config_layer_issues,
    collect_sales_layer_issues,
    run_scope_audit,
)
from app.services import seed_project_defaults
from app.models import Client, PipelineStatus, Project


def test_config_and_sales_layers_have_no_drift() -> None:
    assert not collect_config_layer_issues()
    assert not collect_sales_layer_issues()


def test_full_scope_chain_on_public_pages(client: TestClient) -> None:
    checkout = client.get("/checkout")
    landing = client.get("/")
    terms = client.get("/terms")
    assert checkout.status_code == 200
    assert landing.status_code == 200
    assert terms.status_code == 200

    assert_scope_chain(
        checkout_html=checkout.text,
        landing_html=landing.text,
        terms_html=terms.text,
    )


def test_seeded_deliverables_match_package_config(db_session) -> None:
    for slug in package_display_order():
        client = Client(
            name=f"Scope {slug}",
            target_role="SWE Intern",
            experience_summary="Test",
            skills="Python",
            package_slug=slug,
            package_tier=PACKAGES[slug].display_name,
        )
        db_session.add(client)
        db_session.flush()
        project = Project(client_id=client.id, status=PipelineStatus.INTAKE)
        db_session.add(project)
        db_session.flush()
        seed_project_defaults(db_session, project, package_slug=slug)
        db_session.flush()

        expected = set(PACKAGES[slug].deliverables)
        actual = {d.name for d in project.deliverables}
        assert actual == expected, slug
