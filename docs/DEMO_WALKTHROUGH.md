# CS-OS Demo Walkthrough

**Duration:** 12–15 minutes  
**Audience:** Potential customers (students, career centers, early-career professionals, agency buyers)  
**Showcase client:** `[DEMO] Taylor Nguyen (Showcase)`

Use this script for repeatable sales demonstrations. Do not improvise the pipeline story — follow the journey below.

---

## Demo Flow Overview

```
Problem → Intake → Analysis → Build → QA → Delivery
```

| Journey Step | CS-OS Stage(s) | Demo Client |
|--------------|----------------|-------------|
| Problem | (context — no screen) | — |
| Intake | Intake | Alex Chen |
| Analysis | Analysis | Priya Sharma |
| Build | Build | Marcus Webb |
| QA | QA | Sofia Rivera |
| Delivery | Review + Delivered | Jordan Ellis → Taylor Nguyen (Showcase) |

---

## 1. Problem (2 min) — No Screen

**Goal:** Establish pain before showing the product.

### What to say

> Early-career candidates have skills and projects, but their proof is scattered — generic resumes, missing portfolios, unoptimized LinkedIn, inconsistent GitHub. Recruiters can't find a coherent story. CS-OS is the system that turns fragmented experience into a structured, recruiter-ready digital profile.

### Pain points to hit

- Resume is generic; no impact framing
- Portfolio missing or outdated
- LinkedIn and GitHub don't align with target role
- No visibility into delivery progress (for service providers)

### Transition

> Let me show you how CS-OS manages that delivery from first contact to handoff.

---

## 2. Intake (2 min) — Dashboard + Intake Form

**Open:** http://127.0.0.1:8000  
**Then:** `[DEMO] Alex Chen` or `/intake`

### Screenshot placeholder

![Dashboard with demo clients and WIP counts](screenshots/01-dashboard-demo-clients.png)

*Capture: Full dashboard showing six `[DEMO]` clients, stage counts, and DEMO badges.*

![Structured intake form](screenshots/02-intake-form.png)

*Capture: Intake form with Education, Projects, Work, and Skills fields.*

### What to show

- Dashboard WIP counts by stage (pipeline visibility at a glance)
- `[DEMO]` badge — fictional data, safe for demos
- Intake form: structured fields, not a free-text dump
- Client detail for Alex Chen: project created at **Intake**, initial tasks seeded

### Talking points

- "Every client starts with structured intake — role, experience blocks, skills."
- "Bad data is rejected at the door; we don't build on vague inputs."
- "One intake creates the client, project, tasks, and deliverables automatically."

---

## 3. Analysis (2 min) — Client Detail

**Open:** `[DEMO] Priya Sharma` — status: **Analysis**

### Screenshot placeholder

![Client detail at Analysis stage with tasks by stage](screenshots/03-analysis-stage-tasks.png)

*Capture: Pipeline bar on Analysis, done criteria visible, tasks grouped by stage.*

### What to show

- Pipeline position and **done criteria** for the current stage
- Tasks tied to **Analysis** stage (LinkedIn audit, GitHub audit, template selection)
- Movement policy: one stage forward or back — no skipping
- Status history log (prior transitions timestamped)

### Talking points

- "Analysis is where we audit profiles and pick the delivery template."
- "Tasks are bound to stages — no ambiguity about what belongs where."
- "Every status change is logged for operational analytics later."

---

## 4. Build (2 min) — Client Detail + Dashboard WIP

**Open:** `[DEMO] Marcus Webb` — status: **Build**  
**Optional:** Dashboard filtered to Build — `/?status=Build`

### Screenshot placeholder

![Build stage client with in-progress deliverables](screenshots/04-build-stage-deliverables.png)

*Capture: Marcus Webb at Build; portfolio/resume tasks in progress.*

![Dashboard Build WIP warning if 3+ in Build](screenshots/05-dashboard-build-wip.png)

*Capture: Dashboard stat row highlighting Build stage count (capture when WIP > 2 to show warning).*

### What to show

- Build-phase tasks (portfolio site, resume rewrite)
- Deliverables starting to move from pending → in progress
- Dashboard WIP visibility (how many clients are in Build right now)

### Talking points

- "Build is where production happens — portfolio and resume are the core outputs."
- "The dashboard shows bottlenecks before they become missed deadlines."
- "WIP warning on Build is visual only — you decide capacity, the system surfaces it."

---

## 5. QA (2 min) — Client Detail

**Open:** `[DEMO] Sofia Rivera` — status: **QA**

### Screenshot placeholder

![QA stage with deliverables in progress](screenshots/06-qa-checklist-stage.png)

*Capture: Sofia Rivera at QA; deliverables mostly in progress; QA task visible.*

### What to show

- QA done criteria (links verified, copy checked, deployment readiness)
- Deliverables nearing completion
- Tasks from earlier stages marked done; QA task active

### Talking points

- "Nothing ships without an internal QA gate."
- "Deliverables are tracked separately from tasks — you see assets, not just to-dos."
- "QA is the last internal checkpoint before the client sees anything."

---

## 6. Delivery (3 min) — Review + Delivered Showcase

**Open:** `[DEMO] Jordan Ellis` — status: **Review** (brief)  
**Then:** `[DEMO] Taylor Nguyen (Showcase)` — status: **Delivered**

### Screenshot placeholder

![Review stage with client revision task](screenshots/07-review-stage.png)

*Capture: Jordan Ellis at Review; client review task in progress.*

![Delivered showcase — complete delivery](screenshots/08-delivered-showcase-complete.png)

*Capture: Taylor Nguyen (Showcase) — all tasks done, all deliverables complete with URLs.*

![Full status history with rollback example](screenshots/09-status-history-rollback.png)

*Capture: Status history showing Intake through Delivered, including one controlled rollback.*

### What to show

- **Review:** client feedback loop before final handoff
- **Delivered (Showcase):**
  - All 9 tasks complete
  - All 4 deliverables complete (portfolio, resume, LinkedIn notes, deployment URL)
  - Full status history including a **rollback** at QA (controlled rework — Option B policy)
  - Fictional URLs on `*.cs-os.example.com` — not live production sites

### Talking points

- "Review is where the client sees work and requests revisions."
- "Delivered means deployed, handed off, and documented."
- "The audit log captures every transition — including rollbacks — for accountability."
- "This is the complete Career Systems delivery process in one view."

---

## Demo Talking Points (Quick Reference)

Use these when the prospect asks "why CS-OS?" or "how is this different?"

### Value proposition

1. **Not a website builder** — it's a career delivery operating system.
2. **Structured intake** — garbage in is blocked; every project starts clean.
3. **Enforced pipeline** — no skipped stages, no ambiguous state.
4. **Task-stage binding** — work is organized by delivery phase, not random lists.
5. **Audit trail** — every change timestamped for ops metrics and accountability.
6. **WIP visibility** — see bottlenecks on the dashboard before they cost you clients.

### Differentiators vs. spreadsheets / Notion

| Spreadsheet | CS-OS |
|-------------|-------|
| Manual status updates | Enforced linear pipeline |
| No audit trail | Full timestamp history |
| Tasks disconnected from stages | Tasks bound to pipeline stage |
| No intake validation | Structured, validated intake |
| No WIP view | Per-stage counts + Build warning |

### Objection handlers

| Objection | Response |
|-----------|----------|
| "We already use Notion." | "Notion stores notes. CS-OS enforces delivery law — stages, logs, and task binding." |
| "This looks simple." | "Correct. It's an internal ops system, not enterprise bloat. Simple enough to use daily." |
| "Can it automate GitHub deploy?" | "Not yet — manual-first by design. Automation comes after the process is proven." |
| "Is this multi-user?" | "Single-operator MVP. Built for you first, then scaled when client volume demands it." |

### Close

> CS-OS gives you one place to run every client from intake to delivery — with structure, visibility, and a record of every step. The demo data you saw is fictional; your real clients get the same system.

---

## Screenshot Capture Checklist

Save captures to `docs/screenshots/` using the filenames below.

| # | Filename | Screen |
|---|----------|--------|
| 1 | `01-dashboard-demo-clients.png` | Dashboard with all `[DEMO]` clients |
| 2 | `02-intake-form.png` | Intake form (structured fields) |
| 3 | `03-analysis-stage-tasks.png` | Priya Sharma — Analysis stage |
| 4 | `04-build-stage-deliverables.png` | Marcus Webb — Build stage |
| 5 | `05-dashboard-build-wip.png` | Dashboard Build WIP (optional warning) |
| 6 | `06-qa-checklist-stage.png` | Sofia Rivera — QA stage |
| 7 | `07-review-stage.png` | Jordan Ellis — Review stage |
| 8 | `08-delivered-showcase-complete.png` | Taylor Nguyen — Delivered, all complete |
| 9 | `09-status-history-rollback.png` | Showcase status history with rollback |

---

## Demo Script Timing

| Step | Minutes | Cumulative |
|------|---------|------------|
| Problem | 2 | 2 |
| Intake | 2 | 4 |
| Analysis | 2 | 6 |
| Build | 2 | 8 |
| QA | 2 | 10 |
| Delivery | 3 | 13 |
| Q&A buffer | 2 | 15 |

---

## Pre-Demo / Post-Demo

**Before:** See [DEMO_MODE.md](./DEMO_MODE.md) checklist.

**After demo:**

- Do not delete personal clients
- Optional: `python -m app.demo_seed --force` to reset demo state for next presentation
- Add captured screenshots to `docs/screenshots/` and verify they render in this file

---

## Related

- [DEMO_MODE.md](./DEMO_MODE.md) — Setup, seed commands, troubleshooting
- [../README.md](../README.md) — Application quick start
