# Acceptance checklist — paid deliverable gate

Run this before calling CS-OS "launch ready" or taking client money at scale.

## Automated (run every deploy)

```powershell
# Local
python scripts/verify_acceptance.py

# Production
$env:BASE_URL="https://cs-os.onrender.com"
python scripts/verify_acceptance.py
```

```powershell
# Full browser suite
.\scripts\run_e2e.ps1

# Production smoke only (no mutating ops tests)
npm run test:e2e:prod
```

**Pass bar:** score ≥ 80 (B). Email on production is optional until Resend is configured — expect 75–85 without it.

## Manual (once per milestone)

### Revenue loop
- [ ] Test card checkout → client on dashboard within 60s
- [ ] Intake link works (`/intake/{token}`)
- [ ] Intake submit → project moves to Analysis

### Showcase / comp path
- [ ] Ops `/intake` creates client without Stripe
- [ ] One real showcase delivered to **Delivered** with consent for public proof

### Delivery kit
- [ ] Client detail shows **Build kit** with `templates/portfolio/{slug}/`
- [ ] Portfolio deployed to client GitHub

### Go-live (when charging strangers)
- [ ] Live Stripe keys + live price IDs on Render
- [ ] `RESEND_API_KEY` + verified `EMAIL_FROM` domain
- [ ] `BASE_URL` matches production URL
- [ ] Custom domain (optional) + support inbox

## Grade rubric

| Score | Grade | Meaning |
|-------|-------|---------|
| 95+ | A | Launch-ready; real clients + email + live pay optional |
| 85–94 | B+ | Validation-ready; test Stripe OK |
| 80–84 | B | MVP acceptable; known gaps documented |
| &lt;80 | C or below | Do not take paying clients |

## CI

GitHub Actions runs `pytest`, Playwright, and `verify_acceptance.py` on every push to `master`.
