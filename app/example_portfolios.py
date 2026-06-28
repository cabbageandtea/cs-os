"""Fictional portfolio examples — hosted mocks, not real .me domains."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PortfolioExample:
    slug: str
    template_name: str
    mock_domain: str
    person_name: str
    target_role: str


PORTFOLIO_EXAMPLES: dict[str, PortfolioExample] = {
    "alex-rivera": PortfolioExample(
        slug="alex-rivera",
        template_name="examples/alex_rivera.html",
        mock_domain="alexrivera.me",
        person_name="Alex Rivera",
        target_role="Data Analyst Intern",
    ),
    "jordan-kim": PortfolioExample(
        slug="jordan-kim",
        template_name="examples/jordan_kim.html",
        mock_domain="jordankim.me",
        person_name="Jordan Kim",
        target_role="Junior Software Engineer",
    ),
}


def get_portfolio_example(slug: str) -> PortfolioExample | None:
    return PORTFOLIO_EXAMPLES.get(slug.strip().lower())
