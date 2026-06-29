# Doggybagg — voice & tone

Reference for all **public-facing** copy (landing, checkout, contact, examples, emails to clients). Ops/dashboard and legal pages follow different rules below.

## Voice (constant)

Who we always are:

| Dimension | Setting |
|-----------|---------|
| Serious ↔ Funny | Mostly serious; no jokes on money or guarantees |
| Formal ↔ Casual | Casual-direct — contractions OK, short sentences |
| Respectful ↔ Irreverent | Respectful; buyers are stressed |
| Enthusiastic ↔ Matter-of-fact | Matter-of-fact; specifics beat hype |

**One line:** Direct shop talk — we build your portfolio, you keep the accounts.

## Tone by context

| Zone | Tone | Goal |
|------|------|------|
| Hero, previews, pain, contact, CTA | **Human** | Sound like a person explaining the offer |
| Packages, compare, FAQ, `/demo`, `/start` | **Hybrid** | Warm lead + exact scope/revisions/timeline |
| Checkout header, post-payment pages, client email | **Hybrid** | Friendly; say **brief** not **intake** in UI |
| `/terms`, `/privacy`, form attestations | **Formal** | Unambiguous; keep defined terms (intake in legal OK) |
| Ops dashboard, `/intake` (ops), client detail | **Operational** | Internal product language |
| Portfolio examples (Alex, Taylor, Jordan) | **Character** | First-person, role-specific; not Doggybagg marketing |

## Word choices

| Prefer | Avoid on marketing pages |
|--------|--------------------------|
| brief, form | intake (customer UI) |
| your GitHub, your domain | infrastructure you own |
| match, same story | aligned, coherent narrative |
| we ship / we build | deliver, coordinate output |
| pick a tier | commit scope |
| Usually / Here | Common gap / Our standard |
| At a glance | Recruiter snapshot |

**Keep "intake"** in: URLs (`/intake/{token}`), terms, ops tools, code, and legal definitions.

## Patterns

**Human**
- "You already did the projects. We put them online."
- "Recruiters skim fast."
- "Pick a tier. That's the scope."

**Hybrid**
- Lead: plain English. Detail: numbers and lists.
- FAQ: yes/no first when possible, then 1–3 sentences.

**Formal**
- "We do not guarantee interviews or job offers."
- Revision rounds defined exactly; scope exclusions listed.

## Page map

```
Hero / #examples     → human
#why-me / #signal    → human
#why-us / #packages  → hybrid
#faq / #process      → hybrid
#cta                 → human
/checkout            → hybrid
/start               → hybrid (pre-purchase)
/intake/{token}      → hybrid UI, intake in submit button OK
/terms / /privacy    → formal
/example/*           → character voice
```

## AI tells (do not ship)

- Parallel triples every paragraph
- Arrow chains (`intake → deploy → handoff`)
- "Six-second scan", "professional presence as one system"
- "Before:" / "After:" case-study blocks
- "Single narrative across every surface"
- Consultant stats ("client-owned accounts", "intake triggers delivery")

## Edit checklist

1. Read aloud — LinkedIn carousel or friend explaining $199?
2. Right tone for the page zone (table above)?
3. Specifics (names, URLs, tier limits) instead of abstractions?
4. Legal precision unchanged on `/terms`?

Tests: `tests/test_public_content_firewall.py` includes `VOICE_BANNED_PHRASES` for regression.
