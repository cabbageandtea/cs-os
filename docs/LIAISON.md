# Liaison playbook — Career Systems OS

You are the **human between clients and the system**. Everything else is automated or operator UI.

## Your only recurring jobs

| When | You do | System handles |
|------|--------|----------------|
| Client asks about packages | Send them your checkout URL | Pricing, Stripe Checkout, branding |
| Client paid | **Nothing** — auto-redirect to intake | Webhook + success page redirect |
| Client submitted intake | **Do the work** in Analysis → Delivered | Validation, template pick, pipeline at Analysis |
| Client wants changes at Review | Collect **one** feedback message, log in ops notes | Revision caps per package |
| Stripe/email looks wrong | One-time Dashboard fix (below) | Per-session Checkout branding |

## One-time setup (you, ~10 minutes)

**Start here if you're lost:** [SETUP_SIMPLE.md](./SETUP_SIMPLE.md)

1. **Start local stack** (from repo root):
   ```powershell
   .\scripts\start_local.ps1
   ```
2. **Stripe Dashboard (test mode)** → Settings → Business details:
   - Business name: **Career Systems**
   - Upload logo from `app/static/logo-icon.png`
   - Brand color: `#ff6b4a`
3. **Webhook secret** — `start_local.ps1` writes this to `.env` automatically. Keep the **stripe listen** window open while testing payments.

## Operator access

- URL: http://127.0.0.1:8003/login  
- Password: value of `OPS_PASSWORD` in `.env` (default `csos-local`)

## What you never need to do

- Manually create DB rows for paid clients (webhook does it)
- Edit intake validation rules per client (package rules are automatic)
- Run pytest (hooks run on save; run `pytest tests/ -v` only if something breaks)
- Deploy until you have 3 real clients tracked locally

## Escalation triggers (ping a developer)

- Payment succeeded but no client on dashboard after 2 minutes → webhook secret or `stripe listen` not running
- Intake link says invalid/expired → re-issue from client detail or support flow
- Refund in Stripe → client auto-archives; no action unless client disputes

## Success metric

**3 real clients** from payment → intake → delivered, with zero “where is my data?” messages.

See `EXECUTION.md` for full business scope.
