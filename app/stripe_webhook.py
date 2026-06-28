"""Stripe webhook verification and event dispatch."""

from __future__ import annotations

import os
from typing import Any

import stripe
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Purchase, PurchaseStatus, StripeWebhookEvent, utcnow
from app.provisioning import (
    archive_client_after_refund,
    find_purchase_by_payment_intent,
    find_purchase_by_session_id,
    provision_client_from_purchase,
)


class WebhookConfigError(RuntimeError):
    pass


class WebhookSignatureError(ValueError):
    pass


def verify_stripe_event(payload: bytes, signature: str | None) -> dict[str, Any]:
    secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "").strip()
    if not secret:
        raise WebhookConfigError("STRIPE_WEBHOOK_SECRET is not configured.")
    if not signature:
        raise WebhookSignatureError("Missing Stripe-Signature header.")
    try:
        event = stripe.Webhook.construct_event(payload, signature, secret)
    except stripe.error.SignatureVerificationError as exc:
        raise WebhookSignatureError("Invalid webhook signature.") from exc
    return event


def _event_already_processed(db: Session, event_id: str) -> bool:
    existing = db.scalar(
        select(StripeWebhookEvent).where(StripeWebhookEvent.stripe_event_id == event_id)
    )
    return existing is not None


def _record_event(db: Session, event_id: str, event_type: str) -> None:
    db.add(
        StripeWebhookEvent(
            stripe_event_id=event_id,
            event_type=event_type,
            processed_at=utcnow(),
        )
    )


def handle_stripe_event(db: Session, event: dict[str, Any]) -> None:
    event_id = event["id"]
    event_type = event["type"]

    if _event_already_processed(db, event_id):
        return

    data_object = event["data"]["object"]

    if event_type == "checkout.session.completed":
        _handle_checkout_completed(db, data_object)
    elif event_type == "payment_intent.payment_failed":
        _handle_payment_failed(db, data_object)
    elif event_type == "checkout.session.expired":
        _handle_session_expired(db, data_object)
    elif event_type == "charge.refunded":
        _handle_charge_refunded(db, data_object)
    else:
        _record_event(db, event_id, event_type)
        db.commit()
        return

    _record_event(db, event_id, event_type)
    db.commit()


def _handle_checkout_completed(db: Session, session: dict[str, Any]) -> None:
    if session.get("payment_status") != "paid":
        return

    session_id = session.get("id")
    if not session_id:
        return

    purchase = find_purchase_by_session_id(db, session_id)
    if not purchase:
        metadata = session.get("metadata") or {}
        purchase_id = metadata.get("purchase_id")
        if purchase_id:
            purchase = db.get(Purchase, int(purchase_id))

    if not purchase:
        return

    if purchase.status == PurchaseStatus.PAID.value and purchase.client_id:
        return

    metadata = session.get("metadata") or {}
    package_slug = metadata.get("package_slug")
    if package_slug:
        purchase.package_slug = package_slug

    customer_email = session.get("customer_details", {}).get("email") or session.get("customer_email")
    provision_client_from_purchase(
        db,
        purchase,
        customer_email=customer_email,
        stripe_customer_id=session.get("customer"),
        stripe_payment_intent_id=session.get("payment_intent"),
    )


def _handle_payment_failed(db: Session, payment_intent: dict[str, Any]) -> None:
    purchase = find_purchase_by_payment_intent(db, payment_intent.get("id", ""))
    if not purchase:
        return
    if purchase.status == PurchaseStatus.PAID.value:
        return
    purchase.status = PurchaseStatus.FAILED.value
    purchase.failed_at = utcnow()
    purchase.stripe_payment_intent_id = payment_intent.get("id")


def _handle_session_expired(db: Session, session: dict[str, Any]) -> None:
    purchase = find_purchase_by_session_id(db, session.get("id", ""))
    if not purchase:
        return
    if purchase.status == PurchaseStatus.PAID.value:
        return
    purchase.status = PurchaseStatus.FAILED.value
    purchase.failed_at = utcnow()


def _handle_charge_refunded(db: Session, charge: dict[str, Any]) -> None:
    payment_intent_id = charge.get("payment_intent")
    if not payment_intent_id:
        return
    purchase = find_purchase_by_payment_intent(db, payment_intent_id)
    if not purchase:
        return
    if purchase.status == PurchaseStatus.REFUNDED.value:
        return
    archive_client_after_refund(db, purchase)


def process_webhook(db: Session, payload: bytes, signature: str | None) -> None:
    event = verify_stripe_event(payload, signature)
    try:
        handle_stripe_event(db, event)
    except SQLAlchemyError:
        db.rollback()
        raise
