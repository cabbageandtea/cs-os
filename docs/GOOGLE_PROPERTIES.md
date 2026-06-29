# Google & Ads — Property Update Guide (Liaison)

**Ops only.** Use this checklist to clean up legacy listings after the Doggybagg rebrand.

## Canonical values (paste everywhere)

| Field | Value |
|-------|--------|
| **Business / brand name** | Doggybagg |
| **Legal name** | DoggyBagg LLC |
| **Website** | https://doggybagg.cc |
| **Ops login URL** | https://doggybagg.cc/login |
| **Email** | hello@doggybagg.cc |
| **Tagline** | Take it with you |
| **Category** | Career consulting / professional services (closest allowed category) |
| **Service area** | United States (online service — no storefront) |
| **Description** | Live portfolio, resume, and LinkedIn for students and career changers entering technical roles. Fixed packages; clients keep their GitHub and domain. |
| **Jurisdiction** | Commonwealth of Pennsylvania, United States |

## Replace legacy values

| Old | New |
|-----|-----|
| Career Systems | Doggybagg |
| cs-os.onrender.com | https://doggybagg.cc |
| Personal Gmail on public surfaces | hello@doggybagg.cc |

## Property cleanup checklist

1. Search Console: add/verify `https://doggybagg.cc`, remove stale property labels.
2. Google Business Profile: update business name, website, category, service area.
3. Google Ads: update final URLs, site links, callouts, and conversion destination URLs.
4. Merchant/analytics surfaces: ensure brand and domain match canonical table above.
5. Remove any references to old domain/name in ad assets and extensions.

## Verification artifacts to store in ops docs

- Screenshot of Search Console verified property.
- Screenshot of updated Business Profile overview.
- Screenshot/export of Ads account final URL checks.
- Date + operator initials for each completed update.
| Indiana “Doggy Bagg LLC” (Mishawaka) | **Not us** — different company |

---

## DNS verification (Search Console)

**Domain property:** `doggybagg.cc`  
**TXT record (add at Namecheap → Advanced DNS):**

```
google-site-verification=QF1NCIfUKNA6le0TcCI4c5SlMHr_HsYp57dOZLYK_VY
```

| Field | Value |
|-------|--------|
| Type | TXT |
| Host | `@` |
| Value | (paste full string above) |
| TTL | Automatic |

After saving, wait 5–30 min (up to 24h), return to Search Console → **VERIFY**.

Then submit sitemap: `https://doggybagg.cc/sitemap.xml`

---

## Tour order (log in as you go)

### 1. Google Search Console — [search.google.com/search-console](https://search.google.com/search-console)

1. **Add property** → URL prefix: `https://doggybagg.cc`
2. Verify via **DNS TXT** (Namecheap) or HTML tag if already on site
3. **Sitemaps** → submit: `https://doggybagg.cc/sitemap.xml`
4. **Removals** (optional): request removal of `https://cs-os.onrender.com/*` if it was indexed
5. **Settings → Change of address** — only if you previously verified `cs-os.onrender.com` as primary; point to `doggybagg.cc`

### 2. Google Business Profile — [business.google.com](https://business.google.com)

1. Find existing profile OR **Add business**
2. Name: **Doggybagg** (not “Career Systems”)
3. Category: career / professional services
4. **Service business** — no public address (hide address; show service area)
5. Website: `https://doggybagg.cc`
6. Phone: optional — or use hello@ as primary contact
7. Hours: by appointment / online only
8. Description: use table above
9. **Delete duplicate** profiles for old names or wrong addresses

### 3. Google Ads — [ads.google.com](https://ads.google.com)

1. **Admin → Account settings** — account name: Doggybagg
2. **Business information** — website `doggybagg.cc`, email hello@
3. **Assets → Business name / logos** — upload `app/static/logo.png`
4. Update any **final URLs** from onrender.com → doggybagg.cc
5. Pause ads until checkout + showcase are ready if not already live

### 4. Google Analytics (if used) — [analytics.google.com](https://analytics.google.com)

1. Property name: Doggybagg
2. Website URL: `https://doggybagg.cc`
3. Data stream URL must match doggybagg.cc (not onrender)

### 5. Stripe (not Google, but same pass) — [dashboard.stripe.com/settings/branding](https://dashboard.stripe.com/settings/branding)

- Business name: **Doggybagg**
- Logo: `app/static/logo-icon.png`
- Color: `#ff6b4a`
- Or run: `python scripts/sync_stripe_branding.py`

### 6. Resend — [resend.com/domains](https://resend.com/domains)

- Domain **doggybagg.cc** → Verified
- From: `Doggybagg <hello@doggybagg.cc>`

---

## After updates

```powershell
python scripts/audit_site.py --base https://doggybagg.cc
.\scripts\run_e2e_prod.ps1
```

Search Google for: `site:doggybagg.cc` and `"cs-os.onrender.com"` — confirm only doggybagg.cc appears for your business.

---

## What the agent can do in browser

You log in; say **“I’m on Search Console”** (or whichever step). Agent reads the page and tells you exactly what to click and paste.

Agent **cannot** store passwords or complete 2FA for you.
