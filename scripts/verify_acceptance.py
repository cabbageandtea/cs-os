#!/usr/bin/env python3
"""Run paid-deliverable acceptance checks against a live or local CS-OS instance."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.package_scope import format_scope_report, run_scope_audit

BANNED_PUBLIC_PHRASES: tuple[str, ...] = (
    "career systems",
    "student perk",
    "setup fee",
    "perk arbitrage",
    "loss leader",
    "loss-leader",
    "free to you",
    "activate your student dev perks",
    "INTERNAL_PLAYBOOK",
    "STUDENT_PERK_MODEL",
)

PUBLIC_ROUTES: tuple[str, ...] = (
    "/",
    "/demo",
    "/contact",
    "/checkout",
    "/start",
    "/status",
    "/terms",
    "/privacy",
    "/purchase/return",
    "/purchase/cancelled",
    "/login",
)


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str
    weight: int


def _grade(score: int) -> str:
    if score >= 95:
        return "A"
    if score >= 85:
        return "B+"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def run_checks(base_url: str, timeout: float) -> list[CheckResult]:
    root = base_url.rstrip("/")
    results: list[CheckResult] = []

    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        try:
            health = client.get(f"{root}/health")
            if health.status_code == 404:
                results.append(
                    CheckResult(
                        "health_database",
                        False,
                        "endpoint missing — deploy pending",
                        15,
                    )
                )
                results.append(CheckResult("health_stripe", False, "endpoint missing", 10))
                results.append(CheckResult("health_email", False, "endpoint missing", 5))
            else:
                payload = health.json()
                ok = health.status_code == 200 and payload.get("checks", {}).get("database") is True
                results.append(
                    CheckResult(
                        "health_database",
                        ok,
                        f"status={health.status_code} body={payload.get('status')}",
                        15,
                    )
                )
                stripe_ok = bool(payload.get("checks", {}).get("stripe"))
                results.append(
                    CheckResult(
                        "health_stripe",
                        stripe_ok,
                        "STRIPE_SECRET_KEY configured" if stripe_ok else "missing Stripe key",
                        10,
                    )
                )
                email_ok = bool(payload.get("email_configured"))
                results.append(
                    CheckResult(
                        "health_email",
                        email_ok,
                        "Resend or SMTP configured" if email_ok else "email logs only (dev)",
                        5,
                    )
                )
        except httpx.HTTPError as exc:
            results.append(CheckResult("health_database", False, str(exc), 15))
            results.append(CheckResult("health_stripe", False, "health unreachable", 10))
            results.append(CheckResult("health_email", False, "health unreachable", 5))

        for path in PUBLIC_ROUTES:
            try:
                response = client.get(f"{root}{path}")
                body = response.text.lower()
                leaked = [p for p in BANNED_PUBLIC_PHRASES if p in body]
                passed = response.status_code == 200 and not leaked
                detail = f"HTTP {response.status_code}"
                if leaked:
                    detail += f" leaked={leaked[:2]}"
                results.append(
                    CheckResult(
                        f"public{path.replace('/', '_') or '_root'}",
                        passed,
                        detail,
                        3,
                    )
                )
            except httpx.HTTPError as exc:
                results.append(
                    CheckResult(
                        f"public{path.replace('/', '_') or '_root'}",
                        False,
                        str(exc),
                        3,
                    )
                )

        try:
            dash = client.get(
                f"{root}/dashboard",
                follow_redirects=False,
                headers={"Accept": "text/html,application/xhtml+xml"},
            )
            location = (dash.headers.get("location") or "").lower()
            passed = dash.status_code in (301, 302, 303, 307, 308) and "/login" in location
            results.append(
                CheckResult(
                    "ops_auth_gate",
                    passed,
                    f"HTTP {dash.status_code} -> {dash.headers.get('location', '')}",
                    10,
                )
            )
        except httpx.HTTPError as exc:
            results.append(CheckResult("ops_auth_gate", False, str(exc), 10))

        scope_html: dict[str, str | None] = {
            "checkout_html": None,
            "landing_html": None,
            "terms_html": None,
        }
        for path, key in (("/", "landing_html"), ("/checkout", "checkout_html"), ("/terms", "terms_html")):
            try:
                response = client.get(f"{root}{path}")
                if response.status_code == 200:
                    scope_html[key] = response.text
            except httpx.HTTPError:
                pass

        scope_issues = run_scope_audit(**scope_html)
        results.append(
            CheckResult(
                "package_scope_chain",
                not scope_issues,
                "OK" if not scope_issues else format_scope_report(scope_issues)[:240],
                12,
            )
        )

    return results


def summarize(results: list[CheckResult]) -> dict[str, Any]:
    total_weight = sum(r.weight for r in results)
    earned = sum(r.weight for r in results if r.passed)
    score = round((earned / total_weight) * 100) if total_weight else 0
    return {
        "score": score,
        "grade": _grade(score),
        "passed": sum(1 for r in results if r.passed),
        "failed": sum(1 for r in results if not r.passed),
        "total": len(results),
        "checks": [
            {"name": r.name, "passed": r.passed, "detail": r.detail, "weight": r.weight}
            for r in results
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="CS-OS acceptance verification")
    parser.add_argument(
        "--base-url",
        default=os.environ.get("BASE_URL", "http://127.0.0.1:8003"),
        help="Target instance URL",
    )
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    results = run_checks(args.base_url, args.timeout)
    report = summarize(results)
    report["base_url"] = args.base_url.rstrip("/")

    if args.as_json:
        print(json.dumps(report, indent=2))
    else:
        print(f"CS-OS acceptance — {report['base_url']}")
        print(f"Score: {report['score']}/100 ({report['grade']})")
        print(f"Passed: {report['passed']}/{report['total']}\n")
        for row in report["checks"]:
            mark = "PASS" if row["passed"] else "FAIL"
            print(f"  [{mark}] {row['name']}: {row['detail']}")

    return 0 if report["score"] >= 80 else 1


if __name__ == "__main__":
    sys.exit(main())
