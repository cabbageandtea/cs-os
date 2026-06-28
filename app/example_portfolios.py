"""Fictional portfolio examples — hosted mocks, not real .me domains."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

LinkKind = Literal["repo", "demo", "project"]
RepoStyle = Literal["readme", "notebook"]


@dataclass(frozen=True)
class MockEducation:
    degree: str
    school: str
    dates: str
    detail: str


@dataclass(frozen=True)
class MockHeroStat:
    value: str
    label: str


@dataclass(frozen=True)
class MockApproachStep:
    number: str
    title: str
    body: str


@dataclass(frozen=True)
class MockSkillGroup:
    name: str
    skills: tuple[str, ...]


@dataclass(frozen=True)
class MockProjectHighlight:
    title: str
    body: str


@dataclass(frozen=True)
class MockExperience:
    title: str
    org: str
    dates: str
    detail: str = ""
    meta: str = ""
    bullets: tuple[str, ...] = ()


@dataclass(frozen=True)
class MockProject:
    slug: str
    title: str
    stack: str
    summary: str
    outcome: str
    visual_label: str
    visual_tone: str  # data | code
    readme_intro: str
    readme_bullets: tuple[str, ...]
    primary_cta: str
    secondary_cta: str
    primary_link: LinkKind
    secondary_link: LinkKind
    has_demo: bool = False
    repo_style: RepoStyle = "readme"
    repo_language: str = "Python"
    repo_stars: int = 0


@dataclass(frozen=True)
class ExampleProfile:
    slug: str
    template_name: str
    resume_template: str
    theme: str  # light-hero | dark | pro-teal | pro-coral
    package_label: str
    mock_domain: str
    person_name: str
    target_role: str
    role_tagline: str
    resume_pdf_filename: str
    email: str
    github_handle: str
    linkedin_handle: str
    about: str
    hero_lead: str
    sidebar_note: str
    education: MockEducation
    extra_education: MockEducation | None
    projects: tuple[MockProject, ...]
    skills: tuple[str, ...]
    contact_blurb: str
    linkedin_headline: str
    linkedin_about: str
    linkedin_experience: tuple[MockExperience, ...] = ()
    availability_badge: str = ""
    trust_items: tuple[str, ...] = ()
    hero_stats: tuple[MockHeroStat, ...] = ()
    about_heading: str = ""
    focus_areas: tuple[str, ...] = ()
    role_tags: tuple[str, ...] = ()
    approach_title: str = ""
    approach_lead: str = ""
    approach_steps: tuple[MockApproachStep, ...] = ()
    experience_heading: str = ""
    experience_lead: str = ""
    experience: tuple[MockExperience, ...] = ()
    project_section_title: str = ""
    project_section_lead: str = ""
    project_highlights: tuple[MockProjectHighlight, ...] = ()
    skill_groups: tuple[MockSkillGroup, ...] = ()
    skills_heading: str = ""
    skills_lead: str = ""
    certifications: tuple[str, ...] = ()
    credentials_heading: str = ""
    credentials_lead: str = ""
    recruiter_snapshot: str = ""
    contact_heading: str = ""
    location_note: str = ""


EXAMPLE_PROFILES: dict[str, ExampleProfile] = {
    "alex-rivera": ExampleProfile(
        slug="alex-rivera",
        template_name="examples/portfolio_pro.html",
        resume_template="examples/resume_alex.html",
        theme="pro-teal",
        package_label="Launch",
        mock_domain="alexrivera.me",
        person_name="Alex Rivera",
        target_role="Data Analyst Intern",
        role_tagline="Information Systems · graduating 2027",
        resume_pdf_filename="alex-rivera.pdf",
        email="alex.rivera@example.com",
        github_handle="alexrivera-dev",
        linkedin_handle="alexrivera",
        about=(
            "Information Systems senior at State University. I build ETL pipelines and dashboards "
            "that answer real questions — peak dining demand, ER bottlenecks, budget tradeoffs — "
            "and present them so non-technical stakeholders act on the insight."
        ),
        hero_lead=(
            "I turn coursework and side projects into recruiter-ready data stories — clear metrics, "
            "live dashboards, and copy that survives a six-second scan."
        ),
        sidebar_note="",
        education=MockEducation(
            degree="B.S. Information Systems",
            school="State University",
            dates="Expected May 2027",
            detail="GPA 3.7 · Dean's list · Coursework: databases, statistics, data visualization",
        ),
        extra_education=None,
        projects=(
            MockProject(
                slug="campus-dining",
                title="Campus Dining Insights",
                stack="Pandas · Plotly · SQLite",
                summary=(
                    "Ingested 40k+ meal-swipe records, modeled peak hours and waste patterns, "
                    "and presented recommendations to student government."
                ),
                outcome="Identified two underused meal windows — proposal adopted for pilot scheduling.",
                visual_label="Python · ETL",
                visual_tone="data",
                readme_intro="ETL pipeline and analysis for campus meal-swipe data.",
                readme_bullets=(
                    "Loads CSV exports into SQLite with idempotent daily ingest",
                    "Peak-hour heatmaps and waste-by-station charts in Plotly",
                    "Executive memo with scheduling recommendations for student government",
                ),
                primary_cta="View code",
                secondary_cta="Case study",
                primary_link="repo",
                secondary_link="project",
                repo_language="Python",
                repo_stars=14,
            ),
            MockProject(
                slug="healthcare-wait",
                title="Healthcare Wait-Time Dashboard",
                stack="SQL · Tableau · open data",
                summary=(
                    "Modeled ER wait times by triage level for a capstone clinic dataset. "
                    "Surfaced bottlenecks in intake vs. bed assignment."
                ),
                outcome="Two delay drivers explained 18% of total wait — documented in executive summary.",
                visual_label="SQL · BI",
                visual_tone="data",
                readme_intro="Capstone analytics on synthetic ER throughput data.",
                readme_bullets=(
                    "Star schema in PostgreSQL with triage-level wait facts",
                    "Tableau workbook: intake vs. bed-assignment bottleneck views",
                    "PDF executive summary for clinic stakeholders",
                ),
                primary_cta="Live dashboard",
                secondary_cta="View SQL repo",
                primary_link="demo",
                secondary_link="repo",
                has_demo=True,
                repo_language="SQL",
                repo_stars=9,
            ),
        ),
        skills=(
            "Python",
            "SQL",
            "Pandas",
            "Tableau",
            "Excel",
            "Statistics",
            "Technical writing",
        ),
        contact_blurb="Open to data analyst internships — healthcare, campus ops, and civic data.",
        linkedin_headline="Information Systems student · Seeking data analyst internship",
        linkedin_about=(
            "Building Python/SQL projects with measurable outcomes — campus dining analytics, "
            "healthcare wait-time dashboards, and stakeholder-ready summaries. Portfolio, resume, "
            "and GitHub tell one story at alexrivera.me."
        ),
        availability_badge="Open to data analyst internships · May 2027 · remote or hybrid",
        trust_items=(
            "State University · Dean's List",
            "Google Data Analytics Certificate",
            "40k+ rows in capstone datasets",
            "Plotly + Tableau deliverables",
        ),
        hero_stats=(
            MockHeroStat("2", "Shipped capstone projects"),
            MockHeroStat("40k+", "Rows modeled & reported"),
            MockHeroStat("3.7", "GPA · graduating 2027"),
        ),
        about_heading="Coursework with consequences.",
        focus_areas=(
            "ETL pipelines & reproducible SQL",
            "Stakeholder-ready dashboards",
            "Open-data analysis with documented assumptions",
            "Executive summaries for non-technical audiences",
            "Impact metrics recruiters can verify",
        ),
        role_tags=("Data Analyst Intern", "Healthcare analytics", "Campus operations", "Civic data"),
        approach_title="Where questions meet defensible numbers",
        approach_lead=(
            "Not charts for their own sake — building pipelines and narratives that answer "
            "who acts on the insight and what changed because of it."
        ),
        approach_steps=(
            MockApproachStep(
                "01",
                "Discover",
                "Start with the decision and the audience. Define the metric, the grain, and what "
                "evidence would change someone's mind.",
            ),
            MockApproachStep(
                "02",
                "Model",
                "Clean joins, documented assumptions, idempotent ingest. Notebooks and SQL scripts "
                "a teammate can rerun without guessing.",
            ),
            MockApproachStep(
                "03",
                "Present",
                "Executive summaries, annotated dashboards, and PDF memos built for a six-second "
                "recruiter scan — outcome first, method second.",
            ),
        ),
        experience_heading="Built in labs, validated on real questions",
        experience_lead=(
            "Research, tutoring, and campus operations experience — each project tied to a "
            "stakeholder who could act on the result."
        ),
        experience=(
            MockExperience(
                title="Research Assistant — Campus Analytics Lab",
                org="State University",
                dates="Jan 2025 – Present",
                meta="Part-time · On-campus · Data & reporting",
                bullets=(
                    "Built ETL pipelines ingesting 40k+ dining records into SQLite with daily refresh and data dictionary.",
                    "Delivered Plotly dashboards and a scheduling memo adopted for a student-government pilot.",
                    "Documented ingest runbooks so the lab can extend datasets without one-off scripts.",
                ),
            ),
            MockExperience(
                title="Peer Tutor — Intro to Databases",
                org="State University",
                dates="Sep 2024 – May 2025",
                meta="10 hrs/wk · SQL labs",
                bullets=(
                    "Led weekly labs for 30+ students — joins, aggregations, window functions, and explain plans.",
                    "Authored practice datasets modeled on operational reporting, not toy single-table examples.",
                ),
            ),
            MockExperience(
                title="Student Worker — Campus Dining Services",
                org="State University",
                dates="Aug 2023 – Present",
                meta="Part-time · Operations floor",
                bullets=(
                    "Saw peak-hour waste and scheduling pain that became the dining analytics capstone.",
                    "Partnered with shift leads on count accuracy during lunch rushes — grounded the analysis in floor reality.",
                ),
            ),
        ),
        project_section_title="Analytics from real operational questions",
        project_section_lead=(
            "Capstone-grade work with problem statements, methods, and outcomes — not tutorial clones."
        ),
        project_highlights=(
            MockProjectHighlight(
                "Peak-hour modeling",
                "Heatmaps and waste-by-station views tied to actionable scheduling windows — not vanity charts.",
            ),
            MockProjectHighlight(
                "ER bottleneck analysis",
                "Star-schema SQL plus Tableau views separating intake delay from bed-assignment delay.",
            ),
            MockProjectHighlight(
                "Executive summaries",
                "One-page PDF memos with outcome metrics hiring managers can repeat in a screen.",
            ),
            MockProjectHighlight(
                "Reproducible ingest",
                "Idempotent daily loads, documented assumptions, and handoff notes for the next analyst.",
            ),
        ),
        skill_groups=(
            MockSkillGroup(
                "Data & analysis",
                ("Python", "SQL", "Pandas", "Statistics", "Hypothesis testing", "Data visualization"),
            ),
            MockSkillGroup(
                "Tools",
                ("SQLite", "PostgreSQL", "Tableau", "Plotly", "Excel", "Jupyter"),
            ),
            MockSkillGroup(
                "Communication",
                ("Technical writing", "Stakeholder memos", "Presentation decks", "Git & GitHub"),
            ),
        ),
        skills_heading="What recruiters scan for",
        skills_lead="Analysis depth, tool fluency, and copy that survives a phone screen.",
        certifications=(
            "Google Data Analytics Professional Certificate",
            "Dean's List — 4 semesters",
            "Intro to Database Systems — A",
        ),
        credentials_heading="Formalizing a data-oriented path",
        credentials_lead="Coursework and credentials aligned to analyst screens — not a scatter of unrelated badges.",
        recruiter_snapshot=(
            "IS senior · Python/SQL dashboards · campus + healthcare datasets · May 2027 · "
            "seeking data analyst internships · portfolio + PDF + LinkedIn aligned."
        ),
        contact_heading="Open to the next internship",
        location_note="Remote, hybrid, or on-site — healthcare, campus ops, and civic data teams.",
    ),
    "jordan-kim": ExampleProfile(
        slug="jordan-kim",
        template_name="examples/portfolio_pro.html",
        resume_template="examples/resume_jordan.html",
        theme="pro-coral",
        package_label="Accelerator",
        mock_domain="jordankim.me",
        person_name="Jordan Kim",
        target_role="Junior Software Engineer",
        role_tagline="Career change · bootcamp + 4 yrs retail ops",
        resume_pdf_filename="jordan-kim.pdf",
        email="jordan.kim@example.com",
        github_handle="jordankim-dev",
        linkedin_handle="jordankim",
        hero_lead=(
            "I automated inventory reporting as a floor lead. Now I build APIs and UIs with tests, "
            "deploys, and commit history recruiters can actually read."
        ),
        sidebar_note=(
            "Retail team lead → full-stack bootcamp → SWE search. Pivot story aligned across "
            "this site, resume, and LinkedIn."
        ),
        education=MockEducation(
            degree="Full-stack engineering certificate",
            school="CodeForge Bootcamp",
            dates="2025",
            detail="Capstone: ShiftSync API · 480+ hours · pair programming & CI/CD",
        ),
        extra_education=MockEducation(
            degree="B.A. Business Administration",
            school="State College",
            dates="2018",
            detail="Minor in operations management",
        ),
        projects=(
            MockProject(
                slug="shiftsync",
                title="ShiftSync API",
                stack="PostgreSQL · JWT · Docker",
                summary=(
                    "REST API + React UI for shift swaps at small retailers — replaces spreadsheet "
                    "chaos with auditable requests."
                ),
                outcome="Pilot store cut scheduling conflicts in manual tests; OpenAPI + Render deploy documented.",
                visual_label="FastAPI · React",
                visual_tone="code",
                readme_intro="Shift swap workflow for small retail teams.",
                readme_bullets=(
                    "FastAPI backend with role-based JWT auth",
                    "React UI for request / approve / audit trail",
                    "Docker Compose + Render deploy notes in README",
                ),
                primary_cta="Live demo",
                secondary_cta="Source code",
                primary_link="demo",
                secondary_link="repo",
                has_demo=True,
                repo_language="Python",
                repo_stars=22,
            ),
            MockProject(
                slug="inventory-anomaly",
                title="Inventory Anomaly Detector",
                stack="scikit-learn · pandas",
                summary="Unsupervised flags on nightly shrink exports — tied to real ops experience from prior role.",
                outcome="SKU clusters surfaced for manual audit; notebook + README for hiring screens.",
                visual_label="ML · Python",
                visual_tone="code",
                readme_intro="Notebook-first ML pipeline on retail shrink exports.",
                readme_bullets=(
                    "Isolation Forest on nightly SKU shrink features",
                    "Cluster report export for floor-audit follow-up",
                    "Jupyter notebook + requirements.txt for reproducibility",
                ),
                primary_cta="Open notebook",
                secondary_cta="Case study",
                primary_link="repo",
                secondary_link="project",
                repo_style="notebook",
                repo_language="Jupyter Notebook",
                repo_stars=11,
            ),
        ),
        skills=(
            "Python",
            "TypeScript",
            "React",
            "FastAPI",
            "PostgreSQL",
            "Docker",
            "Git",
            "pytest",
        ),
        contact_blurb="Open to junior SWE roles — backend-leaning full stack with ops domain knowledge.",
        linkedin_headline="Junior Software Engineer · Retail ops → full-stack bootcamp",
        linkedin_about=(
            "Four years retail leadership, now shipping tested APIs and React UIs. Pivot narrative "
            "consistent across jordankim.me, GitHub, and resume."
        ),
        linkedin_experience=(
            MockExperience(
                title="Floor Lead",
                org="National retail chain",
                dates="2019 – 2023",
                meta="Full-time · Pittsburgh, PA · On-site",
                detail="Inventory audits, associate training, Excel reporting adopted district-wide.",
                bullets=(
                    "Automated weekly shrink summaries in Excel — template adopted by two neighboring stores.",
                    "Trained associates on count accuracy during peak seasons; reduced recurring mis-picks.",
                    "Partnered with district on ad-hoc inventory investigations before escalation.",
                ),
            ),
        ),
        availability_badge="Open to junior SWE roles · backend-leaning full stack · remote or hybrid",
        trust_items=(
            "CodeForge Bootcamp · 480+ hours",
            "4 yrs retail floor leadership",
            "FastAPI + React capstone deployed",
            "pytest + CI on every project",
        ),
        hero_stats=(
            MockHeroStat("2", "Deployed capstone apps"),
            MockHeroStat("4 yrs", "Retail ops before pivot"),
            MockHeroStat("33", "GitHub repo stars (sample)"),
        ),
        about=(
            "Four years as a floor lead taught me what breaks in production — mis-picks, shrink, "
            "scheduling chaos. CodeForge formalized the fix: tested APIs, readable commits, and "
            "deploy notes recruiters can follow."
        ),
        about_heading="Floor ops. Shipping code.",
        focus_areas=(
            "REST APIs with auth and audit trails",
            "React UIs with clear empty states",
            "Dockerized local dev + Render deploys",
            "Notebook-to-service ML handoffs",
            "Pivot narrative aligned across every surface",
        ),
        role_tags=("Junior SWE", "Backend-leaning", "Retail domain", "Career change"),
        approach_title="Where ops discipline meets shipping",
        approach_lead=(
            "Not tutorial clones — features, tests, and READMEs that show how the system behaves "
            "when someone else runs it."
        ),
        approach_steps=(
            MockApproachStep(
                "01",
                "Scope",
                "Define the workflow, roles, and failure modes first — especially for ops-heavy domains "
                "like shift swaps and inventory.",
            ),
            MockApproachStep(
                "02",
                "Ship",
                "FastAPI or React with pytest, typed handlers, and OpenAPI or component states documented.",
            ),
            MockApproachStep(
                "03",
                "Prove",
                "Live demo, deploy notes, and commit history that tell the pivot story without hand-waving.",
            ),
        ),
        experience_heading="Leadership before the bootcamp",
        experience_lead=(
            "Retail leadership that explains why my projects focus on audit trails, roles, and "
            "operational edge cases."
        ),
        experience=(
            MockExperience(
                title="Floor Lead",
                org="National retail chain",
                dates="2019 – 2023",
                meta="Full-time · Pittsburgh, PA",
                bullets=(
                    "Owned nightly shrink reporting and coached associates on count accuracy during peak weeks.",
                    "Built Excel templates for inventory variance — adopted district-wide after pilot.",
                    "Led ad-hoc investigations on mis-picks before they hit outbound — foundation for anomaly detector project.",
                ),
            ),
            MockExperience(
                title="Sales Associate → Key Holder",
                org="Regional apparel retailer",
                dates="2017 – 2019",
                meta="Part-time · Southwestern PA",
                bullets=(
                    "Opened/closes, cash reconciliation, and back-room organization in high-traffic mall store.",
                    "Promoted for reliability and training newer associates on POS and restock workflows.",
                ),
            ),
        ),
        project_section_title="Projects recruiters can run",
        project_section_lead=(
            "Capstones with live demos, tests, and README deploy sections — not README-only homework."
        ),
        project_highlights=(
            MockProjectHighlight(
                "Auth + audit trail",
                "JWT roles, request/approve flow, and immutable history for shift swaps.",
            ),
            MockProjectHighlight(
                "Live demo",
                "Render-deployed ShiftSync with seed data and OpenAPI docs linked from README.",
            ),
            MockProjectHighlight(
                "ML from ops data",
                "Isolation Forest on shrink exports — notebook plus export script for floor follow-up.",
            ),
            MockProjectHighlight(
                "Test coverage",
                "pytest on API routes; CI badge in README for hiring screens.",
            ),
        ),
        skill_groups=(
            MockSkillGroup(
                "Backend",
                ("Python", "FastAPI", "PostgreSQL", "SQLAlchemy", "pytest", "JWT"),
            ),
            MockSkillGroup(
                "Frontend",
                ("TypeScript", "React", "HTML/CSS", "REST clients", "Form validation"),
            ),
            MockSkillGroup(
                "DevOps & ops",
                ("Docker", "Git", "GitHub Actions", "Render", "Retail inventory workflows"),
            ),
        ),
        skills_heading="Stack that matches the story",
        skills_lead="Backend-leaning full stack with ops domain knowledge baked in.",
        certifications=(
            "CodeForge Full-Stack Engineering Certificate",
            "AWS Cloud Practitioner (in progress)",
        ),
        credentials_heading="Credentials that support the pivot",
        credentials_lead="Bootcamp capstone plus prior degree — narrative stays consistent on resume and LinkedIn.",
        recruiter_snapshot=(
            "Retail floor lead → bootcamp → junior SWE · FastAPI/React · live demo + tests · "
            "Pittsburgh area · seeking backend-leaning full-stack roles."
        ),
        contact_heading="Open to junior SWE roles",
        location_note="Remote, hybrid, or on-site — teams that value ops-minded engineers.",
    ),
}


@dataclass(frozen=True)
class PortfolioExample:
    slug: str
    template_name: str
    mock_domain: str
    person_name: str
    target_role: str
    resume_pdf_filename: str


def get_portfolio_example(slug: str) -> PortfolioExample | None:
    profile = get_example_profile(slug)
    if profile is None:
        return None
    return PortfolioExample(
        slug=profile.slug,
        template_name=profile.template_name,
        mock_domain=profile.mock_domain,
        person_name=profile.person_name,
        target_role=profile.target_role,
        resume_pdf_filename=profile.resume_pdf_filename,
    )


def get_example_profile(slug: str) -> ExampleProfile | None:
    return EXAMPLE_PROFILES.get(slug.strip().lower())


def get_example_project(slug: str, project_slug: str) -> MockProject | None:
    profile = get_example_profile(slug)
    if profile is None:
        return None
    key = project_slug.strip().lower()
    for project in profile.projects:
        if project.slug == key:
            return project
    return None


def resume_pdf_url(slug: str) -> str | None:
    profile = get_example_profile(slug)
    if profile is None:
        return None
    return f"/example/{profile.slug}/resume.pdf"


def portfolio_url(slug: str) -> str | None:
    profile = get_example_profile(slug)
    if profile is None:
        return None
    return f"/example/{profile.slug}"


def project_url(slug: str, project_slug: str) -> str:
    return f"/example/{slug}/projects/{project_slug}"


def repo_url(slug: str, project_slug: str) -> str:
    return f"/example/{slug}/repo/{project_slug}"


def demo_url(slug: str, project_slug: str) -> str:
    return f"/example/{slug}/demo/{project_slug}"


def github_profile_url(slug: str) -> str | None:
    profile = get_example_profile(slug)
    if profile is None:
        return None
    return f"/example/{profile.slug}/github"


def linkedin_profile_url(slug: str) -> str | None:
    profile = get_example_profile(slug)
    if profile is None:
        return None
    return f"/example/{profile.slug}/linkedin"


def external_repo_display(slug: str, project_slug: str) -> str | None:
    profile = get_example_profile(slug)
    if profile is None:
        return None
    return f"github.com/{profile.github_handle}/{project_slug}"


def _link_url(slug: str, project: MockProject, kind: LinkKind) -> str:
    if kind == "demo":
        return demo_url(slug, project.slug)
    if kind == "project":
        return project_url(slug, project.slug)
    return repo_url(slug, project.slug)


def _project_cards(slug: str, profile: ExampleProfile) -> list[dict]:
    cards: list[dict] = []
    for project in profile.projects:
        cards.append(
            {
                "project": project,
                "detail_url": project_url(slug, project.slug),
                "repo_url": repo_url(slug, project.slug),
                "demo_url": demo_url(slug, project.slug),
                "primary_url": _link_url(slug, project, project.primary_link),
                "secondary_url": _link_url(slug, project, project.secondary_link),
                "repo_display": external_repo_display(slug, project.slug),
            }
        )
    return cards


def example_template_context(slug: str, *, is_portfolio_home: bool = False) -> dict | None:
    profile = get_example_profile(slug)
    if profile is None:
        return None
    return {
        "slug": profile.slug,
        "profile": profile,
        "theme": profile.theme,
        "package_label": profile.package_label,
        "mock_domain": profile.mock_domain,
        "person_name": profile.person_name,
        "target_role": profile.target_role,
        "role_tagline": profile.role_tagline,
        "email": profile.email,
        "github_handle": profile.github_handle,
        "linkedin_handle": profile.linkedin_handle,
        "github_url": github_profile_url(slug),
        "linkedin_url": linkedin_profile_url(slug),
        "about": profile.about,
        "hero_lead": profile.hero_lead,
        "sidebar_note": profile.sidebar_note,
        "education": profile.education,
        "extra_education": profile.extra_education,
        "skills": profile.skills,
        "contact_blurb": profile.contact_blurb,
        "linkedin_experience": profile.linkedin_experience,
        "availability_badge": profile.availability_badge,
        "trust_items": profile.trust_items,
        "hero_stats": profile.hero_stats,
        "about_heading": profile.about_heading,
        "focus_areas": profile.focus_areas,
        "role_tags": profile.role_tags,
        "approach_title": profile.approach_title,
        "approach_lead": profile.approach_lead,
        "approach_steps": profile.approach_steps,
        "experience_heading": profile.experience_heading,
        "experience_lead": profile.experience_lead,
        "experience": profile.experience,
        "project_section_title": profile.project_section_title,
        "project_section_lead": profile.project_section_lead,
        "project_highlights": profile.project_highlights,
        "skill_groups": profile.skill_groups,
        "skills_heading": profile.skills_heading,
        "skills_lead": profile.skills_lead,
        "certifications": profile.certifications,
        "credentials_heading": profile.credentials_heading,
        "credentials_lead": profile.credentials_lead,
        "recruiter_snapshot": profile.recruiter_snapshot,
        "contact_heading": profile.contact_heading,
        "location_note": profile.location_note,
        "last_name": profile.person_name.split(" ")[-1],
        "project_cards": _project_cards(slug, profile),
        "projects": profile.projects,
        "portfolio_url": portfolio_url(slug),
        "resume_pdf_url": resume_pdf_url(slug),
        "resume_url": f"/example/{slug}/resume",
        "first_name": profile.person_name.split(" ")[0],
        "is_portfolio_home": is_portfolio_home,
        "suite_active": "portfolio" if is_portfolio_home else "",
        "total_repo_stars": sum(p.repo_stars for p in profile.projects),
    }


def mock_subpage_context(
    slug: str,
    project_slug: str | None = None,
    *,
    suite_active: str = "",
    chrome_path: str | None = None,
) -> dict | None:
    base = example_template_context(slug)
    if base is None:
        return None
    base["suite_active"] = suite_active
    base["chrome_path"] = chrome_path or base["mock_domain"]
    profile = get_example_profile(slug)
    if profile is None:
        return None
    if project_slug:
        project = get_example_project(slug, project_slug)
        if project is None:
            return None
        base = {
            **base,
            "project": project,
            "project_url": project_url(slug, project.slug),
            "repo_url": repo_url(slug, project.slug),
            "demo_url": demo_url(slug, project.slug),
            "repo_display": external_repo_display(slug, project.slug),
            "chrome_path": chrome_path or external_repo_display(slug, project.slug) or base["mock_domain"],
        }
    base["profile"] = profile
    return base
