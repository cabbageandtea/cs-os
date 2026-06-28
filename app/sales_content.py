"""Public marketing copy — conversion architecture, no internal strategy."""

from __future__ import annotations

from dataclasses import dataclass

from app.package_config import PACKAGES, REVISION_ROUND_DEFINITION, SCOPE_CREEP_EXAMPLES

# ── Hero: outcome + audience + single conversion path ──
HERO_HEADLINE = "Take it with you."
HERO_AUDIENCE = (
    "Early-career and career changers entering technical hiring — "
    "software, data, analytics, and adjacent roles."
)
HERO_LEAD = (
    "We convert fragmented projects and experience into a live portfolio, aligned resume, "
    "and coherent professional presence — deployed on infrastructure you own."
)
HERO_CTA_PRIMARY = ("Start with Launch", "/checkout")
HERO_CTA_SECONDARY = ("Discuss fit first", "/contact")

CREDIBILITY_STATS: tuple[dict[str, str], ...] = (
    {"value": "3", "label": "Fixed-scope packages"},
    {"value": "1", "label": "Intake triggers delivery"},
    {"value": "100%", "label": "Client-owned accounts"},
)

SIGNAL_GAPS: tuple[dict[str, str], ...] = (
    {
        "title": "Work stays invisible",
        "body": "Repos and class projects rarely appear when someone searches your name — unless deployed and linked deliberately.",
    },
    {
        "title": "Platforms disagree",
        "body": "Resume, GitHub, and LinkedIn tell different stories. Recruiters notice the mismatch in seconds.",
    },
    {
        "title": "Execution competes with applications",
        "body": "Deployment, copy structure, and revision cycles are a second job on top of coursework or a career change.",
    },
)

VALUE_BULLETS: tuple[str, ...] = (
    "Live portfolio on your GitHub profile",
    "Structured intake — layout, copy architecture, deployment handled",
    "Resume and LinkedIn aligned to target role (Launch & Accelerator)",
    "Revision rounds included — scope defined before work starts",
)

PROCESS_STEPS: tuple[dict[str, str], ...] = (
    {
        "step": "01",
        "title": "Commit scope",
        "body": "Select Foundation, Launch, or Accelerator. One-time checkout locks deliverables and turnaround.",
    },
    {
        "step": "02",
        "title": "Submit intake",
        "body": "Projects, links, target role, account checklist. Students: optional GitHub Education + .me setup on /start. Clock starts when intake is complete.",
    },
    {
        "step": "03",
        "title": "Receive and revise",
        "body": "Portfolio live. Materials aligned. Included revision rounds, then full handoff on your accounts.",
    },
)

CASE_STUDY = {
    "kicker": "Illustrative delivery",
    "name": "Alex Rivera",
    "disclaimer": "",
    "role": "Data Analyst Intern",
    "package": "Launch",
    "example_slug": "alex-rivera",
    "mock_domain": "alexrivera.me",
    "example_url": "/example/alex-rivera",
    "outcome_metric": "40k+ rows · 2 shipped dashboards",
    "preview_tone": "data",
    "problem": "Strong coursework, no searchable portfolio. Resume and LinkedIn pointed at different roles.",
    "contribution": "Single intake → deployed portfolio, impact-based resume, LinkedIn aligned to data analyst positioning.",
    "outcome": "One narrative across GitHub, PDF, and profile — ready for technical recruiting.",
    "deliverables": (
        ("Portfolio", "alexrivera.me (demo)"),
        ("Resume", "Impact-structured PDF"),
        ("LinkedIn", "Headline + summary aligned"),
    ),
}

CASE_STUDY_CAREER_CHANGE = {
    "kicker": "Illustrative delivery",
    "name": "Jordan Kim",
    "disclaimer": "",
    "role": "Junior Software Engineer (career change)",
    "package": "Accelerator",
    "example_slug": "jordan-kim",
    "mock_domain": "jordankim.me",
    "example_url": "/example/jordan-kim",
    "outcome_metric": "2 deployed apps · pivot narrative aligned",
    "preview_tone": "code",
    "problem": "Bootcamp projects on GitHub, but resume still read like prior field. No pivot story recruiters could scan.",
    "contribution": "Intake → deployed portfolio, resume rewritten for SWE targeting, LinkedIn and narrative aligned to the pivot.",
    "outcome": "One technical story across GitHub, PDF, and profile — credible for entry-level SWE screens.",
    "deliverables": (
        ("Portfolio", "jordankim.me (demo)"),
        ("Resume", "Pivot-focused PDF"),
        ("LinkedIn", "Headline + about aligned to SWE"),
    ),
}

CASE_STUDIES: tuple[dict, ...] = (CASE_STUDY, CASE_STUDY_CAREER_CHANGE)

# Near primary CTA — reduces last-click friction (placement zone 3).
CTA_PROOF_LINE = (
    "See a full Launch delivery before checkout — portfolio, resume, GitHub, and LinkedIn samples."
)

ME_DOMAIN_WHY = {
    "section_label": "Your URL",
    "headline": "Recruiters click one link. Make it yours.",
    "lead": (
        "A personal .me domain is the shortest path from your resume to proof-of-work. "
        "It reads as intentional — not a class repo buried on GitHub Pages."
    ),
    "points": (
        {
            "title": "One link everywhere",
            "body": (
                "Same URL on resume PDF, LinkedIn featured section, email signature, and applications. "
                "No explaining which repo or which branch."
            ),
        },
        {
            "title": "Passes the six-second scan",
            "body": (
                "alexrivera.me is instant context. yourname.github.io/capstone-fall-2025 "
                "forces a recruiter to decode paths before they see your work."
            ),
        },
        {
            "title": "Signals you ship for hiring",
            "body": (
                ".me literally means “about me” — built for personal brands. "
                "Custom domain + live portfolio reads as more serious than a default host URL."
            ),
        },
        {
            "title": "Students: often free",
            "body": (
                "GitHub Education + the Student Pack can include a free .me for a year. "
                "You claim it; we wire DNS to your deployed portfolio at handoff."
            ),
        },
    ),
    "compare_weak": "yourname.github.io/portfolio-repo",
    "compare_strong": "yourname.me",
    "footnote": (
        "github.io works for every package. .me is the upgrade when you want one memorable link "
        "— especially if you already qualify for the student offer."
    ),
    "cta_label": "Student setup guide",
    "cta_url": "/start",
}

PRINCIPLES: tuple[str, ...] = (
    "Not web design. Not resume writing alone. Structured career system delivery.",
    "Template-driven execution with defined SOPs — consistency over improvisation.",
    "You own every account, URL, and file at handoff.",
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
            "One consolidated feedback message per round."
        ),
    },
    {
        "title": "PDF-only deliverables",
        "problem": (
            "Typical resume writers ($150–$600) return documents. Recruiters still cannot see "
            "deployed projects when they search your name."
        ),
        "answer": (
            "Every package ships a live portfolio on infrastructure you own — not a file trapped in email."
        ),
    },
    {
        "title": "Three vendors, three stories",
        "problem": (
            "Separate resume writer, LinkedIn coach, and site builder rarely align copy, "
            "metrics, or target role."
        ),
        "answer": (
            "One intake, one pipeline. Launch and Accelerator align portfolio, resume, and LinkedIn to one role."
        ),
    },
    {
        "title": "Interview guarantees",
        "problem": (
            "Guaranteed interviews sound safe but set false expectations — hiring outcomes "
            "are not controllable by any vendor."
        ),
        "answer": (
            "We do not guarantee interviews or offers. We guarantee defined deliverables, "
            "fixed scope, and honest revision limits — see /terms."
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
        "factor": "Resume + LinkedIn aligned",
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
        "factor": "See example delivery first",
        "resume_writers": "Generic samples",
        "diy_builders": "Blank templates",
        "doggybagg": "Full mock delivery on site",
    },
    {
        "factor": "Interview guarantee",
        "resume_writers": "Common — high dispute risk",
        "diy_builders": "None",
        "doggybagg": "None — honest scope",
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


PACKAGE_SALES: dict[str, PackageSalesInfo] = {
    slug: PackageSalesInfo(
        slug=slug,
        display_name=pkg.display_name,
        price_display=f"${pkg.default_price_cents // 100}",
        who_for={
            "foundation": "Proof-of-work online — students, bootcamp grads, and changers with projects but no live site.",
            "launch": "Active search — portfolio, resume, and LinkedIn operating as one system.",
            "accelerator": "Competitive roles and pivots — narrative strategy and premium support.",
        }[slug],
        deliverables=pkg.deliverables,
        turnaround=pkg.turnaround_display,
        revision_rounds=pkg.revision_rounds,
        featured=(slug == "launch"),
    )
    for slug, pkg in PACKAGES.items()
}

LANDING_FAQ = [
    (
        "Who is this for?",
        "Early-career candidates and career changers targeting technical roles — students, bootcamp grads, "
        "and anyone who needs proof-of-work online plus aligned resume and LinkedIn.",
    ),
    (
        "Why not build this myself?",
        "You can — budget 20+ hours for setup, writing, and cross-platform consistency. "
        "We run a defined pipeline: one intake, coordinated output.",
    ),
    (
        "Do I keep my accounts?",
        "Yes. GitHub, email, LinkedIn, and any domain remain in your name. We build on your infrastructure.",
    ),
    (
        "What do I need before starting?",
        "GitHub, email you check, and LinkedIn for Launch+. Intake includes a short account checklist. "
        "Students: verify GitHub Education (school .edu email) for optional free .me domain setup — see /start.",
    ),
    (
        "Why does a .me domain matter?",
        "Recruiters decide in seconds. yourname.me is one memorable link on your resume, LinkedIn, "
        "and applications — it loads your portfolio, not a GitHub path they have to decode. "
        "Students with GitHub Education can often claim a free .me; we connect it to your site at handoff. "
        "Not required — github.io works — but .me is the difference between “I have projects” and "
        "“I have a professional presence.”",
    ),
    (
        "I'm a student — anything special?",
        "Verify GitHub Education with your .edu email, then claim a free .me if eligible. "
        "See /start for the checklist. We handle DNS so your portfolio loads at yourname.me — "
        "the same URL we put on your resume and LinkedIn.",
    ),
    (
        "How is this different from separate vendors?",
        "One delivery pipeline — not a designer, a resume writer, and a LinkedIn coach telling three stories.",
    ),
    (
        "How is this different from resume writing services?",
        "Most resume writers deliver PDFs and optional LinkedIn guides — not a live portfolio on your GitHub. "
        "We coordinate deploy + resume + LinkedIn (Launch+) with fixed revision caps, no interview guarantees, "
        "and examples you can click through before checkout.",
    ),
    (
        "Why no interview guarantee?",
        "No ethical vendor can guarantee interviews. Services that promise them often create refund disputes "
        "when outcomes do not materialize. We commit to defined deliverables, published revision limits, "
        "and transparent scope — not hiring outcomes.",
    ),
    (
        "Why not unlimited revisions?",
        "Unlimited policies rarely survive contact with reality — they either get capped quietly or "
        "encourage endless scope creep. Fixed rounds (1 / 2 / 3 by tier) keep delivery predictable for "
        "you and sustainable for us. Extra work outside scope is quoted separately.",
    ),
    (
        "When does delivery start?",
        "After payment and complete intake. Payment alone does not start the clock.",
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
        "Examples: "
        + "; ".join(SCOPE_CREEP_EXAMPLES[:3])
        + ". Full list at checkout and in Terms §2 and §5.",
    ),
    (
        "Can I talk to someone before paying?",
        "Yes. Contact form — we reply within one business day.",
    ),
]

DEMO_JOURNEY_STEPS = [
    {"title": "Choose Launch", "description": "Alex selects Launch before graduation recruiting season."},
    {"title": "Pay & intake", "description": "Checkout → intake with projects, links, and target role."},
    {"title": "Delivery", "description": "Portfolio live. Resume and LinkedIn aligned to data analyst positioning."},
    {"title": "Review & handoff", "description": "Revision rounds included. URLs and files in Alex's accounts."},
]

DEMO_EXAMPLE_CLIENT = {
    "name": "Alex Rivera (Example)",
    "target_role": "Data Analyst Intern",
    "package": "Launch",
    "pipeline_stage": "Delivered",
    "portfolio_url": "/example/alex-rivera",
    "deliverables": [
        ("Portfolio website", "/example/alex-rivera"),
        ("Resume (PDF)", "/example/alex-rivera/resume"),
        ("LinkedIn optimization notes", "Delivered"),
        ("Deployment URL", "alexrivera.me (demo)"),
    ],
}


def package_list_for_display() -> list[PackageSalesInfo]:
    return [PACKAGE_SALES[s] for s in ("foundation", "launch", "accelerator")]
