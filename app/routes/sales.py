"""Public sales pages: landing, demo, contact."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse, RedirectResponse, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.jinja_env import templates
from app.email_service import send_contact_lead_notification
from app.lead_service import LeadPersistenceError, LeadValidationError, create_lead
from app.legal_validation import LegalConsentError, validate_privacy_consent
from app.client_prerequisites import CLIENT_PREREQUISITES, prerequisites_for_package
from app.example_portfolios import (
    example_template_context,
    get_example_profile,
    get_portfolio_example,
    mock_subpage_context,
    resume_pdf_url,
)
from app.health import build_status_page_context
from app.site_branding import PUBLIC_SITEMAP_PATHS, site_base_url
from app.sales_content import (
    CASE_STUDIES,
    CREDIBILITY_STATS,
    CTA_PROOF_LINE,
    DEMO_EXAMPLE_CLIENT,
    DEMO_JOURNEY_STEPS,
    HERO_AUDIENCE,
    HERO_CTA_PRIMARY,
    HERO_CTA_SECONDARY,
    HERO_HEADLINE,
    HERO_LEAD,
    LANDING_FAQ,
    ME_DOMAIN_WHY,
    MARKET_PITFALLS,
    COMPARISON_COLUMNS,
    COMPARISON_ROWS,
    PORTFOLIO_SECTION_LABEL,
    PORTFOLIO_SECTION_LEAD,
    PRINCIPLES,
    PROCESS_STEPS,
    SHOWCASE_LINKS,
    SIGNAL_GAPS,
    VALUE_BULLETS,
    package_list_for_display,
)

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
RESUME_PDF_DIR = BASE_DIR / "static" / "examples" / "resumes"

_ROBOTS_DISALLOW_PREFIXES = (
    "/login",
    "/ops",
    "/dashboard",
    "/clients",
    "/intake",
    "/purchase",
    "/webhooks",
    "/example/",
    "/examples/",
)


@router.get("/robots.txt", response_class=PlainTextResponse)
def robots_txt() -> str:
    origin = site_base_url()
    lines = [
        "User-agent: *",
        "Allow: /",
        *(f"Disallow: {prefix}" for prefix in _ROBOTS_DISALLOW_PREFIXES),
        f"Sitemap: {origin}/sitemap.xml",
        "",
    ]
    return "\n".join(lines)


@router.get("/sitemap.xml")
def sitemap_xml() -> Response:
    origin = site_base_url()
    urls = "\n".join(
        f"  <url><loc>{origin}{path}</loc></url>"
        for path in PUBLIC_SITEMAP_PATHS
    )
    body = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n"
        "</urlset>\n"
    )
    return Response(content=body, media_type="application/xml")


@router.get("/", response_class=HTMLResponse)
def landing_page(request: Request):
    return templates.TemplateResponse(
        "landing.html",
        {
            "request": request,
            "packages": package_list_for_display(),
            "faq": LANDING_FAQ,
            "hero_headline": HERO_HEADLINE,
            "hero_audience": HERO_AUDIENCE,
            "hero_lead": HERO_LEAD,
            "hero_cta_primary": HERO_CTA_PRIMARY,
            "hero_cta_secondary": HERO_CTA_SECONDARY,
            "credibility_stats": CREDIBILITY_STATS,
            "signal_gaps": SIGNAL_GAPS,
            "value_bullets": VALUE_BULLETS,
            "process_steps": PROCESS_STEPS,
            "case_studies": CASE_STUDIES,
            "cta_proof_line": CTA_PROOF_LINE,
            "portfolio_section_label": PORTFOLIO_SECTION_LABEL,
            "portfolio_section_lead": PORTFOLIO_SECTION_LEAD,
            "showcase_links": SHOWCASE_LINKS,
            "me_domain_why": ME_DOMAIN_WHY,
            "principles": PRINCIPLES,
            "market_pitfalls": MARKET_PITFALLS,
            "comparison_columns": COMPARISON_COLUMNS,
            "comparison_rows": COMPARISON_ROWS,
        },
    )


@router.get("/demo", response_class=HTMLResponse)
def demo_page(request: Request):
    return templates.TemplateResponse(
        "demo.html",
        {
            "request": request,
            "journey_steps": DEMO_JOURNEY_STEPS,
            "example": DEMO_EXAMPLE_CLIENT,
            "showcase_links": SHOWCASE_LINKS,
        },
    )


@router.get("/contact", response_class=HTMLResponse)
def contact_form(request: Request, success: str | None = None):
    return templates.TemplateResponse(
        "contact.html",
        {
            "request": request,
            "error": None,
            "success": success == "1",
            "success_name": None,
            "form": {},
        },
    )


@router.post("/contact", response_class=HTMLResponse)
def submit_contact(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    target_role: str = Form(...),
    current_status: str = Form(...),
    interested_package: str = Form("unsure"),
    privacy_consent: str | None = Form(None),
    db: Session = Depends(get_db),
):
    form_data = {
        "name": name,
        "email": email,
        "target_role": target_role,
        "current_status": current_status,
        "interested_package": interested_package,
    }
    try:
        validate_privacy_consent((privacy_consent or "").strip().lower() == "on")
        lead = create_lead(
            db,
            name=name,
            email=email,
            target_role=target_role,
            current_status=current_status,
            interested_package=interested_package,
        )
    except LeadValidationError as exc:
        return templates.TemplateResponse(
            "contact.html",
            {"request": request, "error": str(exc), "success": False, "success_name": None, "form": form_data},
            status_code=422,
        )
    except LegalConsentError as exc:
        return templates.TemplateResponse(
            "contact.html",
            {"request": request, "error": str(exc), "success": False, "success_name": None, "form": form_data},
            status_code=422,
        )
    except LeadPersistenceError as exc:
        return templates.TemplateResponse(
            "contact.html",
            {"request": request, "error": str(exc), "success": False, "success_name": None, "form": form_data},
            status_code=500,
        )

    send_contact_lead_notification(
        name=lead.name,
        email=lead.email,
        target_role=lead.target_role,
        current_status=lead.current_status,
        interested_package=lead.interested_package,
    )

    return templates.TemplateResponse(
        "contact.html",
        {
            "request": request,
            "error": None,
            "success": True,
            "success_name": lead.name,
            "form": {},
        },
    )


@router.get("/start", response_class=HTMLResponse)
def client_start_hub(request: Request):
    return templates.TemplateResponse(
        "start.html",
        {
            "request": request,
            "prerequisites": CLIENT_PREREQUISITES,
        },
    )


@router.get("/status", response_class=HTMLResponse)
def system_status_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(
        "status.html",
        {"request": request, **build_status_page_context(db)},
    )


@router.get("/terms", response_class=HTMLResponse)
def terms_page(request: Request):
    return templates.TemplateResponse("terms.html", {"request": request})


@router.get("/privacy", response_class=HTMLResponse)
def privacy_page(request: Request):
    return templates.TemplateResponse("privacy.html", {"request": request})


def _render_example(request: Request, slug: str, template_name: str, **extra):
    ctx = example_template_context(slug, is_portfolio_home=extra.pop("is_portfolio_home", False))
    if ctx is None:
        raise HTTPException(status_code=404, detail="Example not found.")
    ctx.update(extra)
    return templates.TemplateResponse(template_name, {"request": request, **ctx})


@router.get("/example/{slug}", response_class=HTMLResponse)
def portfolio_example(request: Request, slug: str):
    profile = get_example_profile(slug)
    if profile is None:
        raise HTTPException(status_code=404, detail="Example not found.")
    return _render_example(
        request,
        slug,
        profile.template_name,
        is_portfolio_home=True,
        suite_active="portfolio",
    )


@router.get("/example/{slug}/projects/{project_slug}", response_class=HTMLResponse)
def portfolio_example_project(request: Request, slug: str, project_slug: str):
    ctx = mock_subpage_context(slug, project_slug, suite_active="portfolio")
    if ctx is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    return templates.TemplateResponse("examples/mock_project.html", {"request": request, **ctx})


@router.get("/example/{slug}/repo/{project_slug}", response_class=HTMLResponse)
def portfolio_example_repo(request: Request, slug: str, project_slug: str):
    ctx = mock_subpage_context(slug, project_slug, suite_active="github")
    if ctx is None:
        raise HTTPException(status_code=404, detail="Repository not found.")
    return templates.TemplateResponse("examples/mock_repo.html", {"request": request, **ctx})


@router.get("/example/{slug}/demo/{project_slug}", response_class=HTMLResponse)
def portfolio_example_demo(request: Request, slug: str, project_slug: str):
    ctx = mock_subpage_context(slug, project_slug, suite_active="portfolio")
    if ctx is None or not ctx["project"].has_demo:
        raise HTTPException(status_code=404, detail="Demo not found.")
    profile = get_example_profile(slug)
    if profile:
        ctx["chrome_path"] = f"demo.{profile.mock_domain}/{project_slug}"
    return templates.TemplateResponse("examples/mock_demo.html", {"request": request, **ctx})


@router.get("/example/{slug}/github", response_class=HTMLResponse)
def portfolio_example_github(request: Request, slug: str):
    profile = get_example_profile(slug)
    if profile is None:
        raise HTTPException(status_code=404, detail="Example not found.")
    return _render_example(
        request,
        slug,
        "examples/mock_github.html",
        suite_active="github",
        chrome_path=f"github.com/{profile.github_handle}",
    )


@router.get("/example/{slug}/linkedin", response_class=HTMLResponse)
def portfolio_example_linkedin(request: Request, slug: str):
    profile = get_example_profile(slug)
    if profile is None:
        raise HTTPException(status_code=404, detail="Example not found.")
    return _render_example(
        request,
        slug,
        "examples/mock_linkedin.html",
        suite_active="linkedin",
        chrome_path=f"linkedin.com/in/{profile.linkedin_handle}",
    )


@router.get("/example/{slug}/resume.pdf")
def portfolio_example_resume_pdf(slug: str):
    example = get_portfolio_example(slug)
    if example is None:
        raise HTTPException(status_code=404, detail="Example not found.")
    pdf_path = RESUME_PDF_DIR / example.resume_pdf_filename
    if not pdf_path.is_file():
        raise HTTPException(status_code=404, detail="Resume PDF not found.")
    safe_name = example.slug.replace("-", "_")
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"{safe_name}_resume.pdf",
    )


@router.get("/example/{slug}/resume", response_class=HTMLResponse)
def portfolio_example_resume(request: Request, slug: str):
    profile = get_example_profile(slug)
    if profile is None:
        raise HTTPException(status_code=404, detail="Example not found.")
    return _render_example(
        request,
        slug,
        profile.resume_template,
        suite_active="resume",
        chrome_path=f"{profile.mock_domain}/resume",
    )


@router.get("/purchase/return", response_class=HTMLResponse)
def purchase_return_page(request: Request, session_id: str = Query("")):
    return templates.TemplateResponse(
        "purchase_return.html",
        {"request": request, "session_id": session_id.strip()},
    )
