# CS-OS Demo Mode

Demo mode lets you run customer demonstrations using **fictional data only**, separate from your real client records.

---

## What Demo Mode Is

Demo mode is not a separate application build. It is:

1. **Seeded fictional clients** marked with the `[DEMO]` prefix
2. **Documentation** for repeatable sales walkthroughs (`DEMO_WALKTHROUGH.md`)
3. **Visual markers** in the UI (DEMO badge on dashboard, banner on client detail)

Your personal clients and demo clients live in the same database but are clearly distinguishable by name.

---

## Before Every Demo

### 1. Start the application

```bash
cd cs-os
.\.venv\Scripts\activate
uvicorn app.main:app --reload
```

Open: http://127.0.0.1:8000

### 2. Load or refresh demo data

First time or after a clean install:

```bash
python -m app.demo_seed
```

Reset demo clients to a known state (does **not** delete personal clients):

```bash
python -m app.demo_seed --force
```

### 3. Verify demo clients exist

On the dashboard, confirm you see six `[DEMO]` clients — one per pipeline stage. Each row shows a purple **DEMO** badge.

### 4. Open the showcase client

For a full end-to-end story, start at:

**`[DEMO] Taylor Nguyen (Showcase)`** — status: **Delivered**

This client has complete tasks, deliverables, status history, and a controlled rollback example in the audit log.

---

## Demo Client Roster

| Client | Pipeline Stage | Use In Demo For |
|--------|----------------|-----------------|
| `[DEMO] Alex Chen` | Intake | Showing structured intake and project creation |
| `[DEMO] Priya Sharma` | Analysis | Profile audit and template selection phase |
| `[DEMO] Marcus Webb` | Build | Active production / portfolio build |
| `[DEMO] Sofia Rivera` | QA | Internal quality review before client handoff |
| `[DEMO] Jordan Ellis` | Review | Client feedback and revision cycle |
| `[DEMO] Taylor Nguyen (Showcase)` | Delivered | Complete delivery + full audit trail |

All demo clients use:

- Fictional names and career backgrounds
- Placeholder URLs (`demo-csos-*`, `*.cs-os.example.com`)
- **No real GitHub or LinkedIn accounts**

---

## What Demo Mode Does Not Do

- No separate login or environment switch
- No automation or AI features
- No changes to workflow rules or pipeline enforcement
- No connection to external services

Demo mode is **data + documentation only**.

---

## Separating Demo from Production Use

| Practice | Recommendation |
|----------|----------------|
| Live demos | Use `[DEMO]` clients only |
| Real client work | Never prefix real clients with `[DEMO]` |
| Dashboard filter | Filter by stage to focus the story (e.g. `/?status=Build`) |
| After demo | Personal clients remain untouched; demo data is safe to re-seed |

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| No `[DEMO]` clients on dashboard | Run `python -m app.demo_seed` |
| Stale or corrupted demo history | Run `python -m app.demo_seed --force` |
| Server not loading | Confirm `uvicorn app.main:app --reload` and port 8000 is free |
| Mixed demo + real data on screen | Scroll to `[DEMO]` rows or filter by status |

---

## Related Documents

- **[DEMO_WALKTHROUGH.md](./DEMO_WALKTHROUGH.md)** — Step-by-step customer journey, talking points, screenshot checklist
- **[../EXECUTION.md](../EXECUTION.md)** — Internal business plan and MVP scope
- **[../README.md](../README.md)** — Developer quick start

---

## Demo Mode Checklist (Print This)

```
[ ] Server running at http://127.0.0.1:8000
[ ] Demo seed loaded (6 [DEMO] clients visible)
[ ] Showcase client opens without errors
[ ] DEMO_WALKTHROUGH.md reviewed
[ ] Screenshots captured (see docs/screenshots/README.md)
[ ] Personal client data not used in presentation
```
