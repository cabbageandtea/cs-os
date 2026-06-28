"""Public sales pages: landing, demo, contact."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.lead_service import LeadPersistenceError, LeadValidationError, create_lead
from app.client_prerequisites import CLIENT_PREREQUISITES, prerequisites_for_package
from app.health import build_status_page_context
from app.sales_content import (
    CASE_STUDIES,
    CREDIBILITY_STATS,
    DEMO_EXAMPLE_CLIENT,
    DEMO_JOURNEY_STEPS,
    HERO_AUDIENCE,
    HERO_CTA_PRIMARY,
    HERO_CTA_SECONDARY,
    HERO_HEADLINE,
    HERO_LEAD,
    LANDING_FAQ,
    PRINCIPLES,
    PROCESS_STEPS,
    SIGNAL_GAPS,
    VALUE_BULLETS,
    package_list_for_display,
)

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


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
            "principles": PRINCIPLES,
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
    except LeadPersistenceError as exc:
        return templates.TemplateResponse(
            "contact.html",
            {"request": request, "error": str(exc), "success": False, "success_name": None, "form": form_data},
            status_code=500,
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


@router.get("/purchase/return", response_class=HTMLResponse)
def purchase_return_page(request: Request, session_id: str = Query("")):
    return templates.TemplateResponse(
        "purchase_return.html",
        {"request": request, "session_id": session_id.strip()},
    )
