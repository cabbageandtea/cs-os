"""Operator delivery kits — templates for every package-listed deliverable."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from app.models import Client
from app.package_config import get_package, package_display_order
from app.portfolio_scaffold import portfolio_scaffold_repo_path
from app.template_config import recommend_portfolio_template

_REPO_ROOT = Path(__file__).resolve().parents[1]
_DELIVERY_ROOT = _REPO_ROOT / "templates" / "delivery"
_RESUME_ROOT = _REPO_ROOT / "templates" / "resume"

_PLACEHOLDER_RE = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


@dataclass(frozen=True)
class DeliveryDocSpec:
    key: str
    deliverable_name: str
    title: str
    template_file: str
    description: str


DELIVERY_DOCS: tuple[DeliveryDocSpec, ...] = (
    DeliveryDocSpec(
        key="github_guidance",
        deliverable_name="GitHub profile guidance",
        title="GitHub profile guidance",
        template_file="github-profile-guidance.md",
        description="Pinned repos, bio, and README checklist for the client to apply.",
    ),
    DeliveryDocSpec(
        key="linkedin_notes",
        deliverable_name="LinkedIn optimization notes",
        title="LinkedIn optimization notes",
        template_file="linkedin-optimization-notes.md",
        description="Headline, about, featured links, and experience bullets aligned to target role.",
    ),
    DeliveryDocSpec(
        key="deployment_handoff",
        deliverable_name="Deployment URL",
        title="Deployment handoff",
        template_file="deployment-handoff.md",
        description="Live URL, DNS, and repo settings recorded at handoff.",
    ),
    DeliveryDocSpec(
        key="resume_build",
        deliverable_name="Resume (PDF)",
        title="Resume build guide",
        template_file="resume-build-guide.md",
        description="Impact bullets and layout before exporting PDF.",
    ),
    DeliveryDocSpec(
        key="career_narrative",
        deliverable_name="Career narrative summary",
        title="Career narrative summary",
        template_file="career-narrative-summary.md",
        description="One-page positioning doc for pivots and competitive roles.",
    ),
    DeliveryDocSpec(
        key="strategy_session",
        deliverable_name="Strategy session (30 min)",
        title="Strategy session agenda",
        template_file="strategy-session-agenda.md",
        description="30-minute call prep, questions, and follow-up actions.",
    ),
    DeliveryDocSpec(
        key="custom_domain",
        deliverable_name="Custom domain setup guide",
        title="Custom domain setup guide",
        template_file="custom-domain-setup-guide.md",
        description="DNS steps for .me or custom domain on GitHub Pages or Render.",
    ),
)

_DOCS_BY_KEY: dict[str, DeliveryDocSpec] = {doc.key: doc for doc in DELIVERY_DOCS}
_DOCS_BY_DELIVERABLE: dict[str, DeliveryDocSpec] = {
    doc.deliverable_name: doc for doc in DELIVERY_DOCS
}


def delivery_doc_for_deliverable(name: str) -> DeliveryDocSpec | None:
    return _DOCS_BY_DELIVERABLE.get(name.strip())


def delivery_docs_for_package(package_slug: str) -> tuple[DeliveryDocSpec, ...]:
    pkg = get_package(package_slug)
    included = set(pkg.deliverables)
    return tuple(doc for doc in DELIVERY_DOCS if doc.deliverable_name in included)


def delivery_doc_path(spec: DeliveryDocSpec) -> Path:
    path = _DELIVERY_ROOT / spec.template_file
    if not path.is_file():
        raise FileNotFoundError(f"Missing delivery template: {path}")
    return path


def resume_starter_path() -> Path:
    path = _RESUME_ROOT / "starter.html"
    if not path.is_file():
        raise FileNotFoundError(f"Missing resume starter: {path}")
    return path


def _section_from_summary(summary: str, heading: str) -> str:
    marker = f"## {heading}\n"
    if marker not in summary:
        return ""
    chunk = summary.split(marker, 1)[1]
    if "\n\n## " in chunk:
        chunk = chunk.split("\n\n## ", 1)[0]
    return chunk.strip()


def _deployment_url(client: Client) -> str:
    project = getattr(client, "project", None)
    if project is None or not project.deliverables:
        return ""
    for item in project.deliverables:
        if item.name == "Deployment URL" and item.url:
            return str(item.url).strip()
    return ""


def placeholder_context(client: Client, *, package_slug: str) -> dict[str, str]:
    summary = client.experience_summary or ""
    template_slug = recommend_portfolio_template(
        package_slug=package_slug,
        target_role=client.target_role or "",
        skills=client.skills or "",
    )
    scaffold = portfolio_scaffold_repo_path(template_slug) or "templates/portfolio/minimal/"
    return {
        "CLIENT_NAME": (client.name or "").strip(),
        "TARGET_ROLE": (client.target_role or "").strip(),
        "PACKAGE_NAME": (client.package_tier or client.package_slug or "").strip(),
        "EMAIL": (client.email or "").strip(),
        "LINKEDIN_URL": (client.linkedin_url or "").strip(),
        "GITHUB_URL": (client.github_url or "").strip(),
        "SKILLS": (client.skills or "").strip(),
        "EXPERIENCE_SUMMARY": summary.strip(),
        "EDUCATION_SECTION": _section_from_summary(summary, "Education"),
        "PROJECTS_SECTION": _section_from_summary(summary, "Projects"),
        "WORK_SECTION": _section_from_summary(summary, "Work / Internships"),
        "PORTFOLIO_TEMPLATE_PATH": scaffold,
        "RESUME_STARTER_PATH": "templates/resume/starter.html",
        "DEPLOYMENT_URL": _deployment_url(client),
        "PORTFOLIO_URL": _deployment_url(client),
        "SITE_NAME": "Doggybagg",
    }


def render_delivery_doc(spec: DeliveryDocSpec, client: Client, *, package_slug: str) -> str:
    raw = delivery_doc_path(spec).read_text(encoding="utf-8")
    context = placeholder_context(client, package_slug=package_slug)
    return _PLACEHOLDER_RE.sub(
        lambda match: context.get(match.group(1), match.group(0)),
        raw,
    )


def get_delivery_doc_spec(key: str) -> DeliveryDocSpec | None:
    normalized = key.strip().lower()
    return _DOCS_BY_KEY.get(normalized)


def package_deliverable_checklist(package_slug: str) -> list[dict[str, str]]:
    """Rows for ops UI: deliverable name + linked doc key if any."""
    pkg = get_package(package_slug)
    rows: list[dict[str, str]] = []
    for name in pkg.deliverables:
        doc = delivery_doc_for_deliverable(name)
        rows.append(
            {
                "name": name,
                "doc_key": doc.key if doc else "",
                "has_template": bool(doc),
            }
        )
    return rows


def all_package_slugs() -> tuple[str, ...]:
    return package_display_order()
