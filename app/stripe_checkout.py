"""Stripe Checkout session creation."""

from __future__ import annotations

import os

import stripe
from sqlalchemy.orm import Session

from app.models import Purchase, PurchaseStatus, utcnow
from app.metrics_service import record_checkout_started
from app.package_config import PackageConfigError, get_package, resolve_price_cents, resolve_stripe_price_id


class StripeCheckoutError(RuntimeError):
    pass


def _configure_stripe() -> None:
    api_key = os.environ.get("STRIPE_SECRET_KEY", "").strip()
    if not api_key:
        raise StripeCheckoutError("STRIPE_SECRET_KEY is not configured.")
    stripe.api_key = api_key


def base_url() -> str:
    url = os.environ.get("BASE_URL", "http://localhost:8000").strip().rstrip("/")
    if not url:
        raise StripeCheckoutError("BASE_URL is not configured.")
    return url


def create_checkout_session(db: Session, package_slug: str) -> tuple[Purchase, str]:
    """Create Stripe Checkout Session and pending purchase. Returns purchase and redirect URL."""
    _configure_stripe()
    package = get_package(package_slug)
    price_id = resolve_stripe_price_id(package_slug)
    amount = resolve_price_cents(package_slug)
    root = base_url()

    purchase = Purchase(
        package_slug=package.slug,
        amount=amount,
        status=PurchaseStatus.PAYMENT_PENDING.value,
        created_at=utcnow(),
    )
    db.add(purchase)
    db.flush()
    record_checkout_started(db, purchase)

    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=f"{root}/purchase/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{root}/purchase/cancelled",
        metadata={
            "package_slug": package.slug,
            "source": "csos_checkout",
            "purchase_id": str(purchase.id),
        },
    )

    purchase.stripe_session_id = session.id
    db.commit()
    db.refresh(purchase)

    if not session.url:
        raise StripeCheckoutError("Stripe did not return a checkout URL.")
    return purchase, session.url
