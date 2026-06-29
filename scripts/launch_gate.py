#!/usr/bin/env python3
"""One-command launch readiness check for Doggybagg production."""

from __future__ import annotations

import argparse
import subprocess
import sys


def _run(label: str, cmd: list[str]) -> int:
    print(f"\n=== {label} ===")
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        print(f"FAIL: {label} (exit {result.returncode})")
    else:
        print(f"PASS: {label}")
    return result.returncode


def _run_with_retry(label: str, cmd: list[str], retries: int) -> int:
    result = _run(label, cmd)
    attempt = 1
    while result != 0 and attempt <= retries:
        print(f"RETRY: {label} ({attempt}/{retries})")
        result = _run(f"{label} retry {attempt}", cmd)
        attempt += 1
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run launch readiness checks")
    parser.add_argument(
        "base_url",
        nargs="?",
        default="https://doggybagg.cc",
        help="Target base URL (default: https://doggybagg.cc)",
    )
    parser.add_argument(
        "--verify-timeout",
        type=float,
        default=45.0,
        help="Timeout in seconds for verify_acceptance HTTP checks (default: 45)",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=1,
        help="Retry count for flaky networked checks (default: 1)",
    )
    args = parser.parse_args()
    base = args.base_url
    import os

    os.environ["BASE_URL"] = base
    failures = 0
    failures += _run("pytest", [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=no"])
    failures += _run_with_retry(
        "verify_acceptance",
        [
            sys.executable,
            "scripts/verify_acceptance.py",
            "--base-url",
            base,
            "--timeout",
            str(args.verify_timeout),
        ],
        args.retries,
    )
    failures += _run_with_retry(
        "audit_site",
        [sys.executable, "scripts/audit_site.py", "--base", base],
        args.retries,
    )
    try:
        import httpx

        health = httpx.get(f"{base.rstrip('/')}/health", timeout=20.0).json()
        if not health.get("collect_money_ready"):
            print(
                f"\nNOTE: collect_money_ready=false (stripe_mode={health.get('stripe_mode')}). "
                "Set live Stripe keys on Render to charge customers."
            )
    except Exception as exc:
        print(f"\nWARN: could not read /health: {exc}")
        failures += 1
    if failures:
        print(f"\nLaunch gate: BLOCKED ({failures} step(s) failed)")
        return 1
    print("\nLaunch gate: READY — collect money at", base)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
