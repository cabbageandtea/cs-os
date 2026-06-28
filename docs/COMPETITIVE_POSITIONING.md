# Competitive positioning — Doggybagg vs market

**OPS reference only.** Do not paste competitor names on public pages. Customer site uses categories (resume writers, DIY builders).

**Last researched:** June 2026

---

## Market map

| Segment | Price band | Examples (research) | What they sell |
|---------|------------|---------------------|----------------|
| Resume writers | $99–$600+ | TopResume, ZipJob, ZipJob/Resumeble, Proresumes, Resodro | ATS resume PDF, cover letter, LinkedIn “makeover” or guide |
| DIY / AI builders | $19–$50 one-time or $10–20/mo | Kavora, Foliomatic, Gradient Folio, Standowt bundle | Template portfolio + self-serve resume |
| Student CV shops | Opaque / quote | CEVEW | CV + portfolio + LinkedIn — vague pricing |
| **Doggybagg** | **$99 / $199 / $349** | — | Live portfolio on client infra + aligned resume/LinkedIn (Launch+) |

---

## Competitor mistakes (exploit, don’t copy)

### 1. Contradictory revision policies

- **TopResume:** Contract says 2 rounds in 7 days; FAQ implies “unlimited until happy.”
- **ZipJob:** “Unlimited revisions” — reviews report ~1 week practical cap.
- **Proresumes / Resodro:** “Unlimited” for 12–24 months — unsustainable; invites scope creep.

**Our counter:** Publish **1 / 2 / 3 rounds** on checkout + Terms §5. One round = one consolidated message. No “unlimited.”

### 2. Interview guarantees

- Common at TopResume, ZipJob, ResumeSpice ($149–$899 tiers).
- BBB/Trustpilot pattern: disputes when guarantee not met; refund refusal.

**Our counter:** Explicit **no interview guarantee** in Terms + FAQ. Sell deliverables, not hiring outcomes.

### 3. PDF-only or guide-only LinkedIn

- TopResume “LinkedIn makeover” = personalized PDF guide, not aligned live profile work.
- Resume writers rarely deploy GitHub/portfolio.

**Our counter:** **Live portfolio** every tier; Launch+ includes LinkedIn optimization **notes aligned to same role** as resume + site.

### 4. Platform lock-in

- Foliomatic, Kavora: host on vendor URL; client does not own repo/DNS.
- Gradient Folio: subdomain + 1yr hosting on their stack.

**Our counter:** **100% client-owned** GitHub, email, LinkedIn, domain. Handoff is the product.

### 5. Scope hidden until after payment

- Aggressive upsell after “free resume review” (TopResume funnel).
- Bundles like “5 resumes + mock interviews + portfolio” at €49 — unrealistic scope, no revision definition.
- ZipJob checkout reveals TopResume parent post-payment (Trustpilot complaints).

**Our counter:** Full **included / not included** lists on `/checkout` before Stripe. Single brand end-to-end.

### 6. Generic output / weak intake

- Reviews: “resume wasn’t what I wanted” — writer lacks context.
- AI-generated drafts without role-specific grounding.

**Our counter:** **Complete intake gates the clock.** Target role + projects fixed at start. Scope creep = new purchase.

### 7. Communication and timeline failures

- BBB: paid $900, no writer assigned, missed interview deadline, refund denied.

**Our counter:** Published turnaround targets; SLA pauses when **client** is unresponsive (Terms §3). Status at `/status`.

---

## Doggybagg wedge (what we must never dilute)

1. **Technical entry hiring** — students, bootcamp, career changers into SWE/data/analytics.
2. **Proof-of-work online** — deployed portfolio, not PDF in inbox.
3. **One narrative** — portfolio + resume + LinkedIn (Launch+) from one intake.
4. **Fixed economics** — revision caps protect margin; see `PRICING_MODEL.md` hour estimates.
5. **Show before buy** — `/example/*` mock deliveries; competitors use generic stock samples.

---

## Objection handling (customer-facing scripts)

| They say | We say |
|----------|--------|
| “Can I get 10 revisions?” | “Launch includes **2 rounds**. Send one consolidated message per round. Role changes or new projects are new scope — we can quote an add-on.” |
| “TopResume guarantees interviews” | “We don’t guarantee hiring — no one honestly can. We guarantee **defined deliverables** listed at checkout.” |
| “Fiverr is $50” | “That’s usually a PDF. We deploy a **live portfolio on your GitHub** and align platforms. Different product.” |
| “Can you apply to jobs for me?” | “Out of scope per Terms. We deliver assets; you run applications.” |
| “Unlimited edits?” | “We publish exact caps so delivery stays predictable. Unlimited policies usually break down in practice.” |

---

## Research sources

- Forbes Vetted resume services roundup (2026 pricing/revisions)
- TopResume / ZipJob reviews (300hours, Find My Profession, Trustpilot, BBB)
- Proresumes.us, Resodro.com pricing pages
- Kavora, Foliomatic, Gradient Folio, Standowt, CEVEW landing pages

---

## Related docs

- [PRICING_MODEL.md](./PRICING_MODEL.md) — deliverables + revision caps
- [PAID_CLIENT_OPERATIONS.md](./PAID_CLIENT_OPERATIONS.md) — fulfillment rules
- [ICP.md](./ICP.md) — who to pursue / decline
- [CUSTOMER_TERMS.md](./CUSTOMER_TERMS.md) — legal mirror
