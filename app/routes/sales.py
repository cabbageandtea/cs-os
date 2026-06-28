"""Public sales pages: landing, demo, contact."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.lead_service import LeadPersistenceError, LeadValidationError, create_lead
from app.sales_content import (
    DEMO_EXAMPLE_CLIENT,
    DEMO_JOURNEY_STEPS,
    LANDING_FAQ,
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
