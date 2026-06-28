"""Intake validation rules — package-aware URL and field requirements."""

from __future__ import annotations

import pytest

from app.intake_validation import IntakeValidationError, validate_intake_submission


def _base_kwargs(**overrides):
    data = {
        "package_slug": "launch",
        "name": "Alex Student",
        "email": "alex@example.com",
        "target_role": "Data Analyst",
        "experience_education": "BS Information Systems at Strayer University",
        "experience_projects": "Built a portfolio tracker using Python and FastAPI",
        "experience_work": "Retail associate with inventory reporting duties",
        "skills": "Python, SQL, Excel",
        "linkedin_url": "https://linkedin.com/in/alex",
        "github_url": "https://github.com/alex",
        "career_goals": "Break into data analytics roles in healthcare within 6 months.",
        "certifications": None,
        "job_timeline": None,
        "portfolio_template": None,
        "resume_url": None,
        "existing_portfolio_url": None,
        "additional_notes": None,
        "attestation_checked": True,
        "prerequisites_attestation_checked": True,
    }
    data.update(overrides)
    return data


def test_foundation_requires_github_not_linkedin() -> None:
    result = validate_intake_submission(
        **_base_kwargs(
            package_slug="foundation",
            linkedin_url=None,
            career_goals=None,
        )
    )
    assert result.github_url is not None
    assert result.linkedin_url is None


def test_launch_requires_linkedin_and_goals() -> None:
    with pytest.raises(IntakeValidationError, match="LinkedIn"):
        validate_intake_submission(**_base_kwargs(linkedin_url=None))

    with pytest.raises(IntakeValidationError, match="Career goals"):
        validate_intake_submission(**_base_kwargs(career_goals=None))


def test_prerequisites_attestation_required() -> None:
    with pytest.raises(IntakeValidationError, match="required accounts"):
        validate_intake_submission(**_base_kwargs(prerequisites_attestation_checked=False))


def test_attestation_required() -> None:
    with pytest.raises(IntakeValidationError, match="confirm"):
        validate_intake_submission(**_base_kwargs(attestation_checked=False))


def test_compose_optional_sections() -> None:
    result = validate_intake_submission(
        **_base_kwargs(
            certifications="AWS Cloud Practitioner",
            portfolio_template="data-tech",
            additional_notes="Available evenings only.",
        )
    )
    assert "## Certifications" in result.experience_summary
    assert "data-tech" in result.experience_summary
    assert "evenings" in result.experience_summary
