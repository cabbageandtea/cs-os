"""Package-scoped task and deliverable seeding."""

from __future__ import annotations

from sqlalchemy import select

from app.models import Client, Deliverable, PipelineStatus, Project, Task
from app.services import seed_project_defaults


def _seed_project(db_session, *, package_slug: str) -> Project:
    client = Client(
        name="Seed Test",
        target_role="SWE Intern",
        experience_summary="Test",
        skills="Python",
        package_slug=package_slug,
        package_tier=package_slug.title(),
    )
    db_session.add(client)
    db_session.flush()
    project = Project(client_id=client.id, status=PipelineStatus.INTAKE)
    db_session.add(project)
    db_session.flush()
    seed_project_defaults(db_session, project, package_slug=package_slug)
    db_session.flush()
    return project


def test_foundation_skips_resume_task(db_session) -> None:
    project = _seed_project(db_session, package_slug="foundation")

    titles = {t.title for t in db_session.scalars(select(Task).where(Task.project_id == project.id))}
    assert "Resume rewrite" not in titles
    assert "Build portfolio site" in titles

    names = {d.name for d in db_session.scalars(select(Deliverable).where(Deliverable.project_id == project.id))}
    assert "Resume (PDF)" not in names
    assert "Portfolio website" in names


def test_launch_includes_resume_task_and_deliverable(db_session) -> None:
    project = _seed_project(db_session, package_slug="launch")

    titles = {t.title for t in db_session.scalars(select(Task).where(Task.project_id == project.id))}
    assert "Resume rewrite" in titles

    names = {d.name for d in db_session.scalars(select(Deliverable).where(Deliverable.project_id == project.id))}
    assert "Resume (PDF)" in names
    assert "GitHub profile guidance" in names


def test_accelerator_includes_strategy_and_narrative(db_session) -> None:
    project = _seed_project(db_session, package_slug="accelerator")

    names = {d.name for d in db_session.scalars(select(Deliverable).where(Deliverable.project_id == project.id))}
    assert "Career narrative summary" in names
    assert "Strategy session (30 min)" in names
    assert "Custom domain setup guide" in names
    assert "Resume (PDF)" in names

    titles = {t.title for t in db_session.scalars(select(Task).where(Task.project_id == project.id))}
    assert "Resume rewrite" in titles
