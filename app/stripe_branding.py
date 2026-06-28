"""Stripe Checkout branding aligned with CS-OS logo and palette."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import stripe

from app.site_branding import site_name

BRAND_DISPLAY_NAME = site_name()
BRAND_BUTTON_COLOR = "#e86f3a"
BRAND_BACKGROUND_COLOR = "#141416"
_APP_ROOT = Path(__file__).resolve().parent
BRAND_ICON_PATH = _APP_ROOT / "static" / "logo-icon.png"
BRAND_LOGO_PATH = _APP_ROOT / "static" / "logo.png"


class StripeBrandingError(RuntimeError):
    pass


def _configure_stripe() -> None:
    api_key = os.environ.get("STRIPE_SECRET_KEY", "").strip()
    if not api_key:
        raise StripeBrandingError("STRIPE_SECRET_KEY is not configured.")
    stripe.api_key = api_key


def _is_stripe_file_id(value: str) -> bool:
    return value.startswith("file_")


def _resolve_local_path(configured: str, default: Path) -> Path:
    if not configured:
        return default
    candidate = Path(configured)
    if not candidate.is_absolute():
        candidate = Path(__file__).resolve().parents[1] / configured
    return candidate if candidate.is_file() else default


@lru_cache(maxsize=4)
def _upload_brand_file(path_key: str, purpose: str) -> str:
    _configure_stripe()
    path = Path(path_key)
    if not path.is_file():
        raise StripeBrandingError(f"Brand asset not found at {path}")
    size = path.stat().st_size
    if size > 512 * 1024:
        raise StripeBrandingError("Brand asset must be under 512 KB for Stripe Checkout.")
    with path.open("rb") as asset_file:
        uploaded = stripe.File.create(file=asset_file, purpose=purpose)
    file_id = getattr(uploaded, "id", None)
    if not file_id:
        raise StripeBrandingError("Stripe did not return a file id for the brand asset.")
    return file_id


def _resolve_brand_file_id(env_key: str, default_path: Path, purpose: str) -> str:
    configured = os.environ.get(env_key, "").strip()
    if configured and _is_stripe_file_id(configured):
        return configured
    path = _resolve_local_path(configured, default_path)
    return _upload_brand_file(str(path.resolve()), purpose)


def resolve_brand_icon_file_id() -> str:
    return _resolve_brand_file_id("STRIPE_BRAND_ICON_FILE", BRAND_ICON_PATH, "business_icon")


def resolve_brand_logo_file_id() -> str:
    return _resolve_brand_file_id("STRIPE_BRAND_LOGO_FILE", BRAND_LOGO_PATH, "business_logo")


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
