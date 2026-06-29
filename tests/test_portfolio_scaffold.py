"""Portfolio scaffold path resolution."""

from __future__ import annotations

from app.portfolio_scaffold import portfolio_scaffold_dir, portfolio_scaffold_repo_path


def test_minimal_scaffold_exists() -> None:
    assert portfolio_scaffold_dir("minimal") is not None
    assert portfolio_scaffold_repo_path("minimal") == "templates/portfolio/minimal/"


def test_data_tech_scaffold_exists() -> None:
    assert portfolio_scaffold_dir("data-tech") is not None


def test_professional_scaffold_exists() -> None:
    assert portfolio_scaffold_dir("professional") is not None
    assert portfolio_scaffold_repo_path("professional") == "templates/portfolio/professional/"


def test_unknown_scaffold_returns_none() -> None:
    assert portfolio_scaffold_dir("nonexistent") is None
    assert portfolio_scaffold_repo_path("nonexistent") is None
