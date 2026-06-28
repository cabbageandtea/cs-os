"""Sales and marketing content for public pages. Conversion-focused copy."""

from __future__ import annotations

from dataclasses import dataclass

from app.package_config import PACKAGES


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
        who_for="Students and early-career builders who need a live portfolio from class projects.",
        deliverables=PACKAGES["foundation"].deliverables,
        turnaround="5–10 business days after intake",
        revision_rounds=1,
    ),
    "launch": PackageSalesInfo(
        slug="launch",
        display_name="Launch",
        price_display="$199",
        who_for="Job seekers who want portfolio, resume, and LinkedIn aligned for recruiter outreach.",
        deliverables=PACKAGES["launch"].deliverables,
        turnaround="7–14 business days after intake",
        revision_rounds=2,
        featured=True,
    ),
    "accelerator": PackageSalesInfo(
        slug="accelerator",
        display_name="Accelerator",
        price_display="$349",
        who_for="Candidates targeting competitive roles who want strategy, narrative, and premium support.",
        deliverables=PACKAGES["accelerator"].deliverables,
        turnaround="10–21 business days after intake",
        revision_rounds=3,
    ),
}

LANDING_FAQ = [
    (
        "How is this different from a resume writer or web designer?",
        "You get one coordinated package: portfolio, resume, and LinkedIn tell the same story. "
        "We build from your real projects—not generic templates.",
    ),
    (
        "When does delivery start?",
        "After you pay and complete intake. The delivery clock starts when your intake is submitted, not at payment.",
    ),
    (
        "What if I am still in school?",
        "Foundation and Launch are built for students turning coursework into proof of work. "
        "Bring class projects, internships, and target role—we handle structure and deployment.",
    ),
    (
        "Can I talk to someone before paying?",
        "Yes. Use the contact form and we will reply within one business day.",
    ),
    (
        "What is your refund policy?",
        "See customer terms at checkout. Refunds are handled case-by-case before delivery begins.",
    ),
]

DEMO_JOURNEY_STEPS = [
    {
        "title": "1. Choose a package",
        "description": "Alex selects Launch ($199) to become recruiter-ready before graduation.",
    },
    {
        "title": "2. Pay securely",
        "description": "Checkout via Stripe. A client record is created automatically in CS-OS.",
    },
    {
        "title": "3. Complete intake",
        "description": "Alex submits education, projects, GitHub, and target role through a secure link.",
    },
    {
        "title": "4. We deliver",
        "description": "Portfolio goes live. Resume and LinkedIn notes align to the same positioning.",
    },
    {
        "title": "5. Review & handoff",
        "description": "Alex reviews deliverables, requests revisions (2 rounds included on Launch), and receives live URLs.",
    },
]

DEMO_EXAMPLE_CLIENT = {
    "name": "Alex Rivera (Example)",
    "target_role": "Data Analyst Intern",
    "package": "Launch",
    "pipeline_stage": "Delivered",
    "deliverables": [
        ("Portfolio website", "https://demo-portfolio.cs-os.example.com"),
        ("Resume (PDF)", "Delivered"),
        ("LinkedIn optimization notes", "Delivered"),
        ("Deployment URL", "https://demo-portfolio.cs-os.example.com"),
    ],
}


def package_list_for_display() -> list[PackageSalesInfo]:
    return [PACKAGE_SALES[s] for s in ("foundation", "launch", "accelerator")]
