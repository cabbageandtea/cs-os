"""Stripe checkout, webhooks, and token-based intake routes."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.intake_tokens import assign_intake_token
from app.intake_validation import IntakeValidationError
from app.models import Client, IntakeStatus, Purchase, PurchaseStatus
from app.package_config import PACKAGES, PackageConfigError
from app.services import IntakeAccessError, PersistenceError, complete_token_intake
from app.stripe_checkout import StripeCheckoutError, base_url, create_checkout_session
from app.stripe_webhook import (
    WebhookConfigError,
    WebhookSignatureError,
    process_webhook,
)

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


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
    packages = [
        {
            "slug": slug,
            "display_name": PACKAGES[slug].display_name,
            "tagline": PACKAGES[slug].tagline,
            "default_price_cents": PACKAGES[slug].default_price_cents,
            "featured": slug == "launch",
        }
        for slug in ("foundation", "launch", "accelerator")
    ]
    return templates.TemplateResponse(
        "checkout.html",
        {"request": request, "packages": packages, "error": None},
    )


@router.post("/checkout/create")
def checkout_create(
    request: Request,
    package_slug: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        _, redirect_url = create_checkout_session(db, package_slug)
    except (PackageConfigError, StripeCheckoutError) as exc:
        packages = [
            {
                "slug": slug,
                "display_name": PACKAGES[slug].display_name,
                "tagline": PACKAGES[slug].tagline,
                "default_price_cents": PACKAGES[slug].default_price_cents,
                "featured": slug == "launch",
            }
            for slug in ("foundation", "launch", "accelerator")
        ]
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
    if client.intake_status == IntakeStatus.PENDING.value and not purchase.intake_link_delivered:
        token = assign_intake_token(client)
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

    package_name = client.package_tier or "Package"
    return templates.TemplateResponse(
        "token_intake.html",
        {
            "request": request,
            "error": None,
            "client": client,
            "token": token,
            "package_name": package_name,
            "prefill_name": client.name if client.name != "Pending Intake" else "",
            "prefill_email": client.email or "",
        },
    )


@router.post("/intake/{token}")
def submit_token_intake(
    request: Request,
    token: str,
    name: str = Form(...),
    target_role: str = Form(...),
    experience_education: str = Form(...),
    experience_projects: str = Form(...),
    experience_work: str = Form(...),
    skills: str = Form(...),
    linkedin_url: str = Form(""),
    github_url: str = Form(""),
    db: Session = Depends(get_db),
):
    client = _find_client_by_token(db, token)
    if not client:
        return templates.TemplateResponse(
            "token_intake.html",
            {"request": request, "error": "Invalid intake link.", "client": None, "token": token},
            status_code=403,
        )

    try:
        complete_token_intake(
            db,
            client,
            token=token,
            name=name,
            target_role=target_role,
            experience_education=experience_education,
            experience_projects=experience_projects,
            experience_work=experience_work,
            skills=skills,
            linkedin_url=linkedin_url.strip() or None,
            github_url=github_url.strip() or None,
        )
    except IntakeAccessError as exc:
        return templates.TemplateResponse(
            "token_intake.html",
            {
                "request": request,
                "error": str(exc),
                "client": client,
                "token": token,
                "package_name": client.package_tier,
                "prefill_name": name,
                "prefill_email": client.email or "",
            },
            status_code=403,
        )
    except IntakeValidationError as exc:
        return templates.TemplateResponse(
            "token_intake.html",
            {
                "request": request,
                "error": str(exc),
                "client": client,
                "token": token,
                "package_name": client.package_tier,
                "prefill_name": name,
                "prefill_email": client.email or "",
            },
            status_code=422,
        )
    except PersistenceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return templates.TemplateResponse(
        "token_intake_complete.html",
        {"request": request, "client_name": client.name},
    )
