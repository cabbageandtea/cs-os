#!/usr/bin/env python3
"""Seed a paid purchase via webhook handler — for Playwright revenue-loop tests."""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid

# Ensure repo root on path when invoked from e2e/
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from app.database import SessionLocal
from app.models import Purchase, PurchaseStatus, utcnow
from app.stripe_webhook import handle_stripe_event


def _amount_for_package(slug: str) -> int:
    return {"foundation": 9900, "launch": 19900, "accelerator": 34900}.get(slug, 9900)


def main() -> int:
    parser = argparse.ArgumentParser(description="E2E paid purchase fixture")
    parser.add_argument("--package", default="foundation", choices=("foundation", "launch", "accelerator"))
    parser.add_argument("--email", default="")
    args = parser.parse_args()

    email = args.email.strip() or f"e2e-revenue-{uuid.uuid4().hex[:8]}@example.com"
    session_id = f"cs_e2e_{uuid.uuid4().hex}"
    payment_intent = f"pi_e2e_{uuid.uuid4().hex[:12]}"

    db = SessionLocal()
    try:
        purchase = Purchase(
            package_slug=args.package,
            amount=_amount_for_package(args.package),
            status=PurchaseStatus.PAYMENT_PENDING.value,
            stripe_session_id=session_id,
            created_at=utcnow(),
        )
        db.add(purchase)
        db.commit()
        db.refresh(purchase)
        purchase_id = purchase.id

        event = {
            "id": f"evt_e2e_{uuid.uuid4().hex}",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": session_id,
                    "payment_status": "paid",
                    "customer": "cus_e2e_test",
                    "customer_email": email,
                    "customer_details": {"email": email},
                    "payment_intent": payment_intent,
                    "metadata": {
                        "package_slug": args.package,
                        "source": "csos_checkout",
                        "purchase_id": str(purchase_id),
                    },
                }
            },
        }
        handle_stripe_event(db, event)
        db.commit()
    finally:
        db.close()

    print(
        json.dumps(
            {
                "session_id": session_id,
                "purchase_id": purchase_id,
                "email": email,
                "package": args.package,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
