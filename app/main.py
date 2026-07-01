import logging
from pathlib import Path
from time import perf_counter

try:
    from dotenv import load_dotenv

    load_dotenv(encoding="utf-8-sig")
except ImportError:
    pass

from app.logging_config import setup_logging
from fastapi import Depends, FastAPI, Form, HTTPException, Query, Request, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.admin_auth import ops_password, require_ops_auth, set_ops_session, verify_ops_password
from app.dashboard_views import build_dashboard_context
from app.client_views import build_client_detail_context
from app.lead_service import LeadPersistenceError, update_lead_status
from app.lead_views import build_lead_pipeline_context
from app.metrics_service import build_metrics_summary
from app.outcome_service import OutcomePersistenceError, OutcomeValidationError, upsert_client_outcome
from app.database import Base, engine, get_db
from app.health import build_health_payload
from app.intake_context import intake_form_context
from app.intake_tokens import assign_intake_token
from app.delivery_kits import get_delivery_doc_spec, render_delivery_doc
from app.intake_validation import IntakeValidationError, resolve_client_package_slug
from app.package_config import get_package
from app.migrations import run_migrations
from app.models import (
    Client,
    Deliverable,
    DeliverableStatus,
    IntakeStatus,
    Lead,
    LeadStatus,
    PipelineStatus,
    Project,
    Task,
    TaskStatus,
)
from app.stripe_checkout import base_url
from app.jinja_env import templates
from app.pipeline_config import ROLLBACK_POLICY

setup_logging()

from app.services import (
    PersistenceError,
    WorkflowError,
    create_client_with_project,
    update_deliverable_status,
    update_deliverable_url,
    update_project_status,
    update_task_status,
)

Base.metadata.create_all(bind=engine)
run_migrations(engine)

from app.site_branding import site_name

app = FastAPI(title=f"{site_name()} OS", version="0.1.0")
_access_logger = logging.getLogger("app.access")


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    path = request.url.path
    skip_logging = path == "/health" or path.startswith("/static")
    started = perf_counter()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        if not skip_logging:
            duration_ms = round((perf_counter() - started) * 1000, 2)
            _access_logger.info(
                "request completed",
                extra={
                    "http.method": request.method,
                    "http.path": path,
                    "http.status_code": status_code,
                    "http.duration_ms": duration_ms,
                },
            )

from app.routes.revenue import router as revenue_router
from app.routes.sales import router as sales_router

app.include_router(sales_router)
app.include_router(revenue_router)

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

_GOOGLE_SITE_VERIFICATION_HTML = "googleb827bf20974fd6a1.html"


@app.get(f"/{_GOOGLE_SITE_VERIFICATION_HTML}", response_class=PlainTextResponse)
def google_site_verification_file() -> PlainTextResponse:
    return PlainTextResponse(f"google-site-verification: {_GOOGLE_SITE_VERIFICATION_HTML}")


@app.get("/health")
def health_check(request: Request, db: Session = Depends(get_db)):
    from fastapi.responses import JSONResponse

    accept = (request.headers.get("accept") or "").lower()
    if "text/html" in accept and "application/json" not in accept.split(",")[0].strip():
        return RedirectResponse(url="/status", status_code=302)

    payload = build_health_payload(db)
    status_code = 200 if payload["status"] != "unhealthy" else 503
    return JSONResponse(content=payload, status_code=status_code)


@app.exception_handler(HTTPException)
async def ops_login_redirect(request: Request, exc: HTTPException):
    if exc.status_code == status.HTTP_307_TEMPORARY_REDIRECT and exc.headers:
        location = exc.headers.get("Location")
        if location:
            return RedirectResponse(url=location, status_code=303)
    return await http_exception_handler(request, exc)


@app.get("/ops")
def ops_entry() -> RedirectResponse:
    """Bookmark-friendly entry to the password-protected delivery dashboard."""
    return RedirectResponse(url="/login?next=/dashboard", status_code=302)


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request, next: str = Query("/dashboard")):
    safe_next = next if next.startswith("/") and not next.startswith("//") else "/dashboard"
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": None, "next": safe_next},
    )


@app.post("/login")
def login_submit(
    request: Request,
    password: str = Form(...),
    next: str = Form("/dashboard"),
):
    safe_next = next if next.startswith("/") and not next.startswith("//") else "/dashboard"
    if not verify_ops_password(password):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Incorrect password.", "next": safe_next},
            status_code=401,
        )
    response = RedirectResponse(url=safe_next, status_code=303)
    set_ops_session(response, ops_password())
    return response


def _load_client(db: Session, client_id: int) -> Client | None:
    return db.scalar(
        select(Client)
        .where(Client.id == client_id)
        .options(
            joinedload(Client.project).joinedload(Project.tasks),
            joinedload(Client.project).joinedload(Project.deliverables),
            joinedload(Client.purchase),
        )
    )


def _render_client_detail(
    request: Request,
    db: Session,
    client_id: int,
    *,
    error: str | None = None,
    issued_intake_url: str | None = None,
    status_code: int = 200,
) -> HTMLResponse:
    client = _load_client(db, client_id)
    context = build_client_detail_context(db, client, error=error)
    context["request"] = request
    context["rollback_policy"] = ROLLBACK_POLICY.value
    context["issued_intake_url"] = issued_intake_url
    return templates.TemplateResponse("client_detail.html", context, status_code=status_code)


def _client_redirect(client_id: int, fragment: str = "") -> RedirectResponse:
    path = f"/clients/{client_id}"
    if fragment:
        path = f"{path}#{fragment}"
    return RedirectResponse(url=path, status_code=303)


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    status: str | None = Query(None),
    hide_demo: bool = Query(False),
    db: Session = Depends(get_db),
    _ops: str = Depends(require_ops_auth),
):
    status_filter: PipelineStatus | None = None
    if status:
        try:
            status_filter = PipelineStatus(status)
        except ValueError:
            pass

    context = build_dashboard_context(db, status_filter=status_filter, hide_demo=hide_demo)
    context.update(build_lead_pipeline_context(db))
    context.update(build_metrics_summary(db))
    context["request"] = request
    return templates.TemplateResponse("dashboard.html", context)


@app.post("/leads/{lead_id}/status", response_class=HTMLResponse)
def change_lead_status(
    request: Request,
    lead_id: int,
    lead_status: str = Form(...),
    db: Session = Depends(get_db),
    _ops: str = Depends(require_ops_auth),
):
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    try:
        new_status = LeadStatus(lead_status)
    except ValueError:
        context = build_dashboard_context(db)
        context.update(build_lead_pipeline_context(db))
        context["request"] = request
        context["lead_error"] = "Invalid lead status."
        return templates.TemplateResponse("dashboard.html", context, status_code=422)

    try:
        update_lead_status(db, lead, new_status)
    except LeadPersistenceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return RedirectResponse(url="/dashboard#leads", status_code=303)


@app.get("/intake", response_class=HTMLResponse)
def intake_form(request: Request, _ops: str = Depends(require_ops_auth)):
    ctx = intake_form_context(package_slug="foundation", show_package_select=True)
    return templates.TemplateResponse(
        "intake.html",
        {"request": request, "error": None, **ctx},
    )


@app.post("/intake")
def submit_intake(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    package_slug: str = Form("foundation"),
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
    _ops: str = Depends(require_ops_auth),
):
    prefill = {
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
    try:
        client = create_client_with_project(
            db,
            package_slug=package_slug,
            name=name,
            email=email,
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
    except IntakeValidationError as exc:
        ctx = intake_form_context(
            package_slug=package_slug,
            show_package_select=True,
            prefill=prefill,
        )
        return templates.TemplateResponse(
            "intake.html",
            {"request": request, "error": str(exc), **ctx},
            status_code=422,
        )
    except PersistenceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return RedirectResponse(url=f"/clients/{client.id}", status_code=303)


@app.get("/clients/{client_id}", response_class=HTMLResponse)
def client_detail(
    request: Request,
    client_id: int,
    db: Session = Depends(get_db),
    _ops: str = Depends(require_ops_auth),
):
    try:
        return _render_client_detail(request, db, client_id)
    except Exception as exc:
        context = build_client_detail_context(
            db,
            None,
            error=f"Page render error: {exc}",
        )
        context["request"] = request
        context["rollback_policy"] = ROLLBACK_POLICY.value
        return templates.TemplateResponse("client_detail.html", context, status_code=200)


@app.get("/clients/{client_id}/delivery-doc/{doc_key}")
def client_delivery_doc(
    client_id: int,
    doc_key: str,
    raw: int = Query(0),
    db: Session = Depends(get_db),
    _ops: str = Depends(require_ops_auth),
):
    client = _load_client(db, client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")

    spec = get_delivery_doc_spec(doc_key)
    if spec is None:
        raise HTTPException(status_code=404, detail="Unknown delivery document.")

    package_slug = resolve_client_package_slug(client.package_slug, client.package_tier)
    if spec.deliverable_name not in get_package(package_slug).deliverables:
        raise HTTPException(status_code=404, detail="Document not in client package.")

    try:
        body = render_delivery_doc(spec, client, package_slug=package_slug)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    filename = f"{doc_key}-{client_id}.md"
    headers = {}
    if raw:
        headers["Content-Disposition"] = f'attachment; filename="{filename}"'

    return PlainTextResponse(body, media_type="text/markdown; charset=utf-8", headers=headers)


@app.post("/clients/{client_id}/issue-intake-link", response_class=HTMLResponse)
def issue_client_intake_link(
    request: Request,
    client_id: int,
    db: Session = Depends(get_db),
    _ops: str = Depends(require_ops_auth),
):
    client = _load_client(db, client_id)
    if client is None:
        return _render_client_detail(request, db, client_id, error="Client not found.", status_code=404)
    if client.intake_status == IntakeStatus.COMPLETE.value:
        return _render_client_detail(
            request, db, client_id, error="Intake already complete.", status_code=422
        )
    if client.customer_lifecycle == "archived":
        return _render_client_detail(
            request, db, client_id, error="Client is archived.", status_code=422
        )
    token = assign_intake_token(client)
    db.commit()
    intake_url = f"{base_url()}/intake/{token}"
    return _render_client_detail(request, db, client_id, issued_intake_url=intake_url)


@app.post("/clients/{client_id}/status", response_class=HTMLResponse)
def change_project_status(
    request: Request,
    client_id: int,
    status: str = Form(...),
    db: Session = Depends(get_db),
    _ops: str = Depends(require_ops_auth),
):
    client = db.scalar(
        select(Client).where(Client.id == client_id).options(joinedload(Client.project))
    )
    if not client or not client.project:
        raise HTTPException(status_code=404, detail="Client not found")

    try:
        new_status = PipelineStatus(status)
    except ValueError:
        return _render_client_detail(
            request, db, client_id, error="Invalid pipeline status.", status_code=422
        )

    try:
        update_project_status(db, client.project, new_status)
    except WorkflowError as exc:
        return _render_client_detail(request, db, client_id, error=str(exc), status_code=422)
    except PersistenceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return _render_client_detail(request, db, client_id, status_code=200)


@app.post("/clients/{client_id}/outcome", response_class=HTMLResponse)
def save_client_outcome(
    request: Request,
    client_id: int,
    before_problem: str = Form(...),
    after_result: str = Form(...),
    testimonial: str = Form(...),
    display_permission: str = Form(""),
    db: Session = Depends(get_db),
    _ops: str = Depends(require_ops_auth),
):
    client = _load_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    try:
        upsert_client_outcome(
            db,
            client_id=client_id,
            before_problem=before_problem,
            after_result=after_result,
            testimonial=testimonial,
            display_permission=display_permission == "yes",
        )
    except OutcomeValidationError as exc:
        return _render_client_detail(request, db, client_id, error=str(exc), status_code=422)
    except OutcomePersistenceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return _render_client_detail(request, db, client_id, status_code=200)


@app.post("/tasks/{task_id}/status")
def change_task_status(
    task_id: int,
    status: str = Form(...),
    db: Session = Depends(get_db),
    _ops: str = Depends(require_ops_auth),
):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        new_status = TaskStatus(status)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Invalid task status.") from exc

    try:
        update_task_status(db, task, new_status)
    except PersistenceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    project = db.get(Project, task.project_id)
    client_id = project.client_id if project else 0
    return _client_redirect(client_id, fragment="tasks")


@app.post("/deliverables/{deliverable_id}/status")
def change_deliverable_status(
    deliverable_id: int,
    status: str = Form(...),
    db: Session = Depends(get_db),
    _ops: str = Depends(require_ops_auth),
):
    deliverable = db.get(Deliverable, deliverable_id)
    if not deliverable:
        raise HTTPException(status_code=404, detail="Deliverable not found")

    try:
        new_status = DeliverableStatus(status)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Invalid deliverable status.") from exc

    try:
        update_deliverable_status(db, deliverable, new_status)
    except PersistenceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    project = db.get(Project, deliverable.project_id)
    client_id = project.client_id if project else 0
    return _client_redirect(client_id, fragment="deliverables")


@app.post("/deliverables/{deliverable_id}/url")
def update_deliverable_url_route(
    deliverable_id: int,
    url: str = Form(""),
    db: Session = Depends(get_db),
    _ops: str = Depends(require_ops_auth),
):
    deliverable = db.get(Deliverable, deliverable_id)
    if not deliverable:
        raise HTTPException(status_code=404, detail="Deliverable not found")

    try:
        update_deliverable_url(db, deliverable, url.strip() or None)
    except PersistenceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    project = db.get(Project, deliverable.project_id)
    client_id = project.client_id if project else 0
    return _client_redirect(client_id, fragment="deliverables")
