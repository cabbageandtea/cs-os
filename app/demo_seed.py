"""Fictional demo data for sales demonstrations. Does not touch workflow logic."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import (
    Client,
    Deliverable,
    DeliverableStatus,
    PipelineStatus,
    Project,
    Task,
    TaskStatus,
    TimestampLog,
)
from app.pipeline_config import PIPELINE_ORDER, default_tasks_for_project, log_state_label

DEMO_MARKER = "[DEMO]"
DEMO_LINKEDIN = "https://linkedin.com/in/demo-csos-profile"
DEMO_GITHUB = "https://github.com/demo-csos-portfolio"
DEMO_PORTFOLIO_URL = "https://demo-portfolio.cs-os.example.com"
DEMO_RESUME_URL = "https://demo-portfolio.cs-os.example.com/resume.pdf"


def is_demo_client(client: Client | None) -> bool:
    return bool(client and client.name.startswith(DEMO_MARKER))


def demo_clients_exist(db: Session) -> bool:
    existing = db.scalar(select(Client).where(Client.name.startswith(f"{DEMO_MARKER}%")).limit(1))
    return existing is not None


@dataclass(frozen=True)
class DemoProfile:
    name: str
    target_role: str
    package_tier: str
    skills: str
    experience_summary: str
    status: PipelineStatus
    linkedin_url: str | None = DEMO_LINKEDIN
    github_url: str | None = DEMO_GITHUB


DEMO_PROFILES: tuple[DemoProfile, ...] = (
    DemoProfile(
        name=f"{DEMO_MARKER} Alex Chen",
        target_role="Software Engineer Intern",
        package_tier="Basic",
        skills="Python, JavaScript, Git, REST APIs, SQL",
        experience_summary=(
            "## Education\n"
            "B.S. Computer Science (in progress), Northlake University, expected May 2026. "
            "Relevant coursework: Data Structures, Web Development, Database Systems.\n\n"
            "## Projects\n"
            "Campus Events API — Flask + SQLite app serving 200+ weekly users; cut manual "
            "scheduling time by 40%.\n"
            "Budget Tracker CLI — Python tool with CSV export adopted by student org finance team.\n\n"
            "## Work / Internships\n"
            "IT Help Desk Assistant, Northlake University (2024–present). "
            "Resolved 15–20 tickets/week; documented top 10 fixes for onboarding."
        ),
        status=PipelineStatus.INTAKE,
    ),
    DemoProfile(
        name=f"{DEMO_MARKER} Priya Sharma",
        target_role="Junior Data Analyst",
        package_tier="Standard",
        skills="Python, SQL, Excel, Tableau, Pandas, Statistics",
        experience_summary=(
            "## Education\n"
            "B.S. Statistics & Economics, Westfield State College, May 2025. GPA 3.7.\n\n"
            "## Projects\n"
            "Retail Sales Dashboard — Power BI dashboard from 50k-row dataset; identified "
            "3 underperforming regions for merchandising review.\n"
            "Housing Price Predictor — scikit-learn regression model (R² 0.81) with feature "
            "importance report for capstone.\n\n"
            "## Work / Internships\n"
            "Research Assistant, Economics Dept. (2023–2024). Cleaned survey data and "
            "produced weekly trend summaries for faculty publication."
        ),
        status=PipelineStatus.ANALYSIS,
    ),
    DemoProfile(
        name=f"{DEMO_MARKER} Marcus Webb",
        target_role="Frontend Developer",
        package_tier="Standard",
        skills="React, TypeScript, HTML, CSS, Figma, Jest, Node.js",
        experience_summary=(
            "## Education\n"
            "A.S. Web Development, Coastal Tech Institute, 2024. Continuing B.S. part-time.\n\n"
            "## Projects\n"
            "Freelance client landing pages (5 shipped) with Lighthouse performance scores 90+.\n"
            "Open-source component library — 12 accessible React form components; 180 GitHub stars.\n\n"
            "## Work / Internships\n"
            "Freelance Web Developer (2023–present). Delivered responsive sites for 4 local "
            "businesses; average turnaround 10 days per project."
        ),
        status=PipelineStatus.BUILD,
    ),
    DemoProfile(
        name=f"{DEMO_MARKER} Sofia Rivera",
        target_role="Cybersecurity Analyst",
        package_tier="Premium",
        skills="Linux, Wireshark, SIEM, Python, NIST Framework, Incident Response",
        experience_summary=(
            "## Education\n"
            "B.S. Cybersecurity, Meridian College of Technology, May 2025.\n\n"
            "## Projects\n"
            "Home Lab SIEM — Elastic stack ingesting logs from 5 VMs; built 8 detection rules.\n"
            "Phishing Analysis Toolkit — Python scripts to parse email headers and score risk.\n\n"
            "## Work / Internships\n"
            "Security Operations Intern, Harbor Mutual Insurance (Summer 2024). "
            "Triaged 30+ alerts/week; contributed to runbook for credential-stuffing playbooks."
        ),
        status=PipelineStatus.QA,
    ),
    DemoProfile(
        name=f"{DEMO_MARKER} Jordan Ellis",
        target_role="Product Manager",
        package_tier="Premium",
        skills="Product Strategy, User Research, SQL, Jira, Roadmapping, A/B Testing",
        experience_summary=(
            "## Education\n"
            "B.B.A. Marketing + Certificate in Product Management, Eastbridge University, 2024.\n\n"
            "## Projects\n"
            "Campus Marketplace App — led 4-person team; shipped MVP used by 600+ students in beta.\n"
            "Feature Prioritization Framework — RICE scoring template adopted by campus incubator.\n\n"
            "## Work / Internships\n"
            "Associate Product Intern, Flowstack SaaS (2024). Wrote PRDs for 2 onboarding experiments; "
            "one variant improved activation by 12%."
        ),
        status=PipelineStatus.REVIEW,
    ),
    DemoProfile(
        name=f"{DEMO_MARKER} Taylor Nguyen (Showcase)",
        target_role="Full Stack Developer",
        package_tier="Premium",
        skills="Python, FastAPI, React, PostgreSQL, Docker, AWS, CI/CD, System Design",
        experience_summary=(
            "## Education\n"
            "B.S. Computer Science, Lakeside Institute of Technology, May 2025. "
            "Dean's List (4 semesters).\n\n"
            "## Projects\n"
            "InventorySync — Full-stack SaaS for small retailers; FastAPI + React; "
            "processed 10k+ SKU updates/day in load test.\n"
            "DevMetrics Dashboard — Aggregates GitHub Actions data; reduced team status-meeting "
            "time by 25% in pilot.\n"
            "Capstone: Real-time collaboration whiteboard with WebSockets (sub-100ms latency in demo).\n\n"
            "## Work / Internships\n"
            "Software Engineering Intern, Northwind Digital (Summer 2024). "
            "Built internal admin tools; shipped 3 features to production with 98% test coverage."
        ),
        status=PipelineStatus.DELIVERED,
    ),
)


def _stage_index(status: PipelineStatus) -> int:
    return list(PIPELINE_ORDER).index(status)


def _task_status_for_stage(current: PipelineStatus, task_stage: PipelineStatus) -> TaskStatus:
    cur = _stage_index(current)
    task = _stage_index(task_stage)
    if task < cur:
        return TaskStatus.DONE
    if task == cur:
        return TaskStatus.IN_PROGRESS if current != PipelineStatus.DELIVERED else TaskStatus.DONE
    return TaskStatus.TODO


def _deliverable_status_for_stage(current: PipelineStatus, index: int) -> DeliverableStatus:
    cur = _stage_index(current)
    if current == PipelineStatus.DELIVERED:
        return DeliverableStatus.COMPLETE
    if cur >= _stage_index(PipelineStatus.BUILD) and index == 0:
        return DeliverableStatus.IN_PROGRESS
    if cur >= _stage_index(PipelineStatus.QA):
        return DeliverableStatus.IN_PROGRESS if index < 3 else DeliverableStatus.PENDING
    if cur >= _stage_index(PipelineStatus.REVIEW):
        return DeliverableStatus.IN_PROGRESS
    return DeliverableStatus.PENDING


def _deliverable_url(name: str, status: DeliverableStatus) -> str | None:
    if status != DeliverableStatus.COMPLETE:
        return None
    if "Portfolio" in name:
        return DEMO_PORTFOLIO_URL
    if "Resume" in name:
        return DEMO_RESUME_URL
    if "LinkedIn" in name:
        return DEMO_LINKEDIN
    if "Deployment" in name:
        return DEMO_PORTFOLIO_URL
    return None


def _add_project_history(
    db: Session,
    project_id: int,
    final_status: PipelineStatus,
    *,
    base_time: datetime,
    include_rollbacks: bool = False,
) -> None:
    """Build audit trail through every pipeline stage."""
    if include_rollbacks and final_status == PipelineStatus.DELIVERED:
        transitions: list[tuple[str | None, str]] = [
            (None, PipelineStatus.INTAKE.value),
            (PipelineStatus.INTAKE.value, PipelineStatus.ANALYSIS.value),
            (PipelineStatus.ANALYSIS.value, PipelineStatus.BUILD.value),
            (PipelineStatus.BUILD.value, PipelineStatus.QA.value),
            (
                PipelineStatus.QA.value,
                log_state_label(PipelineStatus.QA, PipelineStatus.BUILD),
            ),
            (PipelineStatus.BUILD.value, PipelineStatus.QA.value),
            (PipelineStatus.QA.value, PipelineStatus.REVIEW.value),
            (PipelineStatus.REVIEW.value, PipelineStatus.DELIVERED.value),
        ]
        for i, (previous, new_state) in enumerate(transitions):
            db.add(
                TimestampLog(
                    entity_type="project",
                    entity_id=project_id,
                    previous_state=previous,
                    new_state=new_state,
                    created_at=base_time + timedelta(days=i * 2),
                )
            )
        return

    stages = list(PIPELINE_ORDER)
    final_idx = _stage_index(final_status)
    t = base_time
    previous: str | None = None

    for idx in range(final_idx + 1):
        new = stages[idx].value
        db.add(
            TimestampLog(
                entity_type="project",
                entity_id=project_id,
                previous_state=previous,
                new_state=new,
                created_at=t,
            )
        )
        previous = new
        t += timedelta(days=2)


def _seed_one_client(db: Session, profile: DemoProfile, *, days_ago: int) -> Client:
    base_time = datetime.now(timezone.utc) - timedelta(days=days_ago)

    client = Client(
        name=profile.name,
        target_role=profile.target_role,
        experience_summary=profile.experience_summary,
        skills=profile.skills,
        linkedin_url=profile.linkedin_url,
        github_url=profile.github_url,
        package_tier=profile.package_tier,
        created_at=base_time,
    )
    db.add(client)
    db.flush()

    project = Project(
        client_id=client.id,
        status=profile.status,
        created_at=base_time,
        updated_at=base_time + timedelta(days=_stage_index(profile.status) * 2),
    )
    db.add(project)
    db.flush()

    for title, stage in default_tasks_for_project():
        task_status = _task_status_for_stage(profile.status, stage)
        task = Task(
            project_id=project.id,
            title=title,
            stage_name=stage.value,
            status=task_status,
            created_at=base_time,
            updated_at=base_time + timedelta(days=1),
        )
        db.add(task)
        db.flush()
        if task_status == TaskStatus.DONE:
            db.add(
                TimestampLog(
                    entity_type="task",
                    entity_id=task.id,
                    previous_state="todo",
                    new_state="done",
                    created_at=base_time + timedelta(days=1),
                )
            )

    deliverable_specs = [
        "Portfolio website",
        "Resume (PDF)",
        "LinkedIn optimization notes",
        "Deployment URL",
    ]
    for idx, name in enumerate(deliverable_specs):
        d_status = _deliverable_status_for_stage(profile.status, idx)
        db.add(
            Deliverable(
                project_id=project.id,
                name=name,
                url=_deliverable_url(name, d_status),
                notes="Fictional demo asset — not a live production URL."
                if d_status == DeliverableStatus.COMPLETE
                else None,
                status=d_status,
                created_at=base_time,
                updated_at=base_time + timedelta(days=2),
            )
        )

    _add_project_history(
        db,
        project.id,
        profile.status,
        base_time=base_time,
        include_rollbacks=profile.status == PipelineStatus.DELIVERED,
    )

    return client


def seed_demo_environment(db: Session, *, force: bool = False) -> list[Client]:
    """Insert fictional demo clients across the full pipeline. Idempotent by default."""
    if demo_clients_exist(db) and not force:
        return list(db.scalars(select(Client).where(Client.name.startswith(f"{DEMO_MARKER}%"))).all())

    if force:
        demo_clients = list(
            db.scalars(
                select(Client)
                .where(Client.name.startswith(f"{DEMO_MARKER}%"))
                .options(joinedload(Client.project).joinedload(Project.tasks))
            ).unique().all()
        )
        for client in demo_clients:
            project = client.project
            if project:
                task_ids = [t.id for t in project.tasks]
                deliverable_ids = [d.id for d in project.deliverables]
                log_query = select(TimestampLog).where(
                    (TimestampLog.entity_type == "project")
                    & (TimestampLog.entity_id == project.id)
                )
                for log in db.scalars(log_query).all():
                    db.delete(log)
                if task_ids:
                    for log in db.scalars(
                        select(TimestampLog).where(
                            TimestampLog.entity_type == "task",
                            TimestampLog.entity_id.in_(task_ids),
                        )
                    ).all():
                        db.delete(log)
                if deliverable_ids:
                    for log in db.scalars(
                        select(TimestampLog).where(
                            TimestampLog.entity_type == "deliverable",
                            TimestampLog.entity_id.in_(deliverable_ids),
                        )
                    ).all():
                        db.delete(log)
                db.delete(project)
            db.delete(client)
        db.commit()

    created: list[Client] = []
    offsets = [2, 5, 8, 11, 14, 21]
    for profile, days_ago in zip(DEMO_PROFILES, offsets, strict=True):
        created.append(_seed_one_client(db, profile, days_ago=days_ago))

    db.commit()
    return created


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Seed CS-OS sales demo environment")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Remove existing demo clients and re-seed",
    )
    args = parser.parse_args()

    from app.database import SessionLocal

    db = SessionLocal()
    try:
        clients = seed_demo_environment(db, force=args.force)
        if not clients and not args.force:
            print("Demo clients already exist. Use --force to re-seed.")
            existing = list(
                db.scalars(select(Client).where(Client.name.startswith(f"{DEMO_MARKER}%"))).all()
            )
            for client in existing:
                print(f"  - {client.name} (id={client.id})")
            return
        print(f"Demo environment ready: {len(clients)} client(s) seeded.")
        for client in clients:
            print(f"  - {client.name} (id={client.id})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
