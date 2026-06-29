"""Front-to-back scope alignment — marketing, checkout, ops, and legal."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.delivery_kits import delivery_doc_for_deliverable, delivery_doc_path
from app.package_config import (
    PACKAGES,
    package_display_order,
    resolve_price_cents,
    tasks_for_package,
)
from app.portfolio_scaffold import portfolio_scaffold_dir
from app.sales_content import (
    CASE_STUDIES,
    COMPARISON_ROWS,
    PACKAGE_SALES,
)
from app.template_config import PORTFOLIO_TEMPLATES

PORTFOLIO_ONLY_DELIVERABLES = frozenset({"Portfolio website"})
_LEGACY_TIER_TO_SLUG = {
    "basic": "foundation",
    "foundation": "foundation",
    "standard": "launch",
    "launch": "launch",
    "premium": "accelerator",
    "accelerator": "accelerator",
}


@dataclass(frozen=True)
class ScopeIssue:
    layer: str
    message: str


def _issues(*items: ScopeIssue) -> list[ScopeIssue]:
    return list(items)


def collect_config_layer_issues() -> list[ScopeIssue]:
    """package_config ↔ delivery kits ↔ portfolio scaffolds ↔ pipeline tasks."""
    issues: list[ScopeIssue] = []

    for slug in package_display_order():
        pkg = PACKAGES[slug]
        for name in pkg.deliverables:
            if name in PORTFOLIO_ONLY_DELIVERABLES:
                if portfolio_scaffold_dir("minimal") is None:
                    issues.append(
                        ScopeIssue("portfolio_scaffold", "missing templates/portfolio/minimal/")
                    )
                continue
            doc = delivery_doc_for_deliverable(name)
            if doc is None:
                issues.append(
                    ScopeIssue(
                        "delivery_kits",
                        f"{slug}: no delivery doc for deliverable {name!r}",
                    )
                )
                continue
            try:
                delivery_doc_path(doc)
            except FileNotFoundError as exc:
                issues.append(ScopeIssue("delivery_kits", str(exc)))

        excluded_tasks = set(pkg.excluded_task_titles)
        task_titles = {title for title, _stage in tasks_for_package(slug)}
        if "Resume (PDF)" in pkg.deliverables and "Resume rewrite" not in task_titles:
            issues.append(
                ScopeIssue(
                    "pipeline_tasks",
                    f"{slug}: package includes resume but Resume rewrite task missing",
                )
            )
        if "Resume (PDF)" not in pkg.deliverables and "Resume rewrite" in task_titles:
            issues.append(
                ScopeIssue(
                    "pipeline_tasks",
                    f"{slug}: Resume rewrite task present but package excludes resume",
                )
            )
        if excluded_tasks & task_titles:
            issues.append(
                ScopeIssue(
                    "pipeline_tasks",
                    f"{slug}: excluded tasks still seeded: {excluded_tasks & task_titles}",
                )
            )

    for template in PORTFOLIO_TEMPLATES.values():
        if portfolio_scaffold_dir(template.slug) is None:
            issues.append(
                ScopeIssue(
                    "portfolio_scaffold",
                    f"missing scaffold for template {template.slug!r}",
                )
            )

    return issues


def collect_sales_layer_issues() -> list[ScopeIssue]:
    """sales_content.PACKAGE_SALES ↔ package_config."""
    issues: list[ScopeIssue] = []

    for slug in package_display_order():
        pkg = PACKAGES[slug]
        sales = PACKAGE_SALES.get(slug)
        if sales is None:
            issues.append(ScopeIssue("sales_content", f"missing PACKAGE_SALES entry for {slug}"))
            continue

        if sales.deliverables != pkg.deliverables:
            issues.append(
                ScopeIssue(
                    "sales_content",
                    f"{slug}: PACKAGE_SALES deliverables drift from package_config",
                )
            )
        if sales.excludes_display != pkg.excludes_display:
            issues.append(
                ScopeIssue(
                    "sales_content",
                    f"{slug}: PACKAGE_SALES excludes drift from package_config",
                )
            )
        if sales.revision_rounds != pkg.revision_rounds:
            issues.append(
                ScopeIssue(
                    "sales_content",
                    f"{slug}: revision_rounds mismatch ({sales.revision_rounds} vs {pkg.revision_rounds})",
                )
            )
        if sales.turnaround != pkg.turnaround_display:
            issues.append(
                ScopeIssue(
                    "sales_content",
                    f"{slug}: turnaround mismatch",
                )
            )
        expected_price = f"${resolve_price_cents(slug) // 100}"
        if sales.price_display != expected_price:
            issues.append(
                ScopeIssue(
                    "sales_content",
                    f"{slug}: price_display {sales.price_display!r} != {expected_price!r}",
                )
            )

    return issues


def collect_case_study_issues() -> list[ScopeIssue]:
    """Public examples must match a real package scope."""
    issues: list[ScopeIssue] = []

    for study in CASE_STUDIES:
        package_label = str(study.get("package", "")).strip()
        slug = _LEGACY_TIER_TO_SLUG.get(package_label.lower())
        if slug is None:
            issues.append(
                ScopeIssue(
                    "case_studies",
                    f"{study.get('name')}: unknown package label {package_label!r}",
                )
            )
            continue

        pkg = PACKAGES[slug]
        deliverable_keys = {d[0].lower() for d in study.get("deliverables", ())}
        if "Portfolio" in deliverable_keys and "Portfolio website" not in pkg.deliverables:
            issues.append(ScopeIssue("case_studies", f"{study.get('name')}: portfolio not in {slug}"))
        if "Resume" in deliverable_keys and "Resume (PDF)" not in pkg.deliverables:
            issues.append(
                ScopeIssue(
                    "case_studies",
                    f"{study.get('name')}: resume shown but {slug} excludes resume",
                )
            )
        if "LinkedIn" in deliverable_keys and "LinkedIn optimization notes" not in pkg.deliverables:
            issues.append(
                ScopeIssue(
                    "case_studies",
                    f"{study.get('name')}: LinkedIn shown but {slug} excludes LinkedIn notes",
                )
            )
        if "Strategy" in deliverable_keys and "Strategy session (30 min)" not in pkg.deliverables:
            issues.append(
                ScopeIssue(
                    "case_studies",
                    f"{study.get('name')}: strategy shown but {slug} excludes strategy session",
                )
            )

    return issues


def collect_comparison_issues() -> list[ScopeIssue]:
    """Compare-table Doggybagg cells must reflect verifiable package facts."""
    issues: list[ScopeIssue] = []
    rounds = tuple(str(PACKAGES[s].revision_rounds) for s in package_display_order())

    for row in COMPARISON_ROWS:
        factor = row.get("factor", "")
        doggybagg = row.get("doggybagg", "")

        if factor == "Revision policy":
            for n in rounds:
                if n not in doggybagg:
                    issues.append(
                        ScopeIssue(
                            "comparison_table",
                            f"revision row missing round count {n!r}",
                        )
                    )
        elif factor == "Scope before you pay":
            required = ("checkout", "revision")
            for token in required:
                if token not in doggybagg.lower():
                    issues.append(
                        ScopeIssue(
                            "comparison_table",
                            f"scope row missing {token!r} in doggybagg cell",
                        )
                    )
        elif factor == "Preview before checkout":
            for name in ("Alex", "Taylor", "Jordan"):
                if name not in doggybagg:
                    issues.append(
                        ScopeIssue(
                            "comparison_table",
                            f"preview row missing showcase name {name!r}",
                        )
                    )

    return issues


def collect_checkout_html_issues(html: str) -> list[ScopeIssue]:
    """Rendered /checkout must list full package scope before payment."""
    issues: list[ScopeIssue] = []
    if not html.strip():
        return _issues(ScopeIssue("checkout_html", "empty checkout HTML"))

    lowered = html.lower()
    for slug in package_display_order():
        pkg = PACKAGES[slug]
        for item in pkg.deliverables:
            if item not in html:
                issues.append(
                    ScopeIssue("checkout_html", f"{slug}: missing deliverable {item!r}")
                )
        for item in pkg.excludes_display:
            if item not in html:
                issues.append(
                    ScopeIssue("checkout_html", f"{slug}: missing exclusion {item!r}")
                )
        if pkg.turnaround_display not in html:
            issues.append(
                ScopeIssue("checkout_html", f"{slug}: missing turnaround {pkg.turnaround_display!r}")
            )

    for slug in package_display_order():
        n = PACKAGES[slug].revision_rounds
        pattern = rf"{n}\s+revision\s+round"
        if not re.search(pattern, lowered):
            issues.append(
                ScopeIssue(
                    "checkout_html",
                    f"{slug}: missing {n} revision round(s) copy",
                )
            )

    if 'href="/terms#revisions"' not in html:
        issues.append(ScopeIssue("checkout_html", "missing link to Terms §5 revisions"))

    return issues


def collect_landing_html_issues(html: str) -> list[ScopeIssue]:
    """Landing package cards must show the same deliverables as package_config."""
    issues: list[ScopeIssue] = []
    if not html.strip():
        return _issues(ScopeIssue("landing_html", "empty landing HTML"))

    for slug in package_display_order():
        sales = PACKAGE_SALES[slug]
        if sales.display_name not in html:
            issues.append(
                ScopeIssue("landing_html", f"missing package heading {sales.display_name!r}")
            )
        for item in sales.deliverables:
            if item not in html:
                issues.append(
                    ScopeIssue("landing_html", f"{slug}: missing deliverable {item!r} on landing")
                )
        for item in sales.excludes_display:
            if item not in html:
                issues.append(
                    ScopeIssue(
                        "landing_html",
                        f"{slug}: missing exclusion {item!r} on landing",
                    )
                )

    if "Foundation is portfolio-only" not in html and "portfolio-only" not in html.lower():
        issues.append(
            ScopeIssue(
                "landing_html",
                "missing Foundation tier framing (portfolio-only vs Launch+)",
            )
        )

    return issues


def collect_terms_html_issues(html: str) -> list[ScopeIssue]:
    """Terms revision caps must match package_config."""
    issues: list[ScopeIssue] = []
    if not html.strip():
        return _issues(ScopeIssue("terms_html", "empty terms HTML"))

    for slug in package_display_order():
        pkg = PACKAGES[slug]
        if pkg.display_name not in html:
            issues.append(ScopeIssue("terms_html", f"missing package name {pkg.display_name!r}"))
        if f"{pkg.revision_rounds} round" not in html.lower():
            issues.append(
                ScopeIssue(
                    "terms_html",
                    f"{slug}: missing {pkg.revision_rounds} revision round(s)",
                )
            )

    if "described at checkout" not in html.lower() and "checkout page" not in html.lower():
        issues.append(ScopeIssue("terms_html", "§2 must reference checkout as scope source"))

    return issues


def run_scope_audit(
    *,
    checkout_html: str | None = None,
    landing_html: str | None = None,
    terms_html: str | None = None,
) -> list[ScopeIssue]:
    issues: list[ScopeIssue] = []
    issues.extend(collect_config_layer_issues())
    issues.extend(collect_sales_layer_issues())
    issues.extend(collect_case_study_issues())
    issues.extend(collect_comparison_issues())
    if checkout_html is not None:
        issues.extend(collect_checkout_html_issues(checkout_html))
    if landing_html is not None:
        issues.extend(collect_landing_html_issues(landing_html))
    if terms_html is not None:
        issues.extend(collect_terms_html_issues(terms_html))
    return issues


def format_scope_report(issues: list[ScopeIssue]) -> str:
    if not issues:
        return "OK — no scope drift detected."
    lines = [f"[{issue.layer}] {issue.message}" for issue in issues]
    return "\n".join(lines)


def assert_scope_chain(
    *,
    checkout_html: str | None = None,
    landing_html: str | None = None,
    terms_html: str | None = None,
) -> None:
    issues = run_scope_audit(
        checkout_html=checkout_html,
        landing_html=landing_html,
        terms_html=terms_html,
    )
    if issues:
        raise AssertionError(format_scope_report(issues))
