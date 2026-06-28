"""Customer lifecycle audit trail."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import Client, LifecycleEvent


def record_lifecycle_event(
    db: Session,
    *,
    client_id: int,
    previous_state: str | None,
    new_state: str,
) -> None:
    db.add(
        LifecycleEvent(
            client_id=client_id,
            previous_state=previous_state,
            new_state=new_state,
        )
    )


def transition_customer_lifecycle(
    db: Session,
    client: Client,
    new_state: str,
) -> None:
    previous = client.customer_lifecycle
    if previous == new_state:
        return
    client.customer_lifecycle = new_state
    record_lifecycle_event(
        db,
        client_id=client.id,
        previous_state=previous,
        new_state=new_state,
    )
