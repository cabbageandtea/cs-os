"""Dashboard view-model assembly."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import (
    Client,
    DeliverableStatus,
    PipelineStatus,
    Project,
    TaskStatus,
)
from app.pipeline_config import BUILD_WIP_WARNING_THRESHOLD, PIPELINE_ORDER


@dataclass
class ClientRow:
    client: Client
    is_demo: bool
    pipeline_index: int
    pipeline_total: int
    status_label: str
    tasks_done: int
    tasks_total: int
    deliv_complete: int
    deliv_total: int
    days_in_stage: int
    days_since_created: int
    needs_attention: bool
    attention_reason: str | None


def _days_since(dt: datetime | None) -> int:
    if dt is None:
        return 0
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return max(0, (datetime.now(timezone.utc) - dt).days)


def _enrich_client(client: Client) -> ClientRow:
    project = client.project
    is_demo = client.name.startswith("[DEMO]")

    if not project:
        return ClientRow(
            client=client,
            is_demo=is_demo,
            pipeline_index=0,
            pipeline_total=len(PIPELINE_ORDER),
            status_label="No project",
            tasks_done=0,
            tasks_total=0,
            deliv_complete=0,
            deliv_total=0,
            days_in_stage=0,
            days_since_created=_days_since(client.created_at),
            needs_attention=True,
            attention_reason="Missing project record",
        )

    status_list = list(PIPELINE_ORDER)
    try:
        pipeline_index = status_list.index(project.status)
    except ValueError:
        pipeline_index = 0

    tasks = project.tasks or []
    deliverables = project.deliverables or []
    tasks_done = sum(1 for t in tasks if t.status == TaskStatus.DONE)
    deliv_complete = sum(1 for d in deliverables if d.status == DeliverableStatus.COMPLETE)
    days_in_stage = _days_since(project.updated_at)
    days_since_created = _days_since(client.created_at)

    attention_reason: str | None = None
    if (
        client.customer_lifecycle == "intake_pending"
        and not is_demo
    ):
        attention_reason = "Paid — intake pending"
    elif project.status == PipelineStatus.INTAKE and days_in_stage >= 3 and not is_demo:
        attention_reason = f"In Intake {days_in_stage}d — follow up"
    elif project.status == PipelineStatus.REVIEW and days_in_stage >= 5 and not is_demo:
        attention_reason = f"Awaiting client review {days_in_stage}d"
    elif project.status == PipelineStatus.BUILD and not is_demo and days_in_stage >= 7:
        attention_reason = f"In Build {days_in_stage}d — check capacity"

    return ClientRow(
        client=client,
        is_demo=is_demo,
        pipeline_index=pipeline_index,
        pipeline_total=len(status_list),
        status_label=project.status.value,
        tasks_done=tasks_done,
        tasks_total=len(tasks),
        deliv_complete=deliv_complete,
        deliv_total=len(deliverables),
        days_in_stage=days_in_stage,
        days_since_created=days_since_created,
        needs_attention=attention_reason is not None,
        attention_reason=attention_reason,
    )


def build_dashboard_context(
    db: Session,
    *,
    status_filter: PipelineStatus | None = None,
    hide_demo: bool = False,
) -> dict:
    stmt = (
        select(Client)
        .options(
            joinedload(Client.project).joinedload(Project.tasks),
            joinedload(Client.project).joinedload(Project.deliverables),
        )
        .order_by(Client.created_at.desc())
    )
    all_clients = list(db.scalars(stmt).unique().all())
    rows = [_enrich_client(c) for c in all_clients]

    status_counts: dict[str, int] = {s.value: 0 for s in PipelineStatus}
    for row in rows:
        if row.client.project and row.client.project.status:
            status_counts[row.client.project.status.value] += 1

    real_rows = [r for r in rows if not r.is_demo]
    demo_rows = [r for r in rows if r.is_demo]

    if status_filter:
        real_rows = [r for r in real_rows if r.client.project and r.client.project.status == status_filter]
        demo_rows = [r for r in demo_rows if r.client.project and r.client.project.status == status_filter]

    if hide_demo:
        demo_rows = []

    attention_rows = [r for r in rows if r.needs_attention and not r.is_demo]
    if status_filter:
        attention_rows = [r for r in attention_rows if r.client.project and r.client.project.status == status_filter]

    active_real = [
        r for r in real_rows
        if r.client.project and r.client.project.status != PipelineStatus.DELIVERED
    ]
    delivered_real = [
        r for r in real_rows
        if r.client.project and r.client.project.status == PipelineStatus.DELIVERED
    ]

    build_count = status_counts.get(PipelineStatus.BUILD.value, 0)
    intake_pending_count = sum(
        1
        for row in rows
        if not row.is_demo and row.client.customer_lifecycle == "intake_pending"
    )

    return {
        "statuses": PipelineStatus,
        "status_list": list(PIPELINE_ORDER),
        "status_counts": status_counts,
        "current_filter": status_filter.value if status_filter else None,
        "hide_demo": hide_demo,
        "total_clients": len(all_clients),
        "real_count": len([r for r in rows if not r.is_demo]),
        "demo_count": len([r for r in rows if r.is_demo]),
        "active_count": len(active_real),
        "delivered_count": len(delivered_real),
        "attention_rows": attention_rows,
        "active_rows": active_real,
        "delivered_rows": delivered_real,
        "demo_rows": demo_rows,
        "build_wip_warning": build_count > BUILD_WIP_WARNING_THRESHOLD,
        "build_count": build_count,
        "build_wip_threshold": BUILD_WIP_WARNING_THRESHOLD,
        "intake_pending_count": intake_pending_count,
    }
