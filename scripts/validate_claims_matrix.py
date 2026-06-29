#!/usr/bin/env python3
"""Validate docs/ops/CLAIMS_SOURCE_OF_TRUTH.csv for launch gating."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ALLOWED_STATUS = {"draft", "approved", "deprecated"}
PUBLIC_SURFACES = {
    "landing",
    "checkout",
    "start",
    "status",
    "contact",
    "demo",
    "terms",
    "privacy",
    "public_routes",
    "purchase_return",
}
REQUIRED_COLUMNS = [
    "claim_id",
    "claim_text",
    "surface",
    "deliverable_key",
    "owner",
    "evidence_link",
    "test_guard",
    "status",
    "last_verified",
    "notes",
]


def validate(path: Path) -> list[str]:
    if not path.exists():
        return [f"missing file: {path}"]

    errors: list[str] = []
    seen_ids: set[str] = set()
    seen_surface_claim: set[tuple[str, str]] = set()

    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        for col in REQUIRED_COLUMNS:
            if col not in headers:
                errors.append(f"missing column: {col}")
        if errors:
            return errors

        rows = list(reader)
        if not rows:
            errors.append("claims matrix is empty")
            return errors

        for idx, row in enumerate(rows, start=2):
            claim_id = (row.get("claim_id") or "").strip()
            claim_text = (row.get("claim_text") or "").strip()
            surface = (row.get("surface") or "").strip()
            owner = (row.get("owner") or "").strip()
            status = (row.get("status") or "").strip().lower()
            evidence_link = (row.get("evidence_link") or "").strip()
            test_guard = (row.get("test_guard") or "").strip()
            deliverable_key = (row.get("deliverable_key") or "").strip()

            if not claim_id:
                errors.append(f"row {idx}: claim_id is required")
            elif claim_id in seen_ids:
                errors.append(f"row {idx}: duplicate claim_id {claim_id}")
            else:
                seen_ids.add(claim_id)

            if not claim_text:
                errors.append(f"row {idx}: claim_text is required")

            if not surface:
                errors.append(f"row {idx}: surface is required")

            if not deliverable_key:
                errors.append(f"row {idx}: deliverable_key is required")

            if not owner:
                errors.append(f"row {idx}: owner is required")

            if status not in ALLOWED_STATUS:
                errors.append(f"row {idx}: invalid status '{status}'")

            dedupe_key = (surface.lower(), claim_text.lower())
            if claim_text and surface:
                if dedupe_key in seen_surface_claim:
                    errors.append(
                        f"row {idx}: duplicate claim_text for surface '{surface}'"
                    )
                else:
                    seen_surface_claim.add(dedupe_key)

            # Public-facing claims must be production-ready.
            if surface.lower() in PUBLIC_SURFACES:
                if status != "approved":
                    errors.append(
                        f"row {idx}: public claim must be approved (surface={surface})"
                    )
                if not evidence_link:
                    errors.append(
                        f"row {idx}: public claim missing evidence_link"
                    )
                if not test_guard:
                    errors.append(
                        f"row {idx}: public claim missing test_guard"
                    )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate launch claims matrix")
    parser.add_argument(
        "--path",
        default="docs/ops/CLAIMS_SOURCE_OF_TRUTH.csv",
        help="Path to claims matrix CSV",
    )
    args = parser.parse_args()

    path = Path(args.path)
    errors = validate(path)
    if errors:
        print("Claims matrix validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    print(f"Claims matrix validation passed: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
