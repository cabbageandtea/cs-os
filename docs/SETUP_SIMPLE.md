# Setup — plain English

You only do this **once**. After that, run one command when you sit down to work.

---

## Every time you work (30 seconds)

1. Open **PowerShell** in the project folder (`cs-os`)
2. Run:

```powershell
.\scripts\start_local.ps1
```

3. Two new windows appear — **leave them open**
4. Open http://127.0.0.1:8003/login  
   Password: `csos-local` (unless you changed `OPS_PASSWORD` in `.env`)

That’s it for daily use.

---

## What those two windows are

| Window | What it does |
|--------|----------------|
| **uvicorn** | Your app (dashboard, checkout, intake) |
| **stripe listen** | Tells Stripe “when someone pays, notify my laptop” |

If you close either window, payments won’t create clients on your dashboard.

---

## One-time Stripe Dashboard (optional polish)

Only if checkout still says “doggybagg” or old branding:

1. Go to https://dashboard.stripe.com/test/settings/branding  
2. Business name: **Doggybagg**  
3. Logo: upload `app/static/logo-icon.png` from this project  
4. Accent color: `#ff6b4a`

You do **not** need to paste `whsec_...` manually anymore — `start_local.ps1` writes it to `.env` for you.

---

## Your job as liaison (after setup)

1. Share checkout URL with paying clients (`/checkout`)
2. Comp showcase / referral — **ops** `/intake` (no Stripe); see [SHOWCASE_CLIENT_WORKFLOW.md](./SHOWCASE_CLIENT_WORKFLOW.md)
3. After paid checkout — intake opens automatically
4. After intake submit — **do the delivery work** on the dashboard

Details: [LIAISON.md](./LIAISON.md) · [ICP.md](./ICP.md)

---

## Something broken?

| Problem | Fix |
|---------|-----|
| “Can’t reach page” | Run `.\scripts\start_local.ps1` again |
| Paid but no client on dashboard | Make sure the **stripe listen** window is still open |
| Login fails | Use password from `.env` → `OPS_PASSWORD` |
| Checkout error | Check `.env` has `STRIPE_SECRET_KEY` and price IDs set |
