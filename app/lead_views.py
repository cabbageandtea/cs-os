"""Lead pipeline view-model for operations dashboard."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Lead, LeadStatus


LEAD_STATUS_LABELS = {
    LeadStatus.NEW_LEAD.value: "New Lead",
    LeadStatus.CONTACTED.value: "Contacted",
    LeadStatus.PURCHASED.value: "Purchased",
    LeadStatus.LOST.value: "Lost",
}


@dataclass
class LeadRow:
    lead: Lead
    status_label: str
    package_label: str


def _package_label(slug: str) -> str:
    labels = {
        "foundation": "Foundation",
        "launch": "Launch",
        "accelerator": "Accelerator",
        "unsure": "Not sure yet",
    }
    return labels.get(slug, slug.title())


def build_lead_pipeline_context(db: Session) -> dict:
    leads = list(db.scalars(select(Lead).order_by(Lead.created_at.desc())).all())
    rows = [
        LeadRow(
            lead=lead,
            status_label=LEAD_STATUS_LABELS.get(lead.lead_status, lead.lead_status),
            package_label=_package_label(lead.interested_package),
        )
        for lead in leads
    ]

    status_counts = {s.value: 0 for s in LeadStatus}
    for lead in leads:
        if lead.lead_status in status_counts:
            status_counts[lead.lead_status] += 1

    by_status: dict[str, list[LeadRow]] = {s.value: [] for s in LeadStatus}
    for row in rows:
        by_status.setdefault(row.lead.lead_status, []).append(row)

    return {
        "lead_statuses": LeadStatus,
        "lead_status_list": list(LeadStatus),
        "lead_status_labels": LEAD_STATUS_LABELS,
        "lead_status_counts": status_counts,
        "lead_rows": rows,
        "leads_by_status": by_status,
        "lead_total": len(leads),
        "lead_new_count": status_counts.get(LeadStatus.NEW_LEAD.value, 0),
    }
