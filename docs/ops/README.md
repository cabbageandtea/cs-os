# OPS ONLY — do not link from public site

This folder is for **operator and agent** context. Never expose on:

- `/`, `/checkout`, `/start`, `/intake/*`, `/contact`, `/demo`
- Customer emails or Stripe product descriptions
- Any URL a competitor could browse

## Public vs internal

| Public (client-safe) | Internal (this folder) |
|----------------------|-------------------------|
| Outcomes: live portfolio, aligned resume | Margin, loss-leader, perk arbitrage |
| Account checklist (GitHub, Gmail, LinkedIn) | Which partner offers to prioritize |
| "Accounts in your name" | Setup-fee vs free-perk economics |
| "Why not DIY?" (time, process) | Conversion scripts mentioning Student Pack being free |

## Files

- [INTERNAL_PLAYBOOK.md](./INTERNAL_PLAYBOOK.md) — business model, package leverage, liaison scripts
- [CLAIMS_SOURCE_OF_TRUTH.csv](./CLAIMS_SOURCE_OF_TRUTH.csv) — every public claim mapped to proof and guard tests
- [DELIVERY_READINESS_SCORECARD.md](./DELIVERY_READINESS_SCORECARD.md) — package-by-package sell/no-sell gate
- [REVENUE_INCIDENT_PLAYBOOK.md](./REVENUE_INCIDENT_PLAYBOOK.md) — Sev-1 protocol for payment/brief/email failures
- [14_DAY_EXECUTION_BOARD.md](./14_DAY_EXECUTION_BOARD.md) — operator plan to close launch blockers quickly
- [EXTERNAL_PROPERTY_REGISTRY.md](./EXTERNAL_PROPERTY_REGISTRY.md) — track Search Console, Ads, GBP, DNS, and drift

When editing `app/sales_content.py` or public templates, use **outcome language only**.
