"""Portfolio template recommendation."""

from __future__ import annotations

from app.template_config import recommend_portfolio_template


def test_recommend_honors_client_choice() -> None:
    assert (
        recommend_portfolio_template(
            package_slug="foundation",
            target_role="Analyst",
            skills="Excel",
            client_choice="minimal",
        )
        == "minimal"
    )


def test_recommend_data_tech_for_engineer() -> None:
    assert (
        recommend_portfolio_template(
            package_slug="launch",
            target_role="Software Engineer Intern",
            skills="Python, React",
            client_choice=None,
        )
        == "data-tech"
    )


def test_foundation_blocks_professional_choice() -> None:
    assert (
        recommend_portfolio_template(
            package_slug="foundation",
            target_role="Software Engineer",
            skills="Python",
            client_choice="professional",
        )
        == "data-tech"
    )
