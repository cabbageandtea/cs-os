"""Public marketing copy — conversion architecture, no internal strategy."""

from __future__ import annotations

from dataclasses import dataclass

from app.package_config import PACKAGES, REVISION_ROUND_DEFINITION, SCOPE_CREEP_EXAMPLES

# ── Hero: outcome + audience + single conversion path ──
HERO_HEADLINE = "Take it with you."
HERO_AUDIENCE = (
    "Students and career changers hunting software, data, and analytics roles."
)
HERO_LEAD = (
    "You already did the projects. We put them online, tighten the resume, "
    "and make GitHub and LinkedIn match. It all stays on your accounts."
)
HERO_CTA_PRIMARY = ("Start with Launch", "/checkout")
HERO_CTA_SECONDARY = ("Talk first", "/contact")

CREDIBILITY_STATS: tuple[dict[str, str], ...] = (
    {"value": "3", "label": "Packages, scope on the page"},
    {"value": "1", "label": "Brief to start the clock"},
    {"value": "100%", "label": "Your GitHub, your domain"},
)

SIGNAL_GAPS: tuple[dict[str, str], ...] = (
    {
        "title": "Work stays invisible",
        "body": "Class repos and half-finished tutorials don't show up when someone Googles you. You have to link and deploy them on purpose.",
    },
    {
        "title": "Platforms disagree",
        "body": "Your resume says one thing, GitHub another, LinkedIn a third. Hiring managers notice.",
    },
    {
        "title": "No time to fix it",
        "body": "Deploying, rewriting copy, and chasing revisions on top of classes or a job search is its own unpaid internship.",
    },
)

VALUE_BULLETS: tuple[str, ...] = (
    "Live portfolio on your GitHub",
    "One brief — we handle layout, copy, and deploy",
    "Resume and LinkedIn that match your target role (Launch & Accelerator)",
    "Revision rounds included, with clear limits upfront",
)

PROCESS_STEPS: tuple[dict[str, str], ...] = (
    {
        "step": "01",
        "title": "Pick a package",
        "body": "Foundation, Launch, or Accelerator. Pay once. Deliverables and turnaround are listed before Stripe.",
    },
    {
        "step": "02",
        "title": "Send your brief",
        "body": "Projects, links, target role, account checklist. Students: optional GitHub Education + .me setup on /start. We start when the form is complete.",
    },
    {
        "step": "03",
        "title": "Review and hand off",
        "body": "Site goes live. Resume and LinkedIn updated on Launch+. Use your included revision rounds, then keep everything in your accounts.",
    },
)

CASE_STUDY = {
    "kicker": "Launch delivery",
    "name": "Alex Rivera",
    "disclaimer": "",
    "role": "Data Analyst Intern",
    "package": "Launch",
    "example_slug": "alex-rivera",
    "mock_domain": "alexrivera.me",
    "example_url": "/example/alex-rivera",
    "outcome_metric": "40k+ rows · 2 shipped dashboards",
    "preview_tone": "data",
    "problem": "Solid coursework, nothing live when recruiters searched his name. Resume pointed at business analytics; LinkedIn still said 'seeking opportunities.'",
    "contribution": "Built alexrivera.me, rewrote the resume around dashboard work, and synced LinkedIn to data analyst targeting.",
    "outcome": "Same story on the site, PDF, and profile — ready to send to campus recruiting.",
    "deliverables": (
        ("Portfolio", "alexrivera.me"),
        ("Resume", "PDF, impact bullets"),
        ("LinkedIn", "Headline + summary updated"),
    ),
}

CASE_STUDY_STUDENT = {
    "kicker": "Launch delivery",
    "name": "Taylor Nguyen",
    "disclaimer": "",
    "role": "Software Engineer Intern",
    "package": "Launch",
    "example_slug": "taylor-nguyen",
    "mock_domain": "taylornguyen.me",
    "example_url": "/example/taylor-nguyen",
    "outcome_metric": "2 live apps · resume matches GitHub",
    "preview_tone": "rose",
    "problem": "GitHub was mostly forked tutorials. Resume listed languages, not projects. LinkedIn read like every other CS senior.",
    "contribution": "Shipped taylornguyen.me with two deployed capstones, rewrote the resume around those builds, and fixed LinkedIn to match.",
    "outcome": "Recruiters can click a demo, download a PDF, and see the same projects on GitHub.",
    "deliverables": (
        ("Portfolio", "taylornguyen.me"),
        ("Resume", "PDF, project-led"),
        ("LinkedIn", "Headline + about updated"),
    ),
}

CASE_STUDY_ACCELERATOR = {
    "kicker": "Accelerator delivery",
    "name": "Jordan Kim",
    "disclaimer": "",
    "role": "Junior Software Engineer",
    "package": "Accelerator",
    "example_slug": "jordan-kim",
    "mock_domain": "jordankim.me",
    "example_url": "/example/jordan-kim",
    "outcome_metric": "Bootcamp pivot · live API demo",
    "preview_tone": "coral",
    "problem": "Four years running a retail floor — good with process, weak online proof. GitHub was bootcamp homework; resume still sounded like a manager, not an engineer.",
    "contribution": "Reframed the pivot on jordankim.me, shipped ShiftSync with a live demo, rewrote the resume for junior SWE, and fixed LinkedIn for a career change.",
    "outcome": "Bootcamp grad story that holds up on the site, PDF, and profile — not just in the cover letter.",
    "deliverables": (
        ("Portfolio", "jordankim.me"),
        ("Resume", "PDF, pivot framing"),
        ("LinkedIn", "Headline + about for career change"),
        ("Strategy", "30-min strategy call"),
    ),
}

CASE_STUDIES: tuple[dict, ...] = (CASE_STUDY, CASE_STUDY_STUDENT, CASE_STUDY_ACCELERATOR)

SHOWCASE_LINKS: tuple[dict[str, str], ...] = (
    {"label": "Alex · data", "url": CASE_STUDY["example_url"], "domain": CASE_STUDY["mock_domain"]},
    {"label": "Taylor · SWE", "url": CASE_STUDY_STUDENT["example_url"], "domain": CASE_STUDY_STUDENT["mock_domain"]},
    {"label": "Jordan · pivot", "url": CASE_STUDY_ACCELERATOR["example_url"], "domain": CASE_STUDY_ACCELERATOR["mock_domain"]},
)

# Near primary CTA — reduces last-click friction (placement zone 3).
CTA_PROOF_LINE = (
    "Browse the full builds below before you pay — site, resume, GitHub, and LinkedIn where your tier includes them."
)

PORTFOLIO_SECTION_LABEL = "What we ship"
PORTFOLIO_SECTION_LEAD = (
    "Full sites you can click through now. Launch and Accelerator include resume and LinkedIn; Foundation is portfolio-only."
)

ME_DOMAIN_WHY = {
    "section_label": "Your URL",
    "headline": "Recruiters click one link. Make it yours.",
    "lead": (
        "A .me domain is easy to remember and looks like you meant it — "
        "not a class repo buried on GitHub Pages."
    ),
    "points": (
        {
            "title": "One link everywhere",
            "body": (
                "Same URL on your resume PDF, LinkedIn featured section, and applications. "
                "No explaining which repo or branch."
            ),
        },
        {
            "title": "Easier to remember",
            "body": (
                "alexrivera.me tells them who you are. yourname.github.io/capstone-fall-2025 "
                "makes them decode a path before they see your work."
            ),
        },
        {
            "title": "Looks like you ship",
            "body": (
                "Custom domain plus a live portfolio reads more serious than a default GitHub Pages URL."
            ),
        },
        {
            "title": "Students: often free",
            "body": (
                "GitHub Education and the Student Pack can include a free .me for a year. "
                "You claim it; we point DNS at your site at handoff."
            ),
        },
    ),
    "compare_weak": "yourname.github.io/portfolio-repo",
    "compare_strong": "yourname.me",
    "compare_strong_label": "Your domain",
    "footnote": (
        "github.io works for every package. .me is worth it when you want one link people actually remember "
        "— especially if you already qualify for the student offer."
    ),
    "cta_label": "Student setup guide",
    "cta_url": "/start",
}

PRINCIPLES: tuple[str, ...] = (
    "Not a design agency. Not a resume shop. We ship your portfolio and make the rest match.",
    "Same checklist every time — so you know what you're buying.",
    "When we're done, you own the repo, the domain, and the files.",
)

# Customer-facing contrast vs common alternatives (categories only — no competitor names on site).
MARKET_PITFALLS: tuple[dict[str, str], ...] = (
    {
        "title": "“Unlimited” revisions",
        "problem": (
            "Many resume services advertise unlimited edits, then contradict that in email — "
            "or cap you after a short window."
        ),
        "answer": (
            "Exact caps at checkout: Foundation 1, Launch 2, Accelerator 3 rounds. "
            "One message with all your feedback per round."
        ),
    },
    {
        "title": "PDF-only deliverables",
        "problem": (
            "Typical resume writers ($150–$600) return documents. Recruiters still cannot see "
            "deployed projects when they search your name."
        ),
        "answer": (
            "Every package includes a live portfolio on your GitHub or domain — not a PDF stuck in email."
        ),
    },
    {
        "title": "Three vendors, three stories",
        "problem": (
            "Separate resume writer, LinkedIn coach, and site builder rarely align copy, "
            "metrics, or target role."
        ),
        "answer": (
            "One brief, one team. Launch and Accelerator match portfolio, resume, and LinkedIn to the same role."
        ),
    },
    {
        "title": "Interview guarantees",
        "problem": (
            "Guaranteed interviews sound safe but set false expectations — hiring outcomes "
            "are not controllable by any vendor."
        ),
        "answer": (
            "We don't promise interviews. We promise the deliverables on the checkout page, "
            "honest revision limits, and clear scope — see /terms."
        ),
    },
    {
        "title": "Builder lock-in",
        "problem": (
            "Cheap portfolio tools ($19–$50) host on their subdomain. You do not own the repo, "
            "DNS, or deployment."
        ),
        "answer": (
            "GitHub, email, LinkedIn, and domain stay in your name. We build on your accounts and hand off."
        ),
    },
    {
        "title": "Scope discovered after payment",
        "problem": (
            "Hidden upsells, vague bundles (“5 resumes + mock interviews”), and unclear "
            "what is actually included."
        ),
        "answer": (
            "Checkout lists every included and excluded item before Stripe. Scope is fixed at purchase."
        ),
    },
)

COMPARISON_ROWS: tuple[dict[str, str], ...] = (
    {
        "factor": "Live portfolio deployed",
        "resume_writers": "Rarely — PDF/email",
        "diy_builders": "Template on their host",
        "doggybagg": "Yes — your GitHub / domain",
    },
    {
        "factor": "Resume + LinkedIn match",
        "resume_writers": "Often add-on tiers",
        "diy_builders": "Self-serve only",
        "doggybagg": "Launch & Accelerator",
    },
    {
        "factor": "Scope before you pay",
        "resume_writers": "Often vague until writer assigned",
        "diy_builders": "Feature list only",
        "doggybagg": "Full list at /checkout",
    },
    {
        "factor": "Revision policy",
        "resume_writers": "“Unlimited” or conflicting terms",
        "diy_builders": "N/A — DIY",
        "doggybagg": "1 / 2 / 3 explicit rounds",
    },
    {
        "factor": "You own accounts",
        "resume_writers": "N/A",
        "diy_builders": "Often platform lock-in",
        "doggybagg": "100% client-owned",
    },
    {
        "factor": "Preview before checkout",
        "resume_writers": "Sample PDFs",
        "diy_builders": "Theme previews",
        "doggybagg": "Alex, Taylor, Jordan — full site, resume, GitHub, LinkedIn",
    },
    {
        "factor": "Interview guarantee",
        "resume_writers": "Sometimes offered",
        "diy_builders": "None",
        "doggybagg": "None — deliverables only",
    },
)


@dataclass(frozen=True)
class PackageSalesInfo:
    slug: str
    display_name: str
    price_display: str
    who_for: str
    deliverables: tuple[str, ...]
    turnaround: str
    revision_rounds: int
    featured: bool = False
    preview_links: tuple[tuple[str, str], ...] = ()


_PACKAGE_PREVIEW_LINKS: dict[str, tuple[tuple[str, str], ...]] = {
    "launch": (
        ("Alex · data", CASE_STUDY["example_url"]),
        ("Taylor · SWE", CASE_STUDY_STUDENT["example_url"]),
    ),
    "accelerator": (("Jordan · career change", CASE_STUDY_ACCELERATOR["example_url"]),),
}

PACKAGE_SALES: dict[str, PackageSalesInfo] = {
    slug: PackageSalesInfo(
        slug=slug,
        display_name=pkg.display_name,
        price_display=f"${pkg.default_price_cents // 100}",
        who_for={
            "foundation": "You have projects but nothing live yet — students, bootcamp grads, career changers.",
            "launch": "You're actively applying — need site, resume, and LinkedIn to match.",
            "accelerator": "Competitive roles or a pivot — extra strategy and domain help.",
        }[slug],
        deliverables=pkg.deliverables,
        turnaround=pkg.turnaround_display,
        revision_rounds=pkg.revision_rounds,
        featured=(slug == "launch"),
        preview_links=_PACKAGE_PREVIEW_LINKS.get(slug, ()),
    )
    for slug, pkg in PACKAGES.items()
}

LANDING_FAQ = [
    (
        "Who is this for?",
        "Students, bootcamp grads, and career changers going after technical roles — anyone who needs "
        "a live portfolio plus a resume and LinkedIn that match (on Launch and up).",
    ),
    (
        "Why not build this myself?",
        "You can. Budget 20+ hours for deploy, writing, and making everything consistent. "
        "We run the same checklist every time so you don't have to.",
    ),
    (
        "Do I keep my accounts?",
        "Yes. GitHub, email, LinkedIn, and any domain stay in your name. We work inside your accounts.",
    ),
    (
        "What do I need before starting?",
        "GitHub, an email you check, and LinkedIn for Launch+. The form includes a short account checklist. "
        "Students: verify GitHub Education (.edu email) if you want help with a free .me — see /start.",
    ),
    (
        "Why does a .me domain matter?",
        "Recruiters skim fast. yourname.me is one link on your resume and LinkedIn that loads your portfolio — "
        "not a GitHub path they have to figure out. Students with GitHub Education can often claim a free .me; "
        "we connect it at handoff. github.io works too — .me just looks more finished.",
    ),
    (
        "I'm a student — anything special?",
        "Verify GitHub Education with your .edu email, then claim a free .me if you're eligible. "
        "See /start for the checklist. We handle DNS so yourname.me loads your portfolio — "
        "the same URL goes on your resume and LinkedIn.",
    ),
    (
        "How is this different from separate vendors?",
        "One team, one brief — not a designer, resume writer, and LinkedIn coach telling three different stories.",
    ),
    (
        "How is this different from resume writing services?",
        "Most resume writers send PDFs. We deploy a live portfolio on your GitHub, plus resume and LinkedIn on Launch+. "
        "Fixed revision caps, no interview guarantees, and you can browse sample sites before you pay.",
    ),
    (
        "Why no interview guarantee?",
        "Nobody can honestly guarantee interviews. Services that promise them lead to refund fights "
        "when hiring doesn't work out. We commit to the work on the page — not hiring outcomes.",
    ),
    (
        "Why not unlimited revisions?",
        "Unlimited usually means unlimited until it doesn't. Fixed rounds (1 / 2 / 3 by tier) keep things "
        "predictable for both of us. Extra work outside scope gets a written quote.",
    ),
    (
        "When does delivery start?",
        "After payment and a complete brief. Paying alone doesn't start the clock.",
    ),
    (
        "How many revisions are included?",
        "Foundation includes 1 revision round; Launch 2; Accelerator 3. "
        + REVISION_ROUND_DEFINITION
        + " Extra rounds or scope changes require a new purchase or written quote — see /terms.",
    ),
    (
        "What is not included?",
        "Job placement, guaranteed interviews, ongoing maintenance, application submission on your behalf, "
        "or work outside your package (e.g. resume on Foundation, strategy session on Launch). "
        "For instance: "
        + "; ".join(SCOPE_CREEP_EXAMPLES[:3])
        + ". Full list at checkout and in Terms §2 and §5.",
    ),
    (
        "Can I talk to someone before paying?",
        "Yes. Contact form — we reply within one business day.",
    ),
]

DEMO_JOURNEY_STEPS = [
    {"title": "Pick a package", "description": "Foundation, Launch, or Accelerator — scope and revision rounds listed at checkout."},
    {"title": "Pay and fill out the brief", "description": "Stripe checkout, then projects, links, target role, and account checklist."},
    {"title": "We build", "description": "Portfolio goes live on your GitHub. Resume and LinkedIn updated on Launch+."},
    {"title": "You review", "description": "Use your included revision rounds, then keep the logins and files."},
]

DEMO_EXAMPLE_CLIENT = {
    "name": "Alex Rivera",
    "target_role": "Data Analyst Intern",
    "package": "Launch",
    "pipeline_stage": "Delivered",
    "portfolio_url": "/example/alex-rivera",
    "deliverables": [
        ("Portfolio website", "/example/alex-rivera"),
        ("Resume (PDF)", "/example/alex-rivera/resume"),
        ("LinkedIn optimization notes", "Delivered"),
        ("Deployment URL", "alexrivera.me"),
    ],
}


def package_list_for_display() -> list[PackageSalesInfo]:
    return [PACKAGE_SALES[s] for s in ("foundation", "launch", "accelerator")]
