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
| Foundation | 0 | 0 | 0 | 0 | 0 | No | |
| Launch | 0 | 0 | 0 | 0 | 0 | No | |
| Accelerator | 0 | 0 | 0 | 0 | 0 | No | |

## Minimum evidence before setting score > 0

- Asset: `templates/` and seeded deliverables match package scope.
- QA: `python scripts/launch_gate.py` returns READY for target base URL.
- Ops: Two operators can execute handoff runbook without edits.
- Support: Response macros and escalation owner are documented.
