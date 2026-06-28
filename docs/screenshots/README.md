# Demo Screenshots

Place sales demo screenshots here. Filenames match `DEMO_WALKTHROUGH.md`.

## Required Captures

| File | Description |
|------|-------------|
| `01-dashboard-demo-clients.png` | Dashboard with `[DEMO]` clients |
| `02-intake-form.png` | Structured intake form |
| `03-analysis-stage-tasks.png` | Analysis stage client detail |
| `04-build-stage-deliverables.png` | Build stage client detail |
| `05-dashboard-build-wip.png` | Dashboard Build WIP (optional) |
| `06-qa-checklist-stage.png` | QA stage client detail |
| `07-review-stage.png` | Review stage client detail |
| `08-delivered-showcase-complete.png` | Delivered showcase — full completion |
| `09-status-history-rollback.png` | Status history with rollback entry |

## How to Capture

1. Run `python -m app.demo_seed` if demo clients are missing.
2. Start the app: `uvicorn app.main:app --reload`
3. Follow the screen list in [DEMO_WALKTHROUGH.md](../DEMO_WALKTHROUGH.md)
4. Save PNG files to this folder using the exact filenames above.

Screenshots will render automatically in the walkthrough once files exist.
