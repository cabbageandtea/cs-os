#!/usr/bin/env python3
"""One-command launch readiness check for Doggybagg production."""

from __future__ import annotations

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


def main() -> int:
    base = sys.argv[1] if len(sys.argv) > 1 else "https://doggybagg.cc"
    import os

    os.environ["BASE_URL"] = base
    failures = 0
    failures += _run("pytest", [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=no"])
    failures += _run(
        "verify_acceptance",
        [sys.executable, "scripts/verify_acceptance.py"],
    )
    failures += _run(
        "audit_site",
        [sys.executable, "scripts/audit_site.py", "--base", base],
    )
    if failures:
        print(f"\nLaunch gate: BLOCKED ({failures} step(s) failed)")
        return 1
    print("\nLaunch gate: READY — collect money at", base)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
