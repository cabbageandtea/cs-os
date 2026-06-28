"""Lead capture and sales pipeline operations."""

from __future__ import annotations

import re

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Lead, LeadStatus


class LeadValidationError(ValueError):
    pass


class LeadPersistenceError(RuntimeError):
    pass


_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
_VALID_PACKAGES = frozenset({"foundation", "launch", "accelerator", "unsure", ""})


def _normalize_email(email: str) -> str:
    normalized = email.strip().lower()
    if not _EMAIL_RE.match(normalized):
        raise LeadValidationError("Enter a valid email address.")
    return normalized


def _normalize_text(value: str, label: str, *, min_len: int = 2, max_len: int = 200) -> str:
    text = " ".join(value.split()).strip()
    if len(text) < min_len:
        raise LeadValidationError(f"{label} is required.")
    if len(text) > max_len:
        raise LeadValidationError(f"{label} must be {max_len} characters or fewer.")
    return text


def create_lead(
    db: Session,
    *,
    name: str,
    email: str,
    target_role: str,
    current_status: str,
    interested_package: str,
) -> Lead:
    package = interested_package.strip().lower() or "unsure"
    if package not in _VALID_PACKAGES:
        raise LeadValidationError("Select a valid package option.")

    lead = Lead(
        name=_normalize_text(name, "Name"),
        email=_normalize_email(email),
        target_role=_normalize_text(target_role, "Target role"),
        current_status=_normalize_text(current_status, "Current status"),
        interested_package=package,
        lead_status=LeadStatus.NEW_LEAD.value,
    )
    db.add(lead)
    db.flush()
    from app.metrics_service import record_lead_created

    record_lead_created(db, lead)
    try:
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise LeadPersistenceError("Could not save lead.") from exc
    db.refresh(lead)
    return lead


def update_lead_status(db: Session, lead: Lead, new_status: LeadStatus) -> Lead:
    if lead.lead_status == new_status.value:
        return lead
    lead.lead_status = new_status.value
    try:
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise LeadPersistenceError("Could not update lead.") from exc
    db.refresh(lead)
    return lead
