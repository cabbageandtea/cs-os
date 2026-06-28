# Placement best practices — Career Systems

**OPS + build reference.** Applies to the public landing (`/`) and fictional portfolio mocks (`/example/*`).

Sources synthesized: portfolio conversion guides (2025–2026), B2B landing social-proof placement research, UX playbook homepage patterns.

---

## The 6-second rule (portfolio mocks)

Within one scroll, a visitor must know:

1. **Who** — name + target role  
2. **What** — one-line value prop (outcome, not “welcome to my portfolio”)  
3. **Proof** — strongest project or metric  
4. **Next action** — one primary CTA  

If a non-designer friend cannot answer those four, rewrite the hero.

---

## Three placement zones (Career Systems landing)

| Zone | Where | Job | Our implementation |
|------|--------|-----|-------------------|
| **1 — Credibility** | First scroll after hero | “This is real deliverable quality” | `Live examples` preview cards → `/example/*` |
| **2 — Validation** | Mid-page, near offer | “Peers like me got this outcome” | Proof case studies + metrics before packages |
| **3 — Decision** | Adjacent to checkout CTA | Remove last-click anxiety | `cta_proof_line` + link above final button; Launch card links to Alex mock |

**Do not** bury proof only at the bottom. Footer proof is invisible to most buyers.

---

## Landing page order (locked)

```
Hero (one primary CTA: Launch)
  → Live example preview (2 mock .me cards)
  → Problem (signal gaps)
  → Proof detail (problem / delivery / outcome)
  → Packages (Launch = recommended + example link)
  → Process
  → Position / FAQ
  → Final CTA + proof line
```

---

## Portfolio mock structure (per client)

| Section | Placement | Content |
|---------|-----------|---------|
| Chrome | Top | Fake `.me` URL + “Demo” badge — never hide that it’s fictional |
| Nav | Sticky | 4–5 links max: Work, About, Skills, Contact |
| Hero | Above fold | Role eyebrow, name, **one** primary CTA, optional secondary |
| Stats | Under hero | 2–3 quantified bullets (rows analyzed, projects shipped) |
| Projects | First content block | 2 featured cards max; outcome line on each |
| Skills | After projects | Pills, scannable |
| Contact | Last | Email + LinkedIn; repeated CTA |

### Project card formula

1. **Visual** — gradient or screenshot placeholder (16:9)  
2. **Title** — role-oriented, not “Project 1”  
3. **Stack** — mono tags  
4. **Outcome** — bordered callout with measurable result  
5. **Actions** — primary (code/demo) + secondary (details)

### CTAs on mocks

- **One primary** per viewport (e.g. “View my work”)  
- Secondary: Resume, GitHub — never three equal-weight primaries  

---

## Package ↔ template placement

| Package | Template | Mock persona |
|---------|----------|--------------|
| Foundation | minimal / data-tech | Lighter hero, 2 projects |
| Launch | data-tech + resume | Alex Rivera |
| Accelerator | data-tech dark + narrative | Jordan Kim |

---

## What to avoid

- Generic hero (“Welcome to my portfolio”)  
- Proof only in footer  
- More than 5 projects on a student site  
- Slow reveal / typewriter animations on name  
- Fake `.me` URLs that 404 — always host mocks on `/example/*`  
- Two equal-weight hero CTAs on **client** portfolios (fine on **your** sales page: Launch primary + Discuss fit ghost)

---

## When showcase client is real

Replace or supplement Alex/Jordan card with **consent + real URL**. Keep one fictional card for the other wedge persona until you have two real deliveries.

---

## Checklist before calling a mock “done”

- [ ] 6-second test with someone outside the project  
- [ ] Primary CTA visible without scrolling on mobile  
- [ ] Outcome metric on landing card + case study  
- [ ] Example link on Launch package row  
- [ ] Proof line above final checkout CTA  
- [ ] Lighthouse: avoid layout shift on project visuals (`aspect-ratio` set)
