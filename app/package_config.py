"""Package definitions and Stripe price resolution. Prices come from env, not code."""

from __future__ import annotations

import os
from dataclasses import dataclass


class PackageConfigError(ValueError):
    pass


# Customer-facing scope rules — keep in sync with /terms §2 and §5.
REVISION_ROUND_DEFINITION = (
    "One revision round = one message with all your feedback on deliverables in your package. "
    "Copy, layout, and matching fixes within that scope count toward your included rounds."
)
SCOPE_CREEP_EXAMPLES: tuple[str, ...] = (
    "Changing target role after build has started",
    "Adding projects or experience not listed in intake",
    "Full redesign or new template after first draft",
    "Ongoing maintenance, job applications, or interview coaching",
)


@dataclass(frozen=True)
class PackageDefinition:
    slug: str
    display_name: str
    legacy_tier: str
    tagline: str
    default_price_cents: int
    stripe_price_env: str
    deliverables: tuple[str, ...]
    revision_rounds: int
    turnaround_display: str
    excludes_display: tuple[str, ...]
    excluded_task_titles: tuple[str, ...] = ()


PACKAGES: dict[str, PackageDefinition] = {
    "foundation": PackageDefinition(
        slug="foundation",
        display_name="Foundation",
        legacy_tier="Basic",
        tagline="Get a portfolio live on your GitHub.",
        default_price_cents=9900,
        stripe_price_env="STRIPE_PRICE_FOUNDATION",
        deliverables=("Portfolio website", "Deployment URL", "GitHub profile guidance"),
        revision_rounds=1,
        turnaround_display="5–10 business days after your brief is in",
        excludes_display=("Resume rewrite", "LinkedIn optimization", "Strategy session"),
        excluded_task_titles=("Resume rewrite",),
    ),
    "launch": PackageDefinition(
        slug="launch",
        display_name="Launch",
        legacy_tier="Standard",
        tagline="Portfolio, resume, and LinkedIn that match.",
        default_price_cents=19900,
        stripe_price_env="STRIPE_PRICE_LAUNCH",
        deliverables=(
            "Portfolio website",
            "Resume (PDF)",
            "LinkedIn optimization notes",
            "Deployment URL",
            "GitHub profile guidance",
        ),
        revision_rounds=2,
        turnaround_display="7–14 business days after your brief is in",
        excludes_display=(
            "Strategy session",
            "Career narrative document",
            "Custom domain setup guide",
        ),
    ),
    "accelerator": PackageDefinition(
        slug="accelerator",
        display_name="Accelerator",
        legacy_tier="Premium",
        tagline="For pivots and competitive roles — strategy call included.",
        default_price_cents=34900,
        stripe_price_env="STRIPE_PRICE_ACCELERATOR",
        deliverables=(
            "Portfolio website",
            "Resume (PDF)",
            "LinkedIn optimization notes",
            "Deployment URL",
            "Career narrative summary",
            "Strategy session (30 min)",
            "Custom domain setup guide",
        ),
        revision_rounds=3,
        turnaround_display="10–21 business days after your brief is in",
        excludes_display=(
            "Ongoing maintenance or retainers",
            "Job applications submitted on your behalf",
            "Custom design from scratch",
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


def package_display_order() -> tuple[str, ...]:
    return ("foundation", "launch", "accelerator")


def tasks_for_package(package_slug: str) -> list[tuple[str, str]]:
    """Pipeline tasks included for a package (title, stage value)."""
    from app.pipeline_config import default_tasks_for_project

    pkg = get_package(package_slug)
    excluded = set(pkg.excluded_task_titles)
    return [
        (title, stage.value)
        for title, stage in default_tasks_for_project()
        if title not in excluded
    ]


def checkout_package_rows(*, featured_slug: str = "launch") -> list[dict[str, object]]:
    """Template-ready package rows for /checkout."""
    rows: list[dict[str, object]] = []
    for slug in package_display_order():
        pkg = PACKAGES[slug]
        rows.append(
            {
                "slug": slug,
                "display_name": pkg.display_name,
                "tagline": pkg.tagline,
                "default_price_cents": pkg.default_price_cents,
                "deliverables": pkg.deliverables,
                "excludes_display": pkg.excludes_display,
                "revision_rounds": pkg.revision_rounds,
                "turnaround_display": pkg.turnaround_display,
                "featured": slug == featured_slug,
            }
        )
    return rows
