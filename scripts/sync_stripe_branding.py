"""Upload CS-OS brand assets to Stripe and sync account + checkout branding.

Usage:
  set STRIPE_SECRET_KEY=sk_test_...
  python scripts/sync_stripe_branding.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import stripe

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.stripe_branding import (  # noqa: E402
    BRAND_BACKGROUND_COLOR,
    BRAND_BUTTON_COLOR,
    BRAND_DISPLAY_NAME,
    BRAND_ICON_PATH,
    BRAND_LOGO_PATH,
)

BRAND_NAME = BRAND_DISPLAY_NAME


def _upload_files() -> tuple[str, str]:
    with BRAND_ICON_PATH.open("rb") as icon_file:
        icon = stripe.File.create(file=icon_file, purpose="business_icon")
    with BRAND_LOGO_PATH.open("rb") as logo_file:
        logo = stripe.File.create(file=logo_file, purpose="business_logo")
    return icon.id, logo.id


def _sync_account(icon_id: str, logo_id: str) -> bool:
    try:
        account = stripe.Account.modify(
            business_profile={"name": BRAND_NAME},
            settings={
                "dashboard": {"display_name": BRAND_NAME},
                "branding": {
                    "icon": icon_id,
                    "logo": logo_id,
                    "primary_color": BRAND_BUTTON_COLOR,
                    "secondary_color": BRAND_BACKGROUND_COLOR,
                },
            },
        )
    except stripe.error.InvalidRequestError as exc:
        if "Only live keys can access this method" in str(exc):
            print(
                "Account branding API is live-mode only. "
                "Update test branding in the Stripe Dashboard (links printed below)."
            )
            return False
        raise

    display = account.settings.dashboard.display_name
    print(f"Account display name -> {display}")
    return True


def _print_dashboard_links() -> None:
    print("\nStripe Dashboard (test mode):")
    print("  Business name: https://dashboard.stripe.com/test/settings/business-details")
    print("  Checkout branding: https://dashboard.stripe.com/test/settings/branding/checkout")
    print(f"  Set business name to: {BRAND_NAME}")
    print(f"  Upload icon from: {BRAND_ICON_PATH}")
    print(f"  Upload logo from: {BRAND_LOGO_PATH}")
    print(f"  Button/accent color: {BRAND_BUTTON_COLOR}")


def main() -> int:
    api_key = os.environ.get("STRIPE_SECRET_KEY", "").strip()
    if not api_key.startswith("sk_test_") and not api_key.startswith("sk_live_"):
        print("Set STRIPE_SECRET_KEY to your Stripe secret key.", file=sys.stderr)
        return 1
    if not BRAND_ICON_PATH.is_file():
        print(f"Missing brand icon: {BRAND_ICON_PATH}", file=sys.stderr)
        return 1
    if not BRAND_LOGO_PATH.is_file():
        print(f"Missing brand logo: {BRAND_LOGO_PATH}", file=sys.stderr)
        return 1

    stripe.api_key = api_key
    icon_id, logo_id = _upload_files()
    synced = _sync_account(icon_id, logo_id)
    if not synced:
        _print_dashboard_links()

    print(f"Uploaded icon -> {icon_id}")
    print(f"Uploaded logo -> {logo_id}")
    print("\n# Add to cs-os/.env:")
    print(f"STRIPE_BRAND_ICON_FILE={icon_id}")
    print(f"STRIPE_BRAND_LOGO_FILE={logo_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
