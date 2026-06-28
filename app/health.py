"""Production health probe — Render and acceptance verification."""

from __future__ import annotations

import os
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

APP_VERSION = "0.1.0"


def _env_configured(key: str) -> bool:
    return bool(os.environ.get(key, "").strip())


def _stripe_mode() -> str:
    key = os.environ.get("STRIPE_SECRET_KEY", "").strip()
    if key.startswith("sk_live_"):
        return "live"
    if key.startswith("sk_test_"):
        return "test"
    if not key:
        return "missing"
    return "unknown"


def build_health_payload(db: Session) -> dict[str, Any]:
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    checks = {
        "database": db_ok,
        "stripe": _env_configured("STRIPE_SECRET_KEY"),
        "stripe_webhook": _env_configured("STRIPE_WEBHOOK_SECRET"),
        "ops_auth": _env_configured("OPS_PASSWORD"),
        "base_url": _env_configured("BASE_URL"),
        "email_resend": _env_configured("RESEND_API_KEY"),
        "email_smtp": _env_configured("SMTP_HOST"),
    }
    email_ready = checks["email_resend"] or checks["email_smtp"]
    stripe_mode = _stripe_mode()
    collect_money_ready = (
        db_ok
        and checks["stripe"]
        and checks["stripe_webhook"]
        and checks["base_url"]
        and email_ready
        and stripe_mode == "live"
    )

    critical_ok = db_ok and checks["ops_auth"] and checks["stripe"]
    status = "ok" if critical_ok else "degraded"
    if not db_ok:
        status = "unhealthy"

    return {
        "status": status,
        "version": APP_VERSION,
        "email_configured": email_ready,
        "stripe_mode": stripe_mode,
        "collect_money_ready": collect_money_ready,
        "checks": checks,
    }


def build_status_page_context(db: Session) -> dict[str, Any]:
    payload = build_health_payload(db)
    checks = payload["checks"]
    rows = [
        ("Database", checks["database"], "Client and pipeline data"),
        ("Stripe checkout", checks["stripe"], f"Mode: {payload['stripe_mode']}"),
        ("Stripe webhooks", checks["stripe_webhook"], "Post-payment provisioning"),
        ("Operator auth", checks["ops_auth"], "Dashboard and intake"),
        ("Base URL", checks["base_url"], "Email links and redirects"),
        ("Transactional email", payload["email_configured"], "Resend or SMTP"),
    ]
    weights = (15, 10, 5, 10, 5, 5)
    total = sum(weights)
    earned = sum(w for (_, ok, _), w in zip(rows, weights) if ok)
    score = round((earned / total) * 100) if total else 0
    grade = "A" if score >= 95 else "B+" if score >= 85 else "B" if score >= 80 else "C" if score >= 70 else "D"
    return {
        "overall_status": payload["status"],
        "version": payload["version"],
        "score": score,
        "grade": grade,
        "stripe_mode": payload["stripe_mode"],
        "collect_money_ready": payload["collect_money_ready"],
        "check_rows": [
            {"label": label, "ok": ok, "detail": detail}
            for (label, ok, detail) in rows
        ],
    }
