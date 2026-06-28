"""Public marketing copy — conversion architecture, no internal strategy."""

from __future__ import annotations

from dataclasses import dataclass

from app.package_config import PACKAGES

# ── Hero: outcome + audience + single conversion path ──
HERO_HEADLINE = "Career signal engineered as one system."
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
        "body": "Projects, links, target role, account checklist. The delivery clock starts when intake is complete.",
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
    "disclaimer": "Fictional example — not a real client.",
    "role": "Data Analyst Intern",
    "package": "Launch",
    "problem": "Strong coursework, no searchable portfolio. Resume and LinkedIn pointed at different roles.",
    "contribution": "Single intake → deployed portfolio, impact-based resume, LinkedIn aligned to data analyst positioning.",
    "outcome": "One narrative across GitHub, PDF, and profile — ready for technical recruiting.",
    "deliverables": (
        ("Portfolio", "alexrivera.github.io"),
        ("Resume", "Impact-structured PDF"),
        ("LinkedIn", "Headline + summary aligned"),
    ),
}

CASE_STUDY_CAREER_CHANGE = {
    "kicker": "Illustrative delivery",
    "name": "Jordan Kim",
    "disclaimer": "Fictional example — not a real client.",
    "role": "Junior Software Engineer (career change)",
    "package": "Accelerator",
    "problem": "Bootcamp projects on GitHub, but resume still read like prior field. No pivot story recruiters could scan.",
    "contribution": "Intake → deployed portfolio, resume rewritten for SWE targeting, LinkedIn and narrative aligned to the pivot.",
    "outcome": "One technical story across GitHub, PDF, and profile — credible for entry-level SWE screens.",
    "deliverables": (
        ("Portfolio", "jordankim.github.io"),
        ("Resume", "Pivot-focused PDF"),
        ("LinkedIn", "Headline + about aligned to SWE"),
    ),
}

CASE_STUDIES: tuple[dict, ...] = (CASE_STUDY, CASE_STUDY_CAREER_CHANGE)

PRINCIPLES: tuple[str, ...] = (
    "Not web design. Not resume writing alone. Structured career system delivery.",
    "Template-driven execution with defined SOPs — consistency over improvisation.",
    "You own every account, URL, and file at handoff.",
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
    "foundation": PackageSalesInfo(
        slug="foundation",
        display_name="Foundation",
        price_display="$99",
        who_for="Proof-of-work online — students, bootcamp grads, and changers with projects but no live site.",
        deliverables=PACKAGES["foundation"].deliverables,
        turnaround="5–10 business days after intake",
        revision_rounds=1,
    ),
    "launch": PackageSalesInfo(
        slug="launch",
        display_name="Launch",
        price_display="$199",
        who_for="Active search — portfolio, resume, and LinkedIn operating as one system.",
        deliverables=PACKAGES["launch"].deliverables,
        turnaround="7–14 business days after intake",
        revision_rounds=2,
        featured=True,
    ),
    "accelerator": PackageSalesInfo(
        slug="accelerator",
        display_name="Accelerator",
        price_display="$349",
        who_for="Competitive roles and pivots — narrative strategy and premium support.",
        deliverables=PACKAGES["accelerator"].deliverables,
        turnaround="10–21 business days after intake",
        revision_rounds=3,
    ),
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
        "GitHub, email you check, and LinkedIn for Launch+. Intake includes a short account checklist.",
    ),
    (
        "How is this different from separate vendors?",
        "One delivery pipeline — not a designer, a resume writer, and a LinkedIn coach telling three stories.",
    ),
    (
        "When does delivery start?",
        "After payment and complete intake. Payment alone does not start the clock.",
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
    "deliverables": [
        ("Portfolio website", "https://alexrivera.github.io"),
        ("Resume (PDF)", "Delivered"),
        ("LinkedIn optimization notes", "Delivered"),
        ("Deployment URL", "https://alexrivera.github.io"),
    ],
}


def package_list_for_display() -> list[PackageSalesInfo]:
    return [PACKAGE_SALES[s] for s in ("foundation", "launch", "accelerator")]
