"""Business funnel and delivery metrics recording."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import BusinessMetrics, Client, Lead, Purchase, utcnow


def _metrics_for_purchase(db: Session, purchase_id: int) -> BusinessMetrics | None:
    return db.scalar(select(BusinessMetrics).where(BusinessMetrics.purchase_id == purchase_id))


def _metrics_for_client(db: Session, client_id: int) -> BusinessMetrics | None:
    return db.scalar(select(BusinessMetrics).where(BusinessMetrics.client_id == client_id))


def record_lead_created(db: Session, lead: Lead) -> BusinessMetrics:
    package_slug = lead.interested_package if lead.interested_package != "unsure" else None
    metrics = BusinessMetrics(
        lead_id=lead.id,
        lead_created_at=lead.created_at or utcnow(),
        package_slug=package_slug,
    )
    db.add(metrics)
    db.flush()
    return metrics


def record_checkout_started(db: Session, purchase: Purchase) -> BusinessMetrics:
    metrics = BusinessMetrics(
        purchase_id=purchase.id,
        checkout_started_at=purchase.created_at or utcnow(),
        package_slug=purchase.package_slug,
    )
    db.add(metrics)
    db.flush()
    return metrics


def record_purchased(db: Session, client: Client, purchase: Purchase) -> BusinessMetrics:
    metrics = _metrics_for_purchase(db, purchase.id)
    if metrics is None:
        metrics = BusinessMetrics(
            purchase_id=purchase.id,
            checkout_started_at=purchase.created_at,
            package_slug=purchase.package_slug,
        )
        db.add(metrics)
        db.flush()

    metrics.client_id = client.id
    metrics.purchased_at = purchase.paid_at or utcnow()
    metrics.revenue_amount = purchase.amount
    metrics.package_slug = purchase.package_slug
    db.flush()
    return metrics


def record_intake_completed(db: Session, client: Client) -> BusinessMetrics:
    metrics = _metrics_for_client(db, client.id)
    if metrics is None and client.purchase_id:
        metrics = _metrics_for_purchase(db, client.purchase_id)

    if metrics is None:
        metrics = BusinessMetrics(client_id=client.id)
        db.add(metrics)
        db.flush()
    elif metrics.client_id is None:
        metrics.client_id = client.id

    metrics.intake_completed_at = client.intake_completed_at or utcnow()
    if client.package_slug and not metrics.package_slug:
        metrics.package_slug = client.package_slug
    db.flush()
    return metrics


def record_delivered(db: Session, client: Client) -> BusinessMetrics | None:
    metrics = _metrics_for_client(db, client.id)
    if metrics is None:
        return None
    metrics.delivered_at = utcnow()
    db.flush()
    return metrics


def increment_revision_count(db: Session, client_id: int) -> BusinessMetrics | None:
    metrics = _metrics_for_client(db, client_id)
    if metrics is None:
        return None
    metrics.revision_count = (metrics.revision_count or 0) + 1
    db.flush()
    return metrics


def build_metrics_summary(db: Session) -> dict[str, int]:
    rows = list(db.scalars(select(BusinessMetrics)).all())
    return {
        "metrics_total": len(rows),
        "leads_recorded": sum(1 for r in rows if r.lead_created_at),
        "checkouts_started": sum(1 for r in rows if r.checkout_started_at),
        "purchases_recorded": sum(1 for r in rows if r.purchased_at),
        "intakes_completed": sum(1 for r in rows if r.intake_completed_at),
        "deliveries_recorded": sum(1 for r in rows if r.delivered_at),
        "revenue_cents": sum(r.revenue_amount or 0 for r in rows if r.purchased_at),
    }
