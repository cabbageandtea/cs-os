"""Delivery kit templates match package promises."""

from __future__ import annotations

from app.delivery_kits import (
    delivery_docs_for_package,
    delivery_doc_path,
    get_delivery_doc_spec,
    package_deliverable_checklist,
    render_delivery_doc,
)
from app.models import Client
from app.package_config import get_package


def test_foundation_delivery_docs() -> None:
    docs = delivery_docs_for_package("foundation")
    names = {doc.deliverable_name for doc in docs}
    assert "GitHub profile guidance" in names
    assert "Deployment URL" in names
    assert "Resume (PDF)" not in names
    assert len(docs) == 2


def test_launch_adds_resume_and_linkedin_docs() -> None:
    docs = delivery_docs_for_package("launch")
    names = {doc.deliverable_name for doc in docs}
    assert "Resume (PDF)" in names
    assert "LinkedIn optimization notes" in names
    assert "Career narrative summary" not in names


def test_accelerator_includes_all_doc_templates() -> None:
    docs = delivery_docs_for_package("accelerator")
    assert len(docs) == 6
    for doc in docs:
        assert delivery_doc_path(doc).is_file()


def test_every_listed_deliverable_has_doc_or_portfolio_scaffold() -> None:
    portfolio_only = {"Portfolio website"}
    for slug in ("foundation", "launch", "accelerator"):
        pkg = get_package(slug)
        checklist = package_deliverable_checklist(slug)
        assert len(checklist) == len(pkg.deliverables)
        for row in checklist:
            if row["name"] in portfolio_only:
                assert not row["has_template"]
            else:
                assert row["has_template"], f"{slug}: missing doc for {row['name']}"


def test_render_fills_client_placeholders() -> None:
    client = Client(
        name="Jamie Lee",
        target_role="Data Analyst Intern",
        email="jamie@school.edu",
        skills="Python, SQL",
        experience_summary="## Education\nB.S. Stats\n\n## Projects\nDashboard capstone",
    )
    spec = get_delivery_doc_spec("github_guidance")
    assert spec is not None
    body = render_delivery_doc(spec, client, package_slug="launch")
    assert "Jamie Lee" in body
    assert "Data Analyst Intern" in body
    assert "Dashboard capstone" in body
    assert "{{CLIENT_NAME}}" not in body
