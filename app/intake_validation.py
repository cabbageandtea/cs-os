"""Intake field normalization and validation."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.package_config import ALLOWED_PACKAGE_SLUGS, PACKAGES, get_package


class IntakeValidationError(ValueError):
    pass


PORTFOLIO_TEMPLATES: frozenset[str] = frozenset({"minimal", "data-tech", "professional"})

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class ValidatedIntake:
    name: str
    email: str
    target_role: str
    experience_summary: str
    skills: str
    linkedin_url: str | None
    github_url: str | None


def validate_target_role(value: str) -> str:
    role = " ".join(value.split()).strip()
    if len(role) < 3:
        raise IntakeValidationError("Target role must be at least 3 characters.")
    if len(role) > 200:
        raise IntakeValidationError("Target role must be 200 characters or fewer.")
    return role


def validate_email(value: str) -> str:
    email = value.strip().lower()
    if not email or not _EMAIL_RE.match(email):
        raise IntakeValidationError("A valid email address is required.")
    if len(email) > 320:
        raise IntakeValidationError("Email must be 320 characters or fewer.")
    return email


def normalize_skills(raw: str) -> str:
    """Normalize to deduplicated, comma-separated list."""
    parts = re.split(r"[,;\n]+", raw)
    seen: set[str] = set()
    normalized: list[str] = []
    for part in parts:
        skill = " ".join(part.split()).strip()
        if not skill:
            continue
        key = skill.lower()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(skill)
    if not normalized:
        raise IntakeValidationError("At least one skill is required.")
    return ", ".join(normalized)


def validate_experience_section(label: str, value: str, *, min_length: int = 10) -> str:
    text = value.strip()
    if len(text) < min_length:
        raise IntakeValidationError(
            f"{label} must be at least {min_length} characters. "
            "Provide concrete details, not placeholders."
        )
    return text


def validate_optional_section(label: str, value: str | None, *, min_length: int = 3) -> str | None:
    if not value:
        return None
    text = value.strip()
    if not text:
        return None
    if len(text) < min_length:
        raise IntakeValidationError(f"{label} must be at least {min_length} characters if provided.")
    return text


def validate_career_goals(value: str | None, *, required: bool) -> str | None:
    text = (value or "").strip()
    if not text:
        if required:
            raise IntakeValidationError("Career goals are required for your package.")
        return None
    if len(text) < 10:
        raise IntakeValidationError("Career goals must be at least 10 characters.")
    return text


def validate_portfolio_template(value: str | None) -> str | None:
    if not value:
        return None
    choice = value.strip().lower()
    if choice not in PORTFOLIO_TEMPLATES:
        raise IntakeValidationError(
            "Portfolio template must be one of: minimal, data-tech, professional."
        )
    return choice


def validate_prerequisites_attestation(checked: bool) -> None:
    if not checked:
        raise IntakeValidationError(
            "Confirm you have — or will create within 48 hours — the required accounts listed above."
        )


def validate_attestation(checked: bool) -> None:
    if not checked:
        raise IntakeValidationError(
            "You must confirm that your information is accurate and yours to represent."
        )


def normalize_url(value: str | None) -> str | None:
    if not value:
        return None
    url = value.strip()
    if not url:
        return None
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    return url


def validate_url_field(label: str, value: str | None, *, required: bool) -> str | None:
    url = normalize_url(value)
    if required and not url:
        raise IntakeValidationError(f"{label} is required for your package.")
    if url and len(url) > 500:
        raise IntakeValidationError(f"{label} must be 500 characters or fewer.")
    return url


def package_requires_linkedin(package_slug: str) -> bool:
    return package_slug.strip().lower() in {"launch", "accelerator"}


def package_requires_career_goals(package_slug: str) -> bool:
    return package_slug.strip().lower() in {"launch", "accelerator"}


def resolve_package_slug(raw_slug: str | None, *, fallback: str = "foundation") -> str:
    slug = (raw_slug or fallback).strip().lower()
    if slug not in ALLOWED_PACKAGE_SLUGS:
        raise IntakeValidationError(
            f"Invalid package: {raw_slug!r}. Choose foundation, launch, or accelerator."
        )
    return slug


def resolve_client_package_slug(
    package_slug: str | None,
    package_tier: str | None,
    *,
    fallback: str = "foundation",
) -> str:
    if package_slug:
        normalized = package_slug.strip().lower()
        if normalized in ALLOWED_PACKAGE_SLUGS:
            return normalized
    tier = (package_tier or "").strip()
    for slug, package in PACKAGES.items():
        if tier in {package.display_name, package.legacy_tier, package.slug}:
            return slug
    return fallback


def compose_experience_summary(
    *,
    education: str,
    projects: str,
    work: str,
    career_goals: str | None = None,
    certifications: str | None = None,
    job_timeline: str | None = None,
    portfolio_template: str | None = None,
    resume_url: str | None = None,
    existing_portfolio_url: str | None = None,
    additional_notes: str | None = None,
) -> str:
    """Compose DB `experience_summary` from structured intake form sections."""
    education = validate_experience_section("Education", education)
    projects = validate_experience_section("Projects", projects)
    work = validate_experience_section("Work / internships", work)

    sections: list[str] = [
        f"## Education\n{education}",
        f"## Projects\n{projects}",
        f"## Work / Internships\n{work}",
    ]

    optional_blocks: tuple[tuple[str, str | None], ...] = (
        ("Career goals", career_goals),
        ("Certifications & awards", certifications),
        ("Job search timeline", job_timeline),
        ("Portfolio template preference", portfolio_template),
        ("Resume link", resume_url),
        ("Existing portfolio URL", existing_portfolio_url),
        ("Additional notes", additional_notes),
    )
    for heading, body in optional_blocks:
        if body:
            sections.append(f"## {heading}\n{body}")

    return "\n\n".join(sections)


def validate_name(value: str) -> str:
    name = " ".join(value.split()).strip()
    if len(name) < 2:
        raise IntakeValidationError("Name is required.")
    return name


def validate_intake_submission(
    *,
    package_slug: str,
    name: str,
    email: str,
    target_role: str,
    experience_education: str,
    experience_projects: str,
    experience_work: str,
    skills: str,
    linkedin_url: str | None,
    github_url: str | None,
    career_goals: str | None,
    certifications: str | None,
    job_timeline: str | None,
    portfolio_template: str | None,
    resume_url: str | None,
    existing_portfolio_url: str | None,
    additional_notes: str | None,
    attestation_checked: bool,
    prerequisites_attestation_checked: bool,
) -> ValidatedIntake:
    slug = resolve_package_slug(package_slug)
    validate_prerequisites_attestation(prerequisites_attestation_checked)
    validate_attestation(attestation_checked)

    linkedin_required = package_requires_linkedin(slug)
    goals_required = package_requires_career_goals(slug)

    validated_goals = validate_career_goals(career_goals, required=goals_required)
    template = validate_portfolio_template(portfolio_template)
    certs = validate_optional_section("Certifications", certifications)
    timeline = validate_optional_section("Job search timeline", job_timeline)
    notes = validate_optional_section("Additional notes", additional_notes, min_length=5)

    return ValidatedIntake(
        name=validate_name(name),
        email=validate_email(email),
        target_role=validate_target_role(target_role),
        experience_summary=compose_experience_summary(
            education=experience_education,
            projects=experience_projects,
            work=experience_work,
            career_goals=validated_goals,
            certifications=certs,
            job_timeline=timeline,
            portfolio_template=template,
            resume_url=normalize_url(resume_url),
            existing_portfolio_url=normalize_url(existing_portfolio_url),
            additional_notes=notes,
        ),
        skills=normalize_skills(skills),
        linkedin_url=validate_url_field("LinkedIn URL", linkedin_url, required=linkedin_required),
        github_url=validate_url_field("GitHub URL", github_url, required=True),
    )
