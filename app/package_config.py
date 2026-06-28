"""Package definitions and Stripe price resolution. Prices come from env, not code."""

from __future__ import annotations

import os
from dataclasses import dataclass


class PackageConfigError(ValueError):
    pass


@dataclass(frozen=True)
class PackageDefinition:
    slug: str
    display_name: str
    legacy_tier: str
    tagline: str
    default_price_cents: int
    stripe_price_env: str
    deliverables: tuple[str, ...]


PACKAGES: dict[str, PackageDefinition] = {
    "foundation": PackageDefinition(
        slug="foundation",
        display_name="Foundation",
        legacy_tier="Basic",
        tagline="Live portfolio deployed to your GitHub.",
        default_price_cents=9900,
        stripe_price_env="STRIPE_PRICE_FOUNDATION",
        deliverables=("Portfolio website", "Deployment URL"),
    ),
    "launch": PackageDefinition(
        slug="launch",
        display_name="Launch",
        legacy_tier="Standard",
        tagline="Portfolio, resume, and LinkedIn aligned.",
        default_price_cents=19900,
        stripe_price_env="STRIPE_PRICE_LAUNCH",
        deliverables=(
            "Portfolio website",
            "Resume (PDF)",
            "LinkedIn optimization notes",
            "Deployment URL",
        ),
    ),
    "accelerator": PackageDefinition(
        slug="accelerator",
        display_name="Accelerator",
        legacy_tier="Premium",
        tagline="Custom domain guidance, strategy, and career narrative.",
        default_price_cents=34900,
        stripe_price_env="STRIPE_PRICE_ACCELERATOR",
        deliverables=(
            "Portfolio website",
            "Resume (PDF)",
            "LinkedIn optimization notes",
            "Deployment URL",
            "Career narrative summary",
            "Strategy session",
        ),
    ),
}

ALLOWED_PACKAGE_SLUGS = frozenset(PACKAGES.keys())


def get_package(slug: str) -> PackageDefinition:
    normalized = slug.strip().lower()
    if normalized not in PACKAGES:
        raise PackageConfigError(
            f"Invalid package slug: {slug!r}. Allowed: {', '.join(sorted(ALLOWED_PACKAGE_SLUGS))}."
        )
    return PACKAGES[normalized]


def resolve_stripe_price_id(slug: str) -> str:
    package = get_package(slug)
    price_id = os.environ.get(package.stripe_price_env, "").strip()
    if not price_id:
        raise PackageConfigError(
            f"Missing environment variable {package.stripe_price_env} for package {slug}."
        )
    return price_id


def resolve_price_cents(slug: str) -> int:
    package = get_package(slug)
    env_key = f"PRICE_{package.slug.upper()}_CENTS"
    raw = os.environ.get(env_key, "").strip()
    if raw:
        try:
            return int(raw)
        except ValueError as exc:
            raise PackageConfigError(f"Invalid {env_key} value: {raw!r}.") from exc
    return package.default_price_cents
