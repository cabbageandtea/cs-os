"""Post-payment intake link delivery (email + purchase flags)."""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.email_service import EmailDeliveryError, send_intake_reminder_email
from app.models import Client, Purchase
from app.stripe_checkout import base_url

logger = logging.getLogger(__name__)


def intake_url_for_token(token: str) -> str:
    root = base_url().rstrip("/")
    return f"{root}/intake/{token}"


def maybe_send_intake_reminder_email(
    db: Session,
    purchase: Purchase,
    client: Client,
    intake_token: str,
) -> bool:
    """Email intake link once per purchase. Returns True if email sent."""
    if not intake_token or not (client.email or purchase.customer_email):
        return False
    if purchase.intake_link_delivered:
        return False

    to_email = (client.email or purchase.customer_email or "").strip().lower()
    if not to_email:
        return False

    root = base_url().rstrip("/")
    package_name = client.package_tier or purchase.package_slug or "your package"
    try:
        sent = send_intake_reminder_email(
            to_email=to_email,
            client_name=client.name or "there",
            package_name=package_name,
            intake_url=intake_url_for_token(intake_token),
            start_url=f"{root}/start",
        )
    except EmailDeliveryError:
        logger.warning("intake email failed for purchase %s — will retry on status poll", purchase.id)
        return False

    if sent:
        purchase.intake_link_delivered = True
        db.flush()
    return sent
