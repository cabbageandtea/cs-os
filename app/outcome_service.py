"""Client outcome records for future marketing proof."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import ClientOutcome


class OutcomeValidationError(ValueError):
    pass


class OutcomePersistenceError(RuntimeError):
    pass


def _normalize_text(value: str, label: str, *, min_len: int = 10, max_len: int = 2000) -> str:
    text = value.strip()
    if len(text) < min_len:
        raise OutcomeValidationError(f"{label} must be at least {min_len} characters.")
    if len(text) > max_len:
        raise OutcomeValidationError(f"{label} must be {max_len} characters or fewer.")
    return text


def get_outcome_for_client(db: Session, client_id: int) -> ClientOutcome | None:
    return db.scalar(select(ClientOutcome).where(ClientOutcome.client_id == client_id))


def upsert_client_outcome(
    db: Session,
    *,
    client_id: int,
    before_problem: str,
    after_result: str,
    testimonial: str,
    display_permission: bool,
) -> ClientOutcome:
    outcome = get_outcome_for_client(db, client_id)
    if outcome is None:
        outcome = ClientOutcome(client_id=client_id)
        db.add(outcome)

    outcome.before_problem = _normalize_text(before_problem, "Before problem")
    outcome.after_result = _normalize_text(after_result, "After result")
    outcome.testimonial = _normalize_text(testimonial, "Testimonial", min_len=20)
    outcome.display_permission = display_permission

    try:
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise OutcomePersistenceError("Could not save client outcome.") from exc
    db.refresh(outcome)
    return outcome
