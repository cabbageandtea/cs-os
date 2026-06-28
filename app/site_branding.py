"""Public site name and domain — driven by env (Doggybag / doggybag.cc in production)."""

from __future__ import annotations

import os
from urllib.parse import urlparse

DEFAULT_SITE_NAME = "Doggybag"
DEFAULT_SITE_DOMAIN = "doggybag.cc"
DEFAULT_SITE_TAGLINE = "Career signal engineering"


def site_name() -> str:
    value = (os.getenv("SITE_NAME") or DEFAULT_SITE_NAME).strip()
    return value or DEFAULT_SITE_NAME


def site_domain() -> str:
    explicit = (os.getenv("SITE_DOMAIN") or "").strip().lstrip(".")
    if explicit:
        return explicit

    base = (os.getenv("BASE_URL") or "").strip().rstrip("/")
    if base:
        host = urlparse(base).netloc
        if host and not host.startswith("127.") and host not in {"localhost", "testserver"}:
            return host

    return DEFAULT_SITE_DOMAIN


def site_tagline() -> str:
    value = (os.getenv("SITE_TAGLINE") or DEFAULT_SITE_TAGLINE).strip()
    return value or DEFAULT_SITE_TAGLINE


def site_meta_description() -> str:
    custom = (os.getenv("SITE_META_DESCRIPTION") or "").strip()
    if custom:
        return custom
    return (
        f"{site_name()} engineers portfolio, resume, and professional presence "
        "as one coordinated system — on accounts you own."
    )


def template_globals() -> dict[str, str]:
    return {
        "site_name": site_name(),
        "site_domain": site_domain(),
        "site_tagline": site_tagline(),
        "site_meta_description": site_meta_description(),
    }


def inject_template_globals(jinja_env) -> None:
    jinja_env.globals.update(template_globals())
