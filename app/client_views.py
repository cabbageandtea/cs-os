"""Safe view-model assembly for client detail page."""

from __future__ import annotations

from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import (
    Client,
    DeliverableStatus,
    PipelineStatus,
    Project,
    TaskStatus,
    TimestampLog,
)
from app.outcome_service import get_outcome_for_client
from app.delivery_kits import delivery_docs_for_package, package_deliverable_checklist
from app.intake_validation import resolve_client_package_slug
from app.package_config import get_package
from app.portfolio_scaffold import portfolio_scaffold_repo_path
from app.template_config import (
    get_portfolio_template,
    parse_template_preference_from_summary,
    recommend_portfolio_template,
)
from app.pipeline_config import (
    PIPELINE_ORDER,
    STAGE_DEFINITIONS,
    StageDefinition,
    allowed_next_statuses,
    safe_stage_definition,
)

FALLBACK_STAGE = PipelineStatus.INTAKE.value
UNKNOWN_CLIENT_NAME = "Unknown Client"
MISSING_TEXT = "—"


def _purchase_status_label(client: Client) -> str:
    purchase = client.purchase
    if purchase is None:
        return "Manual (no purchase record)"
    status = getattr(purchase, "status", None)
    return _safe_text(status, MISSING_TEXT)


def _safe_status(raw: PipelineStatus | None) -> PipelineStatus:
    if raw is None:
        return PipelineStatus.INTAKE
    if raw in STAGE_DEFINITIONS:
        return raw
    return PipelineStatus.INTAKE


def _safe_text(value: str | None, fallback: str = MISSING_TEXT) -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return text if text else fallback


def _group_tasks_by_stage(tasks: list) -> dict[str, list]:
    grouped: dict[str, list] = {status.value: [] for status in PIPELINE_ORDER}
    unknown: list = []

    for task in tasks or []:
        stage = _safe_text(getattr(task, "stage_name", None), FALLBACK_STAGE)
        if stage in grouped:
            grouped[stage].append(task)
        else:
            unknown.append(task)

    if unknown:
        grouped.setdefault(FALLBACK_STAGE, []).extend(unknown)

    return grouped


def _fetch_logs(db: Session, project: Project | None) -> list[TimestampLog]:
    if project is None:
        return []

    tasks = project.tasks or []
    deliverables = project.deliverables or []
    task_ids = [t.id for t in tasks if t.id is not None]
    deliverable_ids = [d.id for d in deliverables if d.id is not None]

    filters = [
        (TimestampLog.entity_type == "project") & (TimestampLog.entity_id == project.id)
    ]
    if task_ids:
        filters.append(
            (TimestampLog.entity_type == "task") & TimestampLog.entity_id.in_(task_ids)
        )
    if deliverable_ids:
        filters.append(
            (TimestampLog.entity_type == "deliverable")
            & TimestampLog.entity_id.in_(deliverable_ids)
        )

    return list(
        db.scalars(
            select(TimestampLog)
            .where(or_(*filters))
            .order_by(TimestampLog.created_at.desc())
        ).all()
    )


def build_client_detail_context(
    db: Session,
    client: Client | None,
    *,
    error: str | None = None,
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    """Build template context with safe defaults for missing/null data."""
    page_warnings = list(warnings or [])

    if client is None:
        return {
            "client": None,
            "project": None,
            "status_list": list(PIPELINE_ORDER),
            "current_index": 0,
            "allowed_statuses": [PipelineStatus.INTAKE],
            "current_stage": safe_stage_definition(PipelineStatus.INTAKE),
            "tasks_by_stage": {status.value: [] for status in PIPELINE_ORDER},
            "has_tasks": False,
            "task_statuses": TaskStatus,
            "deliverable_statuses": DeliverableStatus,
            "logs": [],
            "error": error or "Client not found.",
            "warnings": page_warnings,
            "display_name": UNKNOWN_CLIENT_NAME,
            "display_role": MISSING_TEXT,
            "display_package": MISSING_TEXT,
            "display_lifecycle": MISSING_TEXT,
            "display_intake_status": MISSING_TEXT,
            "purchase_status": MISSING_TEXT,
            "display_experience": MISSING_TEXT,
            "display_skills": MISSING_TEXT,
            "outcome": None,
        }

    project = client.project
    if project is None:
        page_warnings.append("No project linked to this client.")

    status = _safe_status(project.status if project else None)
    status_list = list(PIPELINE_ORDER)
    try:
        current_index = status_list.index(status)
    except ValueError:
        current_index = 0
        page_warnings.append(f"Unknown pipeline status: {status.value}")

    current_stage: StageDefinition = safe_stage_definition(status)
    allowed = allowed_next_statuses(status) if project else [PipelineStatus.INTAKE]
    tasks = list(project.tasks) if project and project.tasks else []
    deliverables = list(project.deliverables) if project and project.deliverables else []

    if project and not tasks:
        page_warnings.append("No tasks found for this project.")

    tasks_by_stage = _group_tasks_by_stage(tasks)
    has_tasks = any(grouped for grouped in tasks_by_stage.values())

    package_slug = resolve_client_package_slug(client.package_slug, client.package_tier)
    template_pref = parse_template_preference_from_summary(client.experience_summary or "")
    recommended_slug = recommend_portfolio_template(
        package_slug=package_slug,
        target_role=client.target_role or "",
        skills=client.skills or "",
        client_choice=template_pref,
    )
    recommended_template = get_portfolio_template(recommended_slug)
    scaffold_path = portfolio_scaffold_repo_path(recommended_slug)
    package = get_package(package_slug)
    package_revision_rounds = package.revision_rounds
    package_turnaround = package.turnaround_display
    package_deliverables = package.deliverables
    package_excludes = package.excludes_display
    delivery_kit = delivery_docs_for_package(package_slug)
    deliverable_checklist = package_deliverable_checklist(package_slug)
    incomplete_deliverables = [
        d.name
        for d in deliverables
        if d.status != DeliverableStatus.COMPLETE
    ]

    return {
        "client": client,
        "project": project,
        "statuses": PipelineStatus,
        "status_list": status_list,
        "current_index": current_index,
        "allowed_statuses": allowed,
        "current_stage": current_stage,
        "stage_definitions": STAGE_DEFINITIONS,
        "tasks_by_stage": tasks_by_stage,
        "has_tasks": has_tasks,
        "deliverables": deliverables,
        "task_statuses": TaskStatus,
        "deliverable_statuses": DeliverableStatus,
        "logs": _fetch_logs(db, project),
        "error": error,
        "warnings": page_warnings,
        "display_name": _safe_text(client.name, UNKNOWN_CLIENT_NAME),
        "display_role": _safe_text(client.target_role, "Role not specified"),
        "display_package": _safe_text(
            client.package_slug or client.package_tier, "Basic"
        ),
        "display_lifecycle": _safe_text(client.customer_lifecycle, "—"),
        "display_intake_status": _safe_text(client.intake_status, "—"),
        "purchase_status": _purchase_status_label(client),
        "display_experience": _safe_text(
            client.experience_summary, "No intake experience on file."
        ),
        "display_skills": _safe_text(client.skills, "No skills on file."),
        "recommended_template": recommended_template,
        "template_client_preference": template_pref,
        "portfolio_scaffold_path": scaffold_path,
        "outcome": get_outcome_for_client(db, client.id),
        "package_revision_rounds": package_revision_rounds,
        "package_turnaround": package_turnaround,
        "package_deliverables": package_deliverables,
        "package_excludes": package_excludes,
        "delivery_kit": delivery_kit,
        "deliverable_checklist": deliverable_checklist,
        "incomplete_deliverables": incomplete_deliverables,
    }
