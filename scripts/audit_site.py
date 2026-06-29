"""One-shot production + local audit. Run: python scripts/audit_site.py [--base URL]"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from urllib.parse import urljoin

import httpx

BANNED_PHRASES = (
    "career systems",
    "student perk",
    "shopify",
    "operator dashboard",
    "internal pipeline",
    "malik lomax",
    "maliklomax",
)

PUBLIC_ROUTES = ("/", "/demo", "/contact", "/checkout", "/start", "/status", "/login")
PRIVATE_ROUTES = ("/dashboard", "/ops", "/clients/1")
STATIC_ASSETS = (
    "/static/logo.png",
    "/static/logo-icon.png",
    "/static/logo-header.png",
    "/static/public.css",
)
SEO_REQUIRED = (
    'rel="canonical"',
    'property="og:title"',
    'property="og:image"',
    'name="twitter:card"',
    "summary_large_image",
    "brand-mark--icon",
    "brand-name",
)


@dataclass
class Finding:
    level: str  # pass | warn | fail
    area: str
    message: str


@dataclass
class AuditReport:
    base: str
    findings: list[Finding] = field(default_factory=list)

    def add(self, level: str, area: str, message: str) -> None:
        self.findings.append(Finding(level, area, message))

    @property
    def failed(self) -> int:
        return sum(1 for f in self.findings if f.level == "fail")

    @property
    def warned(self) -> int:
        return sum(1 for f in self.findings if f.level == "warn")


def audit(base: str, timeout: float = 25.0) -> AuditReport:
    report = AuditReport(base=base.rstrip("/"))
    client = httpx.Client(timeout=timeout, follow_redirects=True)

    try:
        health = client.get(f"{report.base}/health")
        if health.status_code == 200:
            report.add("pass", "health", f"/health -> {health.status_code}")
        else:
            report.add("fail", "health", f"/health -> {health.status_code}")

        for path in PUBLIC_ROUTES:
            url = f"{report.base}{path}"
            try:
                resp = client.get(url)
            except httpx.HTTPError as exc:
                report.add("fail", "routes", f"{path} request error: {exc}")
                continue

            if resp.status_code != 200:
                report.add("fail", "routes", f"{path} -> {resp.status_code}")
                continue
            report.add("pass", "routes", f"{path} -> 200")

            lower = resp.text.lower()
            for phrase in BANNED_PHRASES:
                if phrase in lower:
                    report.add("fail", "content", f"{path} contains banned phrase: {phrase!r}")

            if path in ("/terms", "/privacy", "/contact") and "hello@" not in lower:
                report.add("warn", "content", f"{path} missing public support email")

            if path == "/":
                for token in SEO_REQUIRED:
                    if token not in resp.text:
                        report.add("fail", "seo", f"/ missing {token!r}")
                if "Doggybagg" not in resp.text and "doggybagg" not in lower:
                    report.add("warn", "seo", "/ missing site name in HTML")
                if "Take it with you" not in resp.text:
                    report.add("fail", "seo", "/ missing tagline")

            if path == "/login" and 'content="noindex, nofollow"' not in resp.text:
                report.add("fail", "seo", "/login not noindex")

        for path in PRIVATE_ROUTES:
            url = f"{report.base}{path}"
            resp = client.get(url)
            final = str(resp.url)
            if path == "/ops" and "/login" not in final:
                report.add("fail", "ops", f"/ops did not redirect to login (final={final})")
            elif path == "/dashboard" and resp.status_code == 200 and "/login" not in final:
                report.add("fail", "ops", "/dashboard accessible without auth redirect")
            else:
                report.add("pass", "ops", f"{path} -> {resp.status_code} final={final}")

        robots = client.get(f"{report.base}/robots.txt")
        if robots.status_code == 200 and "Sitemap:" in robots.text:
            report.add("pass", "seo", "robots.txt present with Sitemap")
        else:
            report.add("fail", "seo", f"robots.txt bad: {robots.status_code}")

        sitemap = client.get(f"{report.base}/sitemap.xml")
        if sitemap.status_code == 200 and "<loc>" in sitemap.text:
            report.add("pass", "seo", "sitemap.xml present")
        else:
            report.add("fail", "seo", f"sitemap.xml bad: {sitemap.status_code}")

        for asset in STATIC_ASSETS:
            url = f"{report.base}{asset}"
            head = client.head(url)
            if head.status_code != 200:
                report.add("fail", "assets", f"{asset} -> {head.status_code}")
                continue
            size = int(head.headers.get("content-length", "0") or 0)
            if size == 0:
                get = client.get(url)
                size = len(get.content)
            report.add("pass", "assets", f"{asset} -> {size // 1024}KB")
            if asset.endswith("logo.png") and size > 512 * 1024:
                report.add("fail", "stripe", f"logo.png {size} bytes exceeds Stripe 512KB cap")

        canonical_home = client.get(f"{report.base}/")
        m = re.search(r'rel="canonical"\s+href="([^"]+)"', canonical_home.text)
        if m and "doggybagg.cc" in m.group(1):
            report.add("pass", "seo", f"canonical -> {m.group(1)}")
        elif m:
            report.add("warn", "seo", f"canonical unexpected: {m.group(1)}")
        else:
            report.add("fail", "seo", "canonical tag missing on /")

    finally:
        client.close()

    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="https://doggybagg.cc", help="Site origin")
    args = parser.parse_args()
    report = audit(args.base)

    print(f"\n=== AUDIT: {report.base} ===\n")
    for area in ("health", "routes", "content", "seo", "ops", "assets", "stripe"):
        items = [f for f in report.findings if f.area == area]
        if not items:
            continue
        print(f"[{area.upper()}]")
        for f in items:
            icon = {"pass": "OK", "warn": "!!", "fail": "XX"}[f.level]
            print(f"  {icon} {f.message}")
        print()

    print(f"Summary: {report.failed} failed, {report.warned} warnings, "
          f"{sum(1 for f in report.findings if f.level == 'pass')} passed")
    return 1 if report.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
