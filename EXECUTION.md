# Career Systems OS (CS-OS) — Execution Contract

## Success Criterion

**This system is successful if you can track 3 real clients end-to-end without confusion or missing data.**

---

## 1. Business Plan

### Working Name
**Career Systems OS (CS-OS)**

### Core Problem
Students, bootcamp grads, and career changers entering technical hiring fail to convert skills into interviews because:
- Resumes are generic
- Portfolios are inconsistent or non-existent
- LinkedIn is unoptimized
- No structured narrative across platforms

### Solution
A structured career positioning system that builds:
- Portfolio website (proof of work)
- Resume optimization (impact-based rewriting)
- LinkedIn alignment
- GitHub/profile cleanup
- Deployment + domain setup
- Career narrative consistency

### Value Proposition
> We convert fragmented experience into a structured, recruiter-ready digital profile that increases interview conversion rate.

### Offer Structure

| Tier | Price | Includes |
|------|-------|----------|
| Basic | $99 | Portfolio site, deployment + domain, GitHub integration |
| Standard | $199 | Basic + resume rewrite + LinkedIn optimization |
| Premium | $299–399 | Standard + career narrative alignment, 30-min strategy session, profile audit |

### Delivery Model
`Intake → Analysis → Build → QA → Review → Delivered`

Template-driven execution. SOP-based consistency. Manual-first (automation later).

### Key Metrics
- Time per client
- Revision count
- Lead → client conversion rate
- Delivery time
- Client satisfaction (1–5)
- Revenue per package

### Competitive Advantage
Not web design. Not resume writing. **Structured career system engineering** using repeatable workflows + AI-assisted production.

---

## 2. Execution Plan

### Phase 1 — Validate (0 → 5 clients)
1. Build your own portfolio using your SOP; record every step (time + friction)
2. Create minimal assets: intake form, 3 templates (Minimal / Data-Tech / Professional), tracking sheet
3. First beta client (1–2 max, discounted/free) — discover process failures, not profit

### Phase 2 — Standardize (5 → 10 clients)
1. Turn steps into SOP checklist
2. Create reusable prompt library
3. Reduce manual decision-making; standardize portfolio structure

### Phase 3 — Systematize (10+ clients)
1. Move tracking into structured database (this MVP)
2. Build internal dashboard (simple CRUD)
3. Begin measuring operational metrics from timestamp logs

### Phase 4 — Productize
1. Convert internal system into AgencyOS
2. Add automation (GitHub deploy, templates)
3. Expand services beyond portfolios

---

## 3. MVP Scope Lock

### Build Only
- Client intake form (simple schema)
- Project tracker (status pipeline)
- Portfolio generator workflow (manual steps, no automation)
- Basic database (SQLite for Phase 1)
- Minimal dashboard (list + status view)

### Hard Constraints
- No microservices, event systems, or auth (single-user)
- Manual-first workflow
- Every feature maps to a real delivery step
- 3 pages: Dashboard, Intake Form, Client Detail

### Core Entities
`Client` · `Project` · `Task` · `Deliverable` · `Status` · `TimestampLog`

### Pipeline Statuses
`Intake` → `Analysis` → `Build` → `QA` → `Review` → `Delivered`

---

## 4. Cursor Master Prompt (Locked)

```
You are building an MVP internal operations system called "Career Systems OS (CS-OS)".

IMPORTANT CONSTRAINTS:
- Do NOT over-engineer.
- No microservices.
- No authentication system.
- No multi-user architecture.
- Single-user system only.
- Manual-first workflow.
- Every feature must map to a real step in a career portfolio delivery process.
- If a feature is not required for Phase 1 validation, DO NOT BUILD IT.

GOAL:
Build a minimal internal system to manage client delivery for a career portfolio service.

CORE ENTITIES (MUST IMPLEMENT FIRST):
1. Client
2. Project
3. Task
4. Deliverable
5. Status (pipeline stage)
6. Timestamp logs (critical for analytics)

PIPELINE STATUSES:
- Intake, Analysis, Build, QA, Review, Delivered

MINIMUM FEATURES (MVP):
1. Dashboard: list clients, show project status, filter by status
2. Client detail: intake data, tasks, status history
3. Intake form: name, target role, experience summary, skills, LinkedIn/GitHub links
4. Database: relational mapping for all entities
5. Task tracking with timestamp on every status change

DATA LOGGING REQUIREMENT:
Every change must record: timestamp, entity changed, previous state, new state

UI: 3 pages max. Function > design.

TECH STACK:
- Backend: Python FastAPI
- Database: SQLite
- Frontend: Server-rendered Jinja2 templates

SUCCESS CRITERIA:
- Manage 3 real clients end-to-end
- See pipeline status at all times
- Log time and status changes without confusion
```

---

## 5. Immediate Next Actions

1. **Showcase client** — ops `/intake` on production; Launch package; deliver end-to-end (see `docs/SHOWCASE_CLIENT_WORKFLOW.md`)
2. **Clients #2–#3** — same wedge per `docs/ICP.md`; decline generic job-seekers outside technical entry
3. **Production polish** — set `RESEND_API_KEY` on Render for intake emails; swap Stripe test → live when ready for real payments
4. **Validate** — 3 real clients through `Delivered` without confusion (acceptance criterion above)
