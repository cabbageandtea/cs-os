# Career Systems OS (CS-OS)

Minimal internal operations system for career portfolio client delivery.

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

## Stripe Test Mode (Phase 4A)

Copy `.env.example` to `.env` and fill in Stripe test keys and Price IDs.

```bash
stripe listen --forward-to localhost:8000/webhooks/stripe
```

| Route | Purpose |
|-------|---------|
| `/checkout` | Package selection → Stripe Checkout |
| `/purchase/success` | Post-payment intake link (polls webhook) |
| `/intake/{token}` | Paid customer intake form |
| `/webhooks/stripe` | Stripe webhook endpoint |

Run Phase 4A tests:

Set `OPS_PASSWORD` in `.env` before using operator routes (`/dashboard`, `/clients/*`, `/intake`).

```bash
pytest tests/ -v
```

## Sales Demo Environment

**Documentation:** [docs/DEMO_MODE.md](docs/DEMO_MODE.md) · [docs/DEMO_WALKTHROUGH.md](docs/DEMO_WALKTHROUGH.md) · [docs/AUTOMATION_ARCHITECTURE.md](docs/AUTOMATION_ARCHITECTURE.md) · [docs/PHASE_4A_STRIPE_IMPLEMENTATION_PLAN.md](docs/PHASE_4A_STRIPE_IMPLEMENTATION_PLAN.md) · [docs/PRICING_MODEL.md](docs/PRICING_MODEL.md) · [docs/PAID_CLIENT_OPERATIONS.md](docs/PAID_CLIENT_OPERATIONS.md) · [docs/CUSTOMER_TERMS.md](docs/CUSTOMER_TERMS.md) *(customer-facing)*

Load fictional demo clients across the full pipeline (separate from your personal data):

```bash
python -m app.demo_seed
```

This creates 6 clearly marked `[DEMO]` clients — one per pipeline stage. Open **`[DEMO] Taylor Nguyen (Showcase)`** for a completed delivery with full status history, tasks, and deliverables.

Re-seed from scratch:

```bash
python -m app.demo_seed --force
```

## Pages

| Route | Purpose |
|-------|---------|
| `/` | Public landing page — packages, FAQ, CTA |
| `/demo` | Example customer journey (fictional) |
| `/contact` | Lead capture form |
| `/dashboard` | Operations dashboard — delivery + lead pipeline |
| `/intake` | New client intake form (operator) |
| `/clients/{id}` | Client detail — pipeline, tasks, deliverables, history |
| `/checkout` | Paid package checkout (Stripe) |

## Acceptance Test

Track 3 real clients end-to-end without confusion or missing data.

See `EXECUTION.md` for business plan, phase plan, and locked Cursor prompt.
