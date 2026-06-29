# Expert Research Brief — Launch Readiness Hardening

Date: 2026-06-29

This brief captures practical, launch-critical guidance applied to this repo.

## 1) Reliability and SRE guardrails

- Track four golden signals for public experience: latency, errors, traffic, saturation.
- Keep synthetic checks focused on checkout, auth gate, legal pages, and health endpoint dependencies.
- Treat intermittent network failures as expected; use bounded retry with explicit timeout in release gates.
- Keep a clear stop/go signal: if acceptance grade < A for public launch promises, block release.

## 2) Stripe production safety

- Verify webhook signatures on every inbound event.
- Return `2xx` fast from webhook handlers, then do heavier work asynchronously.
- Enforce idempotency for payment state writes to avoid duplicate fulfillment.
- Monitor three paths separately: checkout session creation, webhook delivery, and post-payment provisioning.
- Keep mode clarity explicit (`test` vs `live`) on health output and operator dashboard.

## 3) GitHub Actions hardening

- Prefer least-privilege `permissions` for each workflow/job.
- Pin third-party actions to trusted tags or SHAs when feasible.
- Keep deployment and payment secrets only in environment/repo secrets, never in logs.
- Gate release workflows on deterministic checks (`pytest`, acceptance audit, black-box site audit).

## 4) Email deliverability (Resend or SMTP provider)

- Require SPF + DKIM + DMARC alignment for sending domain.
- Verify domain ownership and keep sender identities consistent (`hello@doggybagg.cc`).
- Track bounce/complaint events and suppress hard bounces automatically.
- Include a fallback operator path when provider API is degraded.

## 5) Operational recommendations already reflected

- `scripts/launch_gate.py` supports configurable acceptance timeout and bounded retries.
- `docs/ops/DELIVERY_READINESS_SCORECARD.md` now includes evidence snapshot from live verification.
- Claims governance remains enforced through `docs/ops/CLAIMS_SOURCE_OF_TRUTH.csv` plus validator.

## 6) Next tightening moves

1. Add daily scheduled launch gate workflow (read-only checks) against production URL.
2. Add webhook replay drill checklist and incident rollback drill cadence.
3. Add DNS evidence table (SPF/DKIM/DMARC status, last verified timestamp, owner).
