# Showcase client workflow (comp — no payment)

Use this for **Client #1** (e.g. first real showcase in the technical-entry wedge) when you are **not** running Stripe checkout.

**ICP fit:** Students, new grads, bootcamp grads, or career changers targeting **technical roles** (SWE, data, analytics). See [ICP.md](./ICP.md).

**Production ops:** https://cs-os.onrender.com/login

---

## What automates vs what you do

| Step | Automates? | Who |
|------|------------|-----|
| GitHub / Gmail / LinkedIn accounts | No | Client |
| GitHub Education + free `.me` (optional) | No | Client — student perk path only |
| Client + project created | **Yes** (on intake submit) | You (ops `/intake`) |
| Intake field validation | **Yes** | System |
| Pipeline **Intake → Analysis** | **Yes** (after valid intake) | System |
| Default tasks + template seed | **Yes** | System |
| Portfolio build + deploy | No | You |
| Resume PDF + LinkedIn notes | No | You |
| **Analysis → Build → QA → Review → Delivered** | No | You (dashboard buttons) |
| Custom domain DNS → GitHub Pages | No | You + client |
| Intake reminder emails | N/A | No payment = no post-pay email path |
| Public homepage case study | No | You (only with client consent) |

**Bottom line:** External signups (GitHub, Namecheap) do **not** create a CS-OS record. The client appears on your dashboard only after **ops `/intake`** (or a completed token intake link).

---

## Phase 0 — Before CS-OS (client, ~30–45 min)

Checklist — do **before** you open `/intake`:

- [ ] [GitHub account](https://github.com/signup)
- [ ] [Gmail](https://accounts.google.com/signup) (if needed)
- [ ] [LinkedIn](https://www.linkedin.com/signup) profile started (Launch tier)
- [ ] **Target role** defined (e.g. “Software Engineer Intern”, “Junior Data Analyst”)
- [ ] **2+ projects** ready to describe (coursework, bootcamp, job-adjacent work)
- [ ] *Optional (students):* [GitHub Education](https://education.github.com/pack) + free [`.me` domain](https://nc.me/github/auth)

Optional ops note: `Showcase — comp, Launch tier, technical-entry wedge`

---

## Phase 1 — Create client in CS-OS (you, ~15 min)

1. Log in → **+ New Client** (`/intake`)
2. Package: **Launch** (recommended showcase)
3. Fill all intake fields with **real** data (not `[DEMO]` placeholders)
4. Check prerequisite + attestation boxes
5. Submit

**System then:**

- Creates client + project
- Sets intake **complete**
- Moves pipeline to **Analysis**
- Seeds tasks from package + template choice

Verify on dashboard: real name (no `[DEMO]` badge).

---

## Phase 2 — Delivery (you)

Work the dashboard in order. One stage at a time.

| Stage | Your work |
|-------|-----------|
| **Analysis** | Pick template (`minimal`, `data-tech`, or `professional` for Launch+), audit LinkedIn/GitHub |
| **Build** | Portfolio repo on **client's** GitHub, resume draft, LinkedIn alignment doc |
| **QA** | Mobile check, links, spelling, content firewall (no internal ops on public site) |
| **Review** | Client approves in one feedback round (log in ops notes) |
| **Delivered** | Paste live portfolio URL + resume link on client record |

Deploy target: **GitHub Pages** on their repo. Optional: custom `.me` via Namecheap DNS → GitHub Pages custom domain.

---

## Phase 3 — Domain hookup (optional, ~20 min)

After portfolio repo exists:

1. GitHub repo → **Settings → Pages** → Custom domain
2. Registrar DNS per GitHub docs (`A` or `CNAME`)
3. Enable HTTPS in GitHub Pages
4. Update deliverable URL on dashboard

---

## Phase 4 — Public proof (optional, with consent)

Only if the client agrees:

- [ ] First name + role + live URL on landing case study (replace fictional example)
- [ ] No school email, full resume, or private details on public site

---

## Quick reference

```
Client accounts (GitHub, LinkedIn; optional Edu + .me)
        ↓  manual
You: /intake (Launch)  →  auto: Analysis
        ↓  manual
You: Build → QA → Review → Delivered
        ↓  optional
DNS: custom domain → GitHub Pages
        ↓  optional + consent
Homepage case study
```

---

## Paid clients vs showcase

| | Paid client | Showcase (comp) |
|--|-------------|-----------------|
| Entry | `/checkout` → Stripe | Ops `/intake` |
| Payment | Required | Skip |
| Intake | Token link after pay | Ops form (fastest) |
| Email | Intake reminder (if Resend configured) | None unless token link issued |

---

See also: [ICP.md](./ICP.md) · [LIAISON.md](./LIAISON.md) · [SETUP_SIMPLE.md](./SETUP_SIMPLE.md) · `/start`
