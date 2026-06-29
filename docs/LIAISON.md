# Liaison playbook — Doggybagg

You are the **human between clients and the system**. You do the work; the site handles money, scope, and paperwork.

## Your only recurring jobs

| When | You do | System handles |
|------|--------|----------------|
| Client asks about packages | Send them **https://doggybagg.cc/checkout** | Pricing, scope lists, Stripe |
| Client paid | **Nothing** — they land on the brief | Webhook + email with brief link |
| Client submitted brief | **Build** Analysis → Delivered in ops | Validation, template pick, pipeline |
| Client wants changes at Review | **One** feedback message per revision round | Caps shown on checkout (1 / 2 / 3) |
| Stripe/email looks wrong | One-time Dashboard fix (below) | Checkout branding per session |

## What clients see (you don't need to manage this)

- **Scope before pay** — included / not included on checkout and landing  
- **Examples** — Alex, Taylor, Jordan (Launch / Accelerator level work)  
- **No ops secrets** — template paths, delivery kits, and pipeline jargon stay in **/clients** (password)

If a client asks "how do you build it?" → *"Fixed scope for your tier; we work in your GitHub and hand off the live site."* Don't walk them through templates or internal steps.

## One-time setup (~10 minutes)

**Start here if you're lost:** [SETUP_SIMPLE.md](./SETUP_SIMPLE.md)

1. **Local stack** (from repo root):
   ```powershell
   .\scripts\start_local.ps1
   ```
2. **Stripe Dashboard (test mode)** → Settings → Business details:
   - Business name: **Doggybagg**
   - Logo: `app/static/logo-icon.png`
   - Brand color: `#ff6b4a`
3. **Webhook** — `start_local.ps1` writes `STRIPE_WEBHOOK_SECRET` to `.env`. Keep **stripe listen** open while testing pay.

## Operator access

- Local: http://127.0.0.1:8003/login  
- Production: https://doggybagg.cc/login  
- Password: `OPS_PASSWORD` in Render env (never share with clients)

## What you never need to do

- Manually create paid clients (webhook does it)
- Explain internal templates or file paths to clients
- Run pytest (hooks on save; `python -m pytest tests/` if something breaks)
- Worry about marketing copy drift — `tests/test_package_scope_chain.py` guards scope

## Escalation (ping a developer)

- Paid but no client on dashboard after 2 minutes → webhook / `stripe listen`
- Brief link invalid → re-issue from client detail
- Refund in Stripe → client archives automatically

## Success metric

**3 real clients** payment → brief → **Delivered**, zero "where is my data?" messages.

## Showcase (no charge)

First delivery in the technical-entry wedge: [SHOWCASE_CLIENT_WORKFLOW.md](./SHOWCASE_CLIENT_WORKFLOW.md)

## Ideal clients #2–#3

Same wedge as showcase: [ICP.md](./ICP.md)

Package truth chain: `EXECUTION.md` → `app/package_config.py` → checkout → Terms.
