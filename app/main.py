from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from fastapi import Depends, FastAPI, Form, HTTPException, Query, Request, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
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
from app.intake_validation import IntakeValidationError
from app.migrations import run_migrations
from app.models import (
    Client,
    Deliverable,
    DeliverableStatus,
    Lead,
    LeadStatus,
    PipelineStatus,
    Project,
    Task,
    TaskStatus,
)
from app.pipeline_config import ROLLBACK_POLICY
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

app = FastAPI(title="Career Systems OS", version="0.1.0")

from app.routes.revenue import router as revenue_router
from app.routes.sales import router as sales_router

app.include_router(sales_router)
app.include_router(revenue_router)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.exception_handler(HTTPException)
async def ops_login_redirect(request: Request, exc: HTTPException):
    if exc.status_code == status.HTTP_307_TEMPORARY_REDIRECT and exc.headers:
        location = exc.headers.get("Location")
        if location:
            return RedirectResponse(url=location, status_code=303)
    return await http_exception_handler(request, exc)


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
    status_code: int = 200,
) -> HTMLResponse:
    client = _load_client(db, client_id)
    context = build_client_detail_context(db, client, error=error)
    context["request"] = request
    context["rollback_policy"] = ROLLBACK_POLICY.value
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
    return templates.TemplateResponse("intake.html", {"request": request, "error": None})


@app.post("/intake")
def submit_intake(
    request: Request,
    name: str = Form(...),
    target_role: str = Form(...),
    experience_education: str = Form(...),
    experience_projects: str = Form(...),
    experience_work: str = Form(...),
    skills: str = Form(...),
    linkedin_url: str = Form(""),
    github_url: str = Form(""),
    package_tier: str = Form("Basic"),
    db: Session = Depends(get_db),
    _ops: str = Depends(require_ops_auth),
):
    try:
        client = create_client_with_project(
            db,
            name=name,
            target_role=target_role,
            experience_education=experience_education,
            experience_projects=experience_projects,
            experience_work=experience_work,
            skills=skills,
            linkedin_url=linkedin_url.strip() or None,
            github_url=github_url.strip() or None,
            package_tier=package_tier,
        )
    except IntakeValidationError as exc:
        return templates.TemplateResponse(
            "intake.html",
            {"request": request, "error": str(exc)},
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
