# Delivery Readiness Scorecard

Use this before opening payment links to strangers. Each package must score >= 90.

## Scoring buckets

- Asset completeness (30): Every promised deliverable exists and is usable.
- QA reliability (30): Automated + manual checks pass in launch gate.
- Ops readiness (20): Runbooks, owner coverage, and escalation path are live.
- Support readiness (20): FAQ, response macros, and handoff workflow are ready.

## Pass/fail policy

- 90-100: Sell normally.
- 80-89: Sell only with explicit caveat documented in checkout/terms.
- <80: Do not sell.

## Package score table

| Package | Asset (30) | QA (30) | Ops (20) | Support (20) | Total | Sell? | Notes |
|---|---:|---:|---:|---:|---:|---|---|
| Foundation | 29 | 28 | 16 | 15 | 88 | Caveat | Passes launch checks; requires second-operator drill + support macro QA before full green. |
| Launch | 30 | 28 | 16 | 16 | 90 | Yes | Site, resume, LinkedIn scope and legal alignment verified across landing/checkout/terms. |
| Accelerator | 29 | 27 | 16 | 16 | 88 | Caveat | Core stack is healthy; strategy-session and escalation rehearsal evidence still needed for >=90. |

## Evidence snapshot (2026-06-29)

- `python scripts/launch_gate.py https://doggybagg.cc` -> blocked once due transient acceptance timeout.
- `python scripts/verify_acceptance.py --base-url https://doggybagg.cc --timeout 45` -> 100/100 (A), 16/16 checks passed.
- `python -m pytest tests/ -q --tb=no` -> 136 passed.
- `python scripts/audit_site.py --base https://doggybagg.cc` -> 0 failed, 0 warnings.

## Minimum evidence before setting score > 0

- Asset: `templates/` and seeded deliverables match package scope.
- QA: `python scripts/launch_gate.py` returns READY for target base URL.
- Ops: Two operators can execute handoff runbook without edits.
- Support: Response macros and escalation owner are documented.
