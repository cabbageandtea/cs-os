"""Template context helpers for intake forms."""

from __future__ import annotations

from app.client_prerequisites import prerequisites_for_package, prerequisites_setup_minutes
from app.intake_validation import package_requires_career_goals, package_requires_linkedin
from app.package_config import PACKAGES, get_package


def intake_form_context(
    *,
    package_slug: str = "foundation",
    show_package_select: bool = False,
    email_readonly: bool = False,
    prefill: dict | None = None,
) -> dict:
    package = get_package(package_slug)
    prefill = prefill or {}
    return {
        "packages": list(PACKAGES.values()),
        "package_slug": package.slug,
        "package_name": package.display_name,
        "show_package_select": show_package_select,
        "email_readonly": email_readonly,
        "linkedin_required": package_requires_linkedin(package.slug),
        "career_goals_required": package_requires_career_goals(package.slug),
        "prerequisites": prerequisites_for_package(package.slug),
        "prerequisites_setup_minutes": prerequisites_setup_minutes(package.slug),
        "prefill_name": prefill.get("name", ""),
        "prefill_email": prefill.get("email", ""),
        "prefill_target_role": prefill.get("target_role", ""),
        "prefill_education": prefill.get("experience_education", ""),
        "prefill_projects": prefill.get("experience_projects", ""),
        "prefill_work": prefill.get("experience_work", ""),
        "prefill_skills": prefill.get("skills", ""),
        "prefill_career_goals": prefill.get("career_goals", ""),
        "prefill_github": prefill.get("github_url", ""),
        "prefill_linkedin": prefill.get("linkedin_url", ""),
        "prefill_portfolio_template": prefill.get("portfolio_template", ""),
        "prefill_resume_url": prefill.get("resume_url", ""),
        "prefill_portfolio_url": prefill.get("existing_portfolio_url", ""),
        "prefill_certifications": prefill.get("certifications", ""),
        "prefill_job_timeline": prefill.get("job_timeline", ""),
        "prefill_notes": prefill.get("additional_notes", ""),
    }
