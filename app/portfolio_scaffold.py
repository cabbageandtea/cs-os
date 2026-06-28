"""Portfolio starter paths for operator build workflow."""

from __future__ import annotations

from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_PORTFOLIO_ROOT = _REPO_ROOT / "templates" / "portfolio"


def portfolio_scaffold_dir(slug: str | None) -> Path | None:
    if not slug:
        return None
    candidate = _PORTFOLIO_ROOT / slug.strip().lower()
    if (candidate / "index.html").is_file():
        return candidate
    return None


def portfolio_scaffold_repo_path(slug: str | None) -> str | None:
    directory = portfolio_scaffold_dir(slug)
    if directory is None:
        return None
    return f"templates/portfolio/{directory.name}/"
