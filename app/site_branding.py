"""Public site name and domain — driven by env (Doggybagg / doggybagg.cc in production)."""

from __future__ import annotations

import os
from urllib.parse import urlparse

DEFAULT_SITE_NAME = "Doggybagg"
DEFAULT_SITE_DOMAIN = "doggybagg.cc"
DEFAULT_SITE_TAGLINE = "Take it with you"


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
        f"{site_name()} — {site_tagline().rstrip('.')}. "
        "Portfolio, resume, and professional presence as one system on accounts you own."
    )


def site_base_url() -> str:
    """Canonical origin for SEO tags (no trailing slash)."""
    base = (os.getenv("BASE_URL") or "").strip().rstrip("/")
    if base:
        return base
    return f"https://{site_domain()}"


def site_og_image_url() -> str:
    """Absolute URL for Open Graph / Twitter preview image."""
    return f"{site_base_url()}/static/logo.png"


def support_email() -> str:
    """Public support / contact mailbox (brand-aligned default: hello@domain)."""
    custom = (os.getenv("SUPPORT_EMAIL") or "").strip()
    if custom and "@" in custom:
        return custom.lower()
    return f"hello@{site_domain()}"


# Public marketing paths included in sitemap.xml (no auth, no PII flows).
PUBLIC_SITEMAP_PATHS: tuple[str, ...] = (
    "/",
    "/demo",
    "/contact",
    "/checkout",
    "/start",
    "/status",
    "/terms",
    "/privacy",
)


def template_globals() -> dict[str, str]:
    return {
        "site_name": site_name(),
        "site_domain": site_domain(),
        "site_tagline": site_tagline(),
        "site_meta_description": site_meta_description(),
        "site_base_url": site_base_url(),
        "site_og_image_url": site_og_image_url(),
        "support_email": support_email(),
    }


def inject_template_globals(jinja_env) -> None:
    jinja_env.globals.update(template_globals())
