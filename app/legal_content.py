"""Public legal copy — single source for /terms and /privacy."""

from __future__ import annotations

import os
from datetime import date

from app.site_branding import site_base_url, site_domain, site_name


TERMS_VERSION = "2026-06-28"
PRIVACY_VERSION = "2026-06-28"


def legal_entity_name() -> str:
    return (os.getenv("LEGAL_ENTITY_NAME") or "DoggyBagg LLC").strip() or "DoggyBagg LLC"


def legal_jurisdiction() -> str:
    custom = (os.getenv("LEGAL_JURISDICTION") or "").strip()
    if custom:
        return custom
    return "the state in which the Company is organized, United States"


def support_email() -> str:
    return os.environ.get("SUPPORT_EMAIL", f"support@{site_domain()}").strip()


def terms_url() -> str:
    return f"{site_base_url()}/terms"


def privacy_url() -> str:
    return f"{site_base_url()}/privacy"


def template_legal_globals() -> dict[str, str]:
    return {
        "legal_entity": legal_entity_name(),
        "legal_jurisdiction": legal_jurisdiction(),
        "legal_support_email": support_email(),
        "terms_version": TERMS_VERSION,
        "privacy_version": PRIVACY_VERSION,
        "terms_url": terms_url(),
        "privacy_url": privacy_url(),
        "legal_last_updated": date.fromisoformat(TERMS_VERSION).strftime("%B %d, %Y"),
    }


def inject_legal_template_globals(jinja_env) -> None:
    jinja_env.globals.update(template_legal_globals())
