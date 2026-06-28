# CS-OS Pricing Model

**Status:** Documentation only — no payment implementation  
**Purpose:** Define sellable packages, fulfillment scope, and future Stripe mapping  
**Config principle:** Prices and Stripe IDs live in environment/config — never hardcoded in application logic

---

## Strategic Context: The Real Asset

CS-OS is the delivery engine. The long-term proprietary asset is the **Career Transformation Dataset** accumulated across every client:

| Direction | Data captured |
|-----------|---------------|
| **Input** | Background, goals, skills, experience structure, target role, links |
| **Output** | Positioning narrative, portfolio structure, resume language, deliverable artifacts |
| **Outcome** (future) | Interview rate, callbacks, offers, time-to-hire |

Each fulfilled package adds a labeled row: *given this profile + goal → this positioning + structure worked*. That dataset compounds; the tooling does not.

**Documentation implication:** Package definitions below specify what to **capture at intake** and **store at delivery** so future automation and model training have clean labels.

---

## Package Overview

| Package | Slug | Legacy name | Positioning |
|---------|------|-------------|-------------|
| **Foundation** | `foundation` | Basic | Proof of work online — portfolio + deploy |
| **Launch** | `launch` | Standard | Recruiter-ready profile — portfolio + resume + LinkedIn |
| **Accelerator** | `accelerator` | Premium | Full career narrative — Launch + strategy + audit + revisions |

---

## Configurable Pricing (source of truth for future checkout)

Prices are **not** stored in CS-OS application code. Use config or environment at checkout-creation time.

### Recommended config file (future)

See [`packages.config.example.yaml`](./packages.config.example.yaml) for the full schema.

### Default price table (revise without code changes)

| Package | List price (USD) | Config key | Stripe (future) |
|---------|------------------|------------|-----------------|
| Foundation | $99 | `PRICE_FOUNDATION_CENTS=9900` | `STRIPE_PRICE_FOUNDATION` |
| Launch | $199 | `PRICE_LAUNCH_CENTS=19900` | `STRIPE_PRICE_LAUNCH` |
| Accelerator | $349 | `PRICE_ACCELERATOR_CENTS=34900` | `STRIPE_PRICE_ACCELERATOR` |

**Rules:**

- Change prices in Stripe Dashboard + env vars only
- CS-OS stores `package_slug` on client record (`foundation` | `launch` | `accelerator`)
- Display price at checkout from Stripe Price object, not from CS-OS DB
- Promotional/discount codes: Stripe Coupons — no CS-OS logic in Phase 4a

---

## Package 1: Foundation

### Name & slug

- **Display name:** Foundation  
- **Slug:** `foundation`  
- **Tagline:** *Get your proof of work online.*

### Description (customer-facing)

> For candidates who need a professional portfolio deployed and GitHub aligned with their target role. You bring your projects and experience; we structure, build, and ship a live portfolio site.

**Best for:** Students, bootcamp grads, career changers into technical roles, and early-career builders with projects but no web presence.

**Not included:** Resume rewrite, LinkedIn optimization, strategy session.

### Included deliverables

| Deliverable | Included | Notes |
|-------------|----------|-------|
| Portfolio website | ✓ | Template-based (Minimal or Data/Tech) |
| Deployment URL | ✓ | GitHub Pages or Render; subdomain included |
| GitHub profile guidance | ✓ | Pin repos, bio, README suggestions (client applies) |
| Resume (PDF) | ✗ | — |
| LinkedIn optimization notes | ✗ | — |
| Strategy session | ✗ | — |
| Custom domain setup | ✗ | Add-on or Accelerator |

### Internal fulfillment tasks

Maps to CS-OS pipeline tasks. **Included** tasks marked ✓.

| Stage | Task | Foundation |
|-------|------|------------|
| Intake | Review intake data | ✓ |
| Analysis | Audit LinkedIn profile | ○ (light — link check only) |
| Analysis | Audit GitHub profile | ✓ |
| Analysis | Select portfolio template | ✓ |
| Build | Build portfolio site | ✓ |
| Build | Resume rewrite | ✗ skip |
| QA | QA checklist | ✓ |
| Review | Client review + revisions | ✓ (1 round) |
| Delivered | Deploy + handoff | ✓ |

**Revision policy:** 1 round of portfolio copy/layout fixes at Review.

### Estimated delivery effort

| Activity | Hours |
|----------|-------|
| Intake review | 0.25 |
| Analysis + template | 0.75 |
| Portfolio build | 2.0 |
| QA | 0.5 |
| Review + revisions | 0.75 |
| Deploy + handoff | 0.25 |
| **Total** | **~4.5 hrs** |

### Margin assumptions (Foundation @ $99)

| Line item | Amount |
|-----------|--------|
| Revenue | $99.00 |
| Stripe fee (~2.9% + $0.30) | −$3.17 |
| Net revenue | $95.83 |
| Labor (@ $25/hr internal) | −$112.50 |
| **Gross margin (manual delivery)** | **−$16.67** |

**Interpretation:** Foundation is a **loss-leader / acquisition tier** at manual labor rates. Margin turns positive when build drops below ~3.5 hrs (template + automation) or price increases to ~$119.

---

## Package 2: Launch

### Name & slug

- **Display name:** Launch  
- **Slug:** `launch`  
- **Tagline:** *Become recruiter-ready across portfolio, resume, and LinkedIn.*

### Description (customer-facing)

> Everything in Foundation, plus impact-based resume rewrite and LinkedIn profile alignment. One coherent story across every platform recruiters check.

**Best for:** Active job seekers ready to apply within 30 days.

### Included deliverables

| Deliverable | Included |
|-------------|----------|
| Portfolio website | ✓ |
| Deployment URL | ✓ |
| GitHub profile guidance | ✓ |
| Resume (PDF) | ✓ |
| LinkedIn optimization notes | ✓ |
| Strategy session | ✗ |
| Career narrative document | ✗ |

### Internal fulfillment tasks

| Stage | Task | Launch |
|-------|------|--------|
| Intake | Review intake data | ✓ |
| Analysis | Audit LinkedIn profile | ✓ |
| Analysis | Audit GitHub profile | ✓ |
| Analysis | Select portfolio template | ✓ |
| Build | Build portfolio site | ✓ |
| Build | Resume rewrite | ✓ |
| QA | QA checklist | ✓ |
| Review | Client review + revisions | ✓ (2 rounds) |
| Delivered | Deploy + handoff | ✓ |

**Revision policy:** 2 rounds across resume + portfolio + LinkedIn copy.

### Estimated delivery effort

| Activity | Hours |
|----------|-------|
| Foundation subtotal | 4.5 |
| LinkedIn audit + copy | 1.0 |
| Resume rewrite | 1.5 |
| Extra revision round | 0.5 |
| **Total** | **~7.5 hrs** |

### Margin assumptions (Launch @ $199)

| Line item | Amount |
|-----------|--------|
| Revenue | $199.00 |
| Stripe fee | −$6.07 |
| Net revenue | $192.93 |
| Labor (@ $25/hr) | −$187.50 |
| **Gross margin** | **+$5.43 (~3%)** |

**Interpretation:** Launch is **margin-neutral** at manual delivery. Target automation to bring labor to ~5 hrs for ~37% margin, or price at $229 for healthy manual margin.

---

## Package 3: Accelerator

### Name & slug

- **Display name:** Accelerator  
- **Slug:** `accelerator`  
- **Tagline:** *Full career positioning with strategy, narrative alignment, and premium support.*

### Description (customer-facing)

> Everything in Launch, plus a 30-minute career strategy session, cross-platform narrative alignment, and an extended profile audit with priority revisions. For candidates targeting competitive roles or career pivots.

**Best for:** Premium placements, career changers, new grads targeting top-tier roles.

### Included deliverables

| Deliverable | Included |
|-------------|----------|
| Portfolio website | ✓ |
| Deployment URL | ✓ |
| GitHub profile guidance | ✓ |
| Resume (PDF) | ✓ |
| LinkedIn optimization notes | ✓ |
| Career narrative summary | ✓ (1-page positioning doc) |
| 30-min strategy session | ✓ |
| Custom domain setup guide | ✓ (client-owned domain) |

### Internal fulfillment tasks

| Stage | Task | Accelerator |
|-------|------|-------------|
| All Launch tasks | | ✓ |
| Analysis | Career narrative alignment (internal) | ✓ |
| Review | Client review + revisions | ✓ (3 rounds) |
| Delivered | Strategy session + handoff call | ✓ |

### Estimated delivery effort

| Activity | Hours |
|----------|-------|
| Launch subtotal | 7.5 |
| Strategy session + prep | 1.0 |
| Narrative alignment doc | 1.0 |
| Extra revision round | 0.5 |
| Custom domain guide | 0.25 |
| **Total** | **~10.25 hrs** |

### Margin assumptions (Accelerator @ $349)

| Line item | Amount |
|-----------|--------|
| Revenue | $349.00 |
| Stripe fee | −$10.42 |
| Net revenue | $338.58 |
| Labor (@ $25/hr) | −$256.25 |
| **Gross margin** | **+$82.33 (~24%)** |

**Interpretation:** Accelerator is the **profit tier** at manual delivery. Protect margin with clear revision caps and session no-show policy.

---

## Comparative Summary

| | Foundation | Launch | Accelerator |
|---|------------|--------|-------------|
| **List price** | $99 | $199 | $349 |
| **Est. hours** | 4.5 | 7.5 | 10.25 |
| **Deliverables** | 2 | 4 | 7 |
| **Revision rounds** | 1 | 2 | 3 |
| **Manual margin @ $25/hr** | Negative | ~3% | ~24% |
| **Dataset richness** | Low | Medium | High |

---

## Future Stripe Product Mapping

One Stripe **Product** per package; one active **Price** per product (USD, one-time).

| Package slug | Stripe Product name | Env: Product ID | Env: Price ID |
|--------------|---------------------|-----------------|---------------|
| `foundation` | CS-OS Foundation | `STRIPE_PRODUCT_FOUNDATION` | `STRIPE_PRICE_FOUNDATION` |
| `launch` | CS-OS Launch | `STRIPE_PRODUCT_LAUNCH` | `STRIPE_PRICE_LAUNCH` |
| `accelerator` | CS-OS Accelerator | `STRIPE_PRODUCT_ACCELERATOR` | `STRIPE_PRICE_ACCELERATOR` |

### Checkout Session metadata (required)

```yaml
metadata:
  package_slug: foundation | launch | accelerator
  csos_version: "1"
  source: stripe_checkout
```

CS-OS maps `package_slug` → client `package_tier` display name + fulfillment rules (future).

### Legacy tier migration

| Old intake value | New slug |
|------------------|----------|
| Basic | `foundation` |
| Standard | `launch` |
| Premium | `accelerator` |

Existing clients keep stored values; new checkouts use slugs only.

---

## Career Transformation Dataset — Capture Spec

Per client, store (future schema / export):

**Input fields**

- `target_role`, `experience_summary`, `skills`
- `goals` (Accelerator intake add-on)
- `linkedin_url`, `github_url`
- `package_slug`, `intake_completed_at`

**Output artifacts**

- Portfolio template ID + final URL
- Resume PDF hash / version
- LinkedIn copy blocks
- Narrative summary (Accelerator)
- Positioning keywords extracted

**Outcome fields** (manual follow-up initially)

- `interviews_30d`, `offers`, `satisfaction_score`
- `revision_count` (from TimestampLog)

This aligns package tiers with **dataset label quality**: Accelerator rows are the highest-value training examples.

---

## Operational Rules (all packages)

1. **No work before paid + intake complete** (Phase 4a+)
2. **Deliverables gated by package** — do not ship resume on Foundation
3. **Revision caps enforced at Review** — overages quoted separately
4. **Refund policy:** Before Build starts — full minus Stripe fee; after Build — no refund (document in ToS)
5. **Price changes:** New Stripe Price objects; retire old prices; never mutate historical client records

---

## What This Document Does Not Do

- Does not change CS-OS application code
- Does not create Stripe products (manual Dashboard step before Phase 4a implementation)
- Does not bind legal pricing — update config when market validates

---

## Related Documents

- [PHASE_4A_PAYMENT_PLAN.md](./PHASE_4A_PAYMENT_PLAN.md) — Checkout + webhook implementation
- [AUTOMATION_ARCHITECTURE.md](./AUTOMATION_ARCHITECTURE.md) — Full automation blueprint
- [EXECUTION.md](../EXECUTION.md) — Original offer structure (Basic / Standard / Premium)
- [packages.config.example.yaml](./packages.config.example.yaml) — Machine-readable package config

---

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Package names | Foundation, Launch, Accelerator |
| Code impact | None |
