"""Intake field normalization and validation."""

import re


class IntakeValidationError(ValueError):
    pass


def validate_target_role(value: str) -> str:
    role = " ".join(value.split()).strip()
    if len(role) < 3:
        raise IntakeValidationError("Target role must be at least 3 characters.")
    if len(role) > 200:
        raise IntakeValidationError("Target role must be 200 characters or fewer.")
    return role


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


def compose_experience_summary(
    *,
    education: str,
    projects: str,
    work: str,
) -> str:
    """Compose DB `experience_summary` from structured intake form sections."""
    education = validate_experience_section("Education", education)
    projects = validate_experience_section("Projects", projects)
    work = validate_experience_section("Work / internships", work)

    return (
        f"## Education\n{education}\n\n"
        f"## Projects\n{projects}\n\n"
        f"## Work / Internships\n{work}"
    )


def validate_name(value: str) -> str:
    name = " ".join(value.split()).strip()
    if len(name) < 2:
        raise IntakeValidationError("Name is required.")
    return name


def normalize_url(value: str | None) -> str | None:
    if not value:
        return None
    url = value.strip()
    if not url:
        return None
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    return url
