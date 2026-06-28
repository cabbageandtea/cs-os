"""Stripe Checkout branding aligned with CS-OS logo and palette."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import stripe

BRAND_DISPLAY_NAME = "Career Systems"
BRAND_BUTTON_COLOR = "#ff6b4a"
BRAND_BACKGROUND_COLOR = "#f7f5f0"
BRAND_ICON_PATH = Path(__file__).resolve().parent / "static" / "logo-icon.png"


class StripeBrandingError(RuntimeError):
    pass


def _configure_stripe() -> None:
    api_key = os.environ.get("STRIPE_SECRET_KEY", "").strip()
    if not api_key:
        raise StripeBrandingError("STRIPE_SECRET_KEY is not configured.")
    stripe.api_key = api_key
BRAND_BUTTON_COLOR = "#ff6b4a"
BRAND_BACKGROUND_COLOR = "#f7f5f0"
BRAND_ICON_PATH = Path(__file__).resolve().parent / "static" / "logo-icon.png"


@lru_cache(maxsize=2)
def _upload_brand_file(purpose: str) -> str:
    _configure_stripe()
    if not BRAND_ICON_PATH.is_file():
        raise StripeBrandingError(f"Brand icon not found at {BRAND_ICON_PATH}")
    size = BRAND_ICON_PATH.stat().st_size
    if size > 512 * 1024:
        raise StripeBrandingError("Brand icon must be under 512 KB for Stripe Checkout.")
    with BRAND_ICON_PATH.open("rb") as icon_file:
        uploaded = stripe.File.create(file=icon_file, purpose=purpose)
    file_id = getattr(uploaded, "id", None)
    if not file_id:
        raise StripeBrandingError("Stripe did not return a file id for the brand icon.")
    return file_id


def resolve_brand_icon_file_id() -> str:
    configured = os.environ.get("STRIPE_BRAND_ICON_FILE", "").strip()
    if configured:
        return configured
    return _upload_brand_file("business_icon")


def resolve_brand_logo_file_id() -> str:
    configured = os.environ.get("STRIPE_BRAND_LOGO_FILE", "").strip()
    if configured:
        return configured
    return _upload_brand_file("business_logo")


def checkout_branding_settings() -> dict[str, Any]:
    icon_file = resolve_brand_icon_file_id()
    logo_file = resolve_brand_logo_file_id()
    return {
        "display_name": BRAND_DISPLAY_NAME,
        "icon": {"type": "file", "file": icon_file},
        "logo": {"type": "file", "file": logo_file},
        "button_color": BRAND_BUTTON_COLOR,
        "background_color": BRAND_BACKGROUND_COLOR,
        "border_style": "rounded",
        "font_family": "inter",
    }
