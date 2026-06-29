# Custom domain setup guide — {{CLIENT_NAME}}

**Desired domain:** _______________.me (or other TLD)  
**Portfolio host:** GitHub Pages / Render  
**Registrar:** (client-owned account — Namecheap, Google Domains, nc.me, etc.)

Client owns the domain and DNS. You provide these steps; they click approve.

---

## Option A — GitHub Pages + apex domain

1. Client registers domain at registrar (Student Pack .me if eligible).  
2. In GitHub repo → **Settings → Pages → Custom domain** → enter `yourname.me`.  
3. At registrar, set DNS:

| Type | Name | Value |
|------|------|-------|
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |
| CNAME | www | `<username>.github.io` |

4. Enable **Enforce HTTPS** in GitHub Pages settings.  
5. Wait up to 24h for DNS propagation.

---

## Option B — subdomain only (github.io)

No custom domain required. Primary URL:

`https://<username>.github.io/<repo>/`

Put this URL on resume and LinkedIn until domain is ready.

---

## Option C — Render custom domain

1. Render dashboard → service → **Settings → Custom Domains**.  
2. Add domain; copy Render’s CNAME target.  
3. Client adds CNAME at registrar.  
4. Verify HTTPS in Render.

---

## Student .me (GitHub Education)

1. Verify at [education.github.com](https://education.github.com/pack).  
2. Claim domain via [nc.me/github/auth](https://nc.me/github/auth) when eligible.  
3. Point DNS to GitHub Pages or Render per options above.

---

## Verification checklist

- [ ] Domain resolves to portfolio (not registrar parking page)
- [ ] HTTPS works
- [ ] Same URL on resume PDF and LinkedIn featured
- [ ] Client has registrar login saved (not shared with operator)

**Live URL (record on Deliverable):** https://

**Operator sign-off:** _______________ **Date:** _______________
