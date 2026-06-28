"""Extended production checks. Run: python scripts/audit_site.py --extended"""
from __future__ import annotations

import httpx


def run_extended(base: str = "https://doggybagg.cc") -> int:
    base = base.rstrip("/")
    fails = 0
    client = httpx.Client(timeout=30, follow_redirects=True)

    def check(name: str, ok: bool, detail: str) -> None:
        nonlocal fails
        print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}")
        if not ok:
            fails += 1

    # www
    bare = httpx.Client(timeout=30, follow_redirects=False)
    www = bare.get("https://www.doggybagg.cc/")
    check("www redirect", www.status_code in (301, 302, 307, 308), f"{www.status_code} -> {www.headers.get('location', '')}")

    final = client.get("https://www.doggybagg.cc/")
    check("www resolves", "doggybagg.cc" in str(final.url), str(final.url))

    # ops gate (browser)
    dash = client.get(f"{base}/dashboard", headers={"Accept": "text/html"})
    check("dashboard gated", "/login" in str(dash.url), str(dash.url))

    home = client.get(f"{base}/").text
    check("twitter large image", "summary_large_image" in home, "present")
    check("json-ld", "application/ld+json" in home and "Doggybagg" in home, "present")
    check("logo header", "logo-header.png" in home, "present")
    check("home clean", "career systems" not in home.lower(), "no legacy brand")

    for path in ("/start", "/example/alex-rivera", "/example/jordan-kim"):
        body = client.get(f"{base}{path}").text.lower()
        check(f"{path} clean", "career systems" not in body, "no legacy brand")

    client.close()
    bare.close()
    print(f"\nExtended: {fails} failure(s)")
    return fails


if __name__ == "__main__":
    raise SystemExit(run_extended())
