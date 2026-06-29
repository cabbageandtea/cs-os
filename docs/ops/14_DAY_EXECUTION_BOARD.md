# 14-Day Execution Board

Outcome: raise launch confidence and remove revenue blockers fast.

## Week 1

### Day 1-2

- Finalize [CLAIMS_SOURCE_OF_TRUTH.csv](./CLAIMS_SOURCE_OF_TRUTH.csv) with all public claims.
- Mark each claim `approved`, `draft`, or `deprecated`.
- Assign one owner per claim and one test guard per claim.

### Day 3-4

- Run `python scripts/validate_claims_matrix.py` and fix all failures.
- Run `python scripts/launch_gate.py https://doggybagg.cc` and log findings.
- Update [DELIVERY_READINESS_SCORECARD.md](./DELIVERY_READINESS_SCORECARD.md) with real scores.

### Day 5-7

- Close any Sev-1 blocker discovered in launch gate.
- Execute one full prod-safe smoke: pay -> brief -> ops dashboard -> handoff email.
- Record evidence links in claims matrix for all payment and fulfillment claims.

## Week 2

### Day 8-10

- Perform two operator handoff drills from runbooks.
- Validate fallback path for email outage and dashboard mismatch.
- Fill [EXTERNAL_PROPERTY_REGISTRY.md](./EXTERNAL_PROPERTY_REGISTRY.md).

### Day 11-12

- Run another launch gate and compare deltas.
- Re-score package readiness and set sell/no-sell per package.
- Remove or rewrite any claim still lacking evidence.

### Day 13-14

- Publish final go/no-go summary.
- Schedule weekly launch gate cadence.
- Schedule monthly incident drill.

## Definition of done

- No Sev-1 open issues.
- All public claims are `approved` with proof + test guard.
- Every package score >= 90 or explicitly marked not for sale.
