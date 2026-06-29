"""Stripe checkout, webhooks, and token-based intake routes."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from app.jinja_env import templates
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.intake_context import intake_form_context
from app.intake_notify import intake_url_for_token, maybe_send_intake_reminder_email
from app.intake_tokens import assign_intake_token
from app.intake_validation import IntakeValidationError, resolve_client_package_slug
from app.models import Client, IntakeStatus, Purchase, PurchaseStatus
from app.package_config import PACKAGES, PackageConfigError, checkout_package_rows
from app.services import IntakeAccessError, PersistenceError, complete_token_intake
from app.stripe_branding import StripeBrandingError, checkout_branding_settings
from app.stripe_checkout import StripeCheckoutError, base_url, create_checkout_session
from app.legal_validation import LegalConsentError, validate_terms_accepted
from app.stripe_webhook import (
    WebhookConfigError,
    WebhookSignatureError,
    process_webhook,
)

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent


def _token_intake_template_context(
    *,
    client: Client,
    token: str,
    prefill: dict | None = None,
) -> dict:
    slug = resolve_client_package_slug(client.package_slug, client.package_tier)
    base_prefill = {
        "name": client.name if client.name not in {"Pending Intake", "Pending intake"} else "",
        "email": client.email or "",
    }
    if prefill:
        base_prefill.update(prefill)
    return {
        "client": client,
        "token": token,
        **intake_form_context(
            package_slug=slug,
            show_package_select=False,
            email_readonly=bool(client.email),
            prefill=base_prefill,
        ),
    }


def _intake_prefill_from_form(
    *,
    name: str,
    email: str,
    target_role: str,
    experience_education: str,
    experience_projects: str,
    experience_work: str,
    skills: str,
    career_goals: str,
    linkedin_url: str,
    github_url: str,
    portfolio_template: str,
    resume_url: str,
    existing_portfolio_url: str,
    certifications: str,
    job_timeline: str,
    additional_notes: str,
) -> dict:
    return {
        "name": name,
        "email": email,
        "target_role": target_role,
        "experience_education": experience_education,
        "experience_projects": experience_projects,
        "experience_work": experience_work,
        "skills": skills,
        "career_goals": career_goals,
        "linkedin_url": linkedin_url,
        "github_url": github_url,
        "portfolio_template": portfolio_template,
        "resume_url": resume_url,
        "existing_portfolio_url": existing_portfolio_url,
        "certifications": certifications,
        "job_timeline": job_timeline,
        "additional_notes": additional_notes,
    }


def _find_client_by_token(db: Session, token: str) -> Client | None:
    from app.intake_tokens import hash_token

    token_hash = hash_token(token)
    return db.scalar(
        select(Client)
        .where(Client.intake_token_hash == token_hash)
        .options(joinedload(Client.project))
    )


@router.get("/checkout", response_class=HTMLResponse)
def checkout_page(request: Request):
    return templates.TemplateResponse(
        "checkout.html",
        {
            "request": request,
            "packages": checkout_package_rows(),
            "error": None,
        },
    )


@router.post("/checkout/create")
def checkout_create(
    request: Request,
    package_slug: str = Form(...),
    terms_accepted: str | None = Form(None),
    db: Session = Depends(get_db),
):
    packages = checkout_package_rows()
    try:
        validate_terms_accepted((terms_accepted or "").strip().lower() == "on")
        _, redirect_url = create_checkout_session(db, package_slug)
    except LegalConsentError as exc:
        return templates.TemplateResponse(
            "checkout.html",
            {"request": request, "packages": packages, "error": str(exc)},
            status_code=422,
        )
    except (PackageConfigError, StripeCheckoutError, StripeBrandingError) as exc:
        return templates.TemplateResponse(
            "checkout.html",
            {"request": request, "packages": packages, "error": str(exc)},
            status_code=422,
        )
    return RedirectResponse(url=redirect_url, status_code=303)


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    signature = request.headers.get("Stripe-Signature")

    try:
        process_webhook(db, payload, signature)
    except WebhookConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except WebhookSignatureError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except PersistenceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return JSONResponse({"received": True})


@router.get("/purchase/success", response_class=HTMLResponse)
def purchase_success(request: Request, session_id: str = Query(...)):
    return templates.TemplateResponse(
        "purchase_success.html",
        {"request": request, "session_id": session_id, "base_url": base_url()},
    )


@router.get("/purchase/cancelled", response_class=HTMLResponse)
def purchase_cancelled(request: Request):
    return templates.TemplateResponse("purchase_cancelled.html", {"request": request})


@router.get("/purchase/status")
def purchase_status(session_id: str = Query(...), db: Session = Depends(get_db)):
    purchase = db.scalar(select(Purchase).where(Purchase.stripe_session_id == session_id))
    if not purchase:
        return JSONResponse({"status": "unknown", "ready": False})

    if purchase.status != PurchaseStatus.PAID.value or not purchase.client_id:
        return JSONResponse(
            {
                "status": purchase.status,
                "ready": False,
                "package_slug": purchase.package_slug,
            }
        )

    client = db.get(Client, purchase.client_id)
    if not client:
        return JSONResponse({"status": purchase.status, "ready": False})

    intake_url = None
    if client.intake_status == IntakeStatus.PENDING.value:
        token = assign_intake_token(client)
        if not purchase.intake_link_delivered:
            purchase.intake_link_delivered = True
        db.commit()
        intake_url = f"{base_url()}/intake/{token}"

    return JSONResponse(
        {
            "status": purchase.status,
            "ready": True,
            "client_id": client.id,
            "package_slug": purchase.package_slug,
            "intake_url": intake_url,
            "intake_complete": client.intake_status == IntakeStatus.COMPLETE.value,
        }
    )


@router.get("/intake/{token}", response_class=HTMLResponse)
def token_intake_form(request: Request, token: str, db: Session = Depends(get_db)):
    client = _find_client_by_token(db, token)
    if not client:
        return templates.TemplateResponse(
            "token_intake.html",
            {"request": request, "error": "Invalid intake link.", "client": None, "token": token},
            status_code=403,
        )

    from app.intake_tokens import verify_intake_token

    token_error = verify_intake_token(client, token)
    if token_error:
        return templates.TemplateResponse(
            "token_intake.html",
            {"request": request, "error": token_error, "client": None, "token": token},
            status_code=403,
        )

    return templates.TemplateResponse(
        "token_intake.html",
        {
            "request": request,
            "error": None,
            **_token_intake_template_context(client=client, token=token),
        },
    )


@router.post("/intake/{token}")
def submit_token_intake(
    request: Request,
    token: str,
    name: str = Form(...),
    email: str = Form(""),
    target_role: str = Form(...),
    experience_education: str = Form(...),
    experience_projects: str = Form(...),
    experience_work: str = Form(...),
    skills: str = Form(...),
    career_goals: str = Form(""),
    linkedin_url: str = Form(""),
    github_url: str = Form(...),
    portfolio_template: str = Form(""),
    resume_url: str = Form(""),
    existing_portfolio_url: str = Form(""),
    certifications: str = Form(""),
    job_timeline: str = Form(""),
    additional_notes: str = Form(""),
    attestation: str | None = Form(None),
    prerequisites_attestation: str | None = Form(None),
    db: Session = Depends(get_db),
):
    client = _find_client_by_token(db, token)
    if not client:
        return templates.TemplateResponse(
            "token_intake.html",
            {"request": request, "error": "Invalid intake link.", "client": None, "token": token},
            status_code=403,
        )

    prefill = _intake_prefill_from_form(
        name=name,
        email=email or client.email or "",
        target_role=target_role,
        experience_education=experience_education,
        experience_projects=experience_projects,
        experience_work=experience_work,
        skills=skills,
        career_goals=career_goals,
        linkedin_url=linkedin_url,
        github_url=github_url,
        portfolio_template=portfolio_template,
        resume_url=resume_url,
        existing_portfolio_url=existing_portfolio_url,
        certifications=certifications,
        job_timeline=job_timeline,
        additional_notes=additional_notes,
    )

    try:
        complete_token_intake(
            db,
            client,
            token=token,
            name=name,
            email=email or client.email or "",
            target_role=target_role,
            experience_education=experience_education,
            experience_projects=experience_projects,
            experience_work=experience_work,
            skills=skills,
            linkedin_url=linkedin_url.strip() or None,
            github_url=github_url.strip() or None,
            career_goals=career_goals.strip() or None,
            certifications=certifications.strip() or None,
            job_timeline=job_timeline.strip() or None,
            portfolio_template=portfolio_template.strip() or None,
            resume_url=resume_url.strip() or None,
            existing_portfolio_url=existing_portfolio_url.strip() or None,
            additional_notes=additional_notes.strip() or None,
            attestation_checked=(attestation or "").strip().lower() == "on",
            prerequisites_attestation_checked=(prerequisites_attestation or "").strip().lower() == "on",
        )
    except IntakeAccessError as exc:
        return templates.TemplateResponse(
            "token_intake.html",
            {
                "request": request,
                "error": str(exc),
                **_token_intake_template_context(client=client, token=token, prefill=prefill),
            },
            status_code=403,
        )
    except IntakeValidationError as exc:
        return templates.TemplateResponse(
            "token_intake.html",
            {
                "request": request,
                "error": str(exc),
                **_token_intake_template_context(client=client, token=token, prefill=prefill),
            },
            status_code=422,
        )
    except PersistenceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return templates.TemplateResponse(
        "token_intake_complete.html",
        {"request": request, "client_name": client.name},
    )
