"""Production health probe — Render and acceptance verification."""

from __future__ import annotations

import os
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

APP_VERSION = "0.1.0"


def _env_configured(key: str) -> bool:
    return bool(os.environ.get(key, "").strip())


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

    critical_ok = db_ok and checks["ops_auth"] and checks["stripe"]
    status = "ok" if critical_ok else "degraded"
    if not db_ok:
        status = "unhealthy"

    return {
        "status": status,
        "version": APP_VERSION,
        "email_configured": email_ready,
        "checks": checks,
    }
