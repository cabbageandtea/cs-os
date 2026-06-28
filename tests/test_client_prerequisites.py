"""Client prerequisite lists by package."""

from app.client_prerequisites import prerequisites_for_package


def test_foundation_includes_github_not_linkedin() -> None:
    slugs = {p.slug for p in prerequisites_for_package("foundation")}
    assert "github" in slugs
    assert "linkedin" not in slugs
    assert "custom-domain" not in slugs


def test_launch_includes_linkedin() -> None:
    slugs = {p.slug for p in prerequisites_for_package("launch")}
    assert "linkedin" in slugs


def test_accelerator_includes_custom_domain() -> None:
    slugs = {p.slug for p in prerequisites_for_package("accelerator")}
    assert "custom-domain" in slugs
    assert "github-education" in slugs
