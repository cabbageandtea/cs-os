"""Portfolio template registry — template-first delivery, not full custom."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PortfolioTemplate:
    slug: str
    display_name: str
    best_for: str
    foundation_eligible: bool
    sections: tuple[str, ...]


PORTFOLIO_TEMPLATES: dict[str, PortfolioTemplate] = {
    "minimal": PortfolioTemplate(
        slug="minimal",
        display_name="Minimal",
        best_for="General students and early-career roles with a focused project list.",
        foundation_eligible=True,
        sections=("Hero", "About", "Projects", "Skills", "Contact"),
    ),
    "data-tech": PortfolioTemplate(
        slug="data-tech",
        display_name="Data-Tech",
        best_for="Software, data, and engineering targets — stack and outcomes forward.",
        foundation_eligible=True,
        sections=("Hero", "Projects", "Tech stack", "Experience", "GitHub", "Contact"),
    ),
    "professional": PortfolioTemplate(
        slug="professional",
        display_name="Professional",
        best_for="Business, operations, and consulting-style positioning.",
        foundation_eligible=False,
        sections=("Hero", "Summary", "Experience", "Projects", "Skills", "Contact"),
    ),
}


def get_portfolio_template(slug: str | None) -> PortfolioTemplate | None:
    if not slug:
        return None
    return PORTFOLIO_TEMPLATES.get(slug.strip().lower())


def allowed_templates_for_package(package_slug: str) -> tuple[PortfolioTemplate, ...]:
    slug = package_slug.strip().lower()
    if slug == "foundation":
        return tuple(t for t in PORTFOLIO_TEMPLATES.values() if t.foundation_eligible)
    return tuple(PORTFOLIO_TEMPLATES.values())


def parse_template_preference_from_summary(experience_summary: str) -> str | None:
    marker = "## Portfolio template preference\n"
    if marker not in experience_summary:
        return None
    chunk = experience_summary.split(marker, 1)[1].split("\n\n", 1)[0].strip()
    return chunk.lower() if chunk else None


def recommend_portfolio_template(
    *,
    package_slug: str,
    target_role: str,
    skills: str,
    client_choice: str | None = None,
) -> str:
    """Pick template slug: honor valid client choice, else light heuristic."""
    if client_choice:
        choice = client_choice.strip().lower()
        allowed = {t.slug for t in allowed_templates_for_package(package_slug)}
        if choice in allowed:
            return choice

    role_skills = f"{target_role} {skills}".lower()
    tech_markers = (
        "engineer",
        "developer",
        "software",
        "data",
        "python",
        "javascript",
        "react",
        "sql",
        "devops",
        "cloud",
        "cyber",
    )
    business_markers = ("analyst", "consulting", "operations", "business", "finance", "marketing")

    if any(m in role_skills for m in tech_markers):
        return "data-tech"
    if package_slug.strip().lower() != "foundation" and any(m in role_skills for m in business_markers):
        return "professional"
    return "minimal"
