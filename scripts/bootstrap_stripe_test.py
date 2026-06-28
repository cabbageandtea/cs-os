"""Create CS-OS test products/prices in Stripe and print .env lines.

Usage:
  set STRIPE_SECRET_KEY=sk_test_...
  python scripts/bootstrap_stripe_test.py
"""
from __future__ import annotations

import os
import sys

import stripe


PACKAGES = (
    ("foundation", "CS-OS Foundation", 9900, "Portfolio website and deployment."),
    ("launch", "CS-OS Launch", 19900, "Portfolio, resume, and LinkedIn alignment."),
    ("accelerator", "CS-OS Accelerator", 34900, "Full career positioning package."),
)


def main() -> int:
    api_key = os.environ.get("STRIPE_SECRET_KEY", "").strip()
    if not api_key.startswith("sk_test_"):
        print("Set STRIPE_SECRET_KEY to your Stripe TEST secret key (sk_test_...).", file=sys.stderr)
        print("Get it: https://dashboard.stripe.com/test/apikeys", file=sys.stderr)
        return 1

    stripe.api_key = api_key
    env_lines: list[str] = [f"STRIPE_SECRET_KEY={api_key}"]

    for slug, name, cents, description in PACKAGES:
        product = stripe.Product.create(
            name=name,
            description=description,
            metadata={"package_slug": slug, "cs_os": "true"},
        )
        price = stripe.Price.create(
            product=product.id,
            unit_amount=cents,
            currency="usd",
        )
        env_key = f"STRIPE_PRICE_{slug.upper()}"
        env_lines.append(f"{env_key}={price.id}")
        print(f"Created {name}: {price.id}")

    print("\n# Add these to cs-os/.env:")
    for line in env_lines:
        print(line)
    print("\n# Then run webhook listener in another terminal:")
    print("stripe listen --forward-to localhost:8000/webhooks/stripe")
    print("# Copy whsec_... into STRIPE_WEBHOOK_SECRET in .env")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
