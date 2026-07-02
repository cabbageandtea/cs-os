"""Portfolio fulfillment status and management API.

Clients and the frontend can poll these endpoints to check build progress.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.fulfillment_orchestrator import get_job_status, OrchestrationError
from app.models import PortfolioBuildJob, Purchase

router = APIRouter()


@router.get("/builds/status")
def get_build_status(
    session_id: str | None = Query(None),
    client_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    """
    Get portfolio build status.
    
    Query by either:
    - session_id (from Stripe checkout session)
    - client_id (authenticated clients)
    
    Returns current job state, portfolio URL (when complete), and error details.
    """
    if not session_id and not client_id:
        raise HTTPException(
            status_code=400,
            detail="Either session_id or client_id required"
        )

    if session_id:
        # Look up by Stripe session
        purchase = db.scalar(
            select(Purchase).where(Purchase.stripe_session_id == session_id)
        )
        if not purchase or not purchase.client_id:
            return JSONResponse({
                "status": "unknown",
                "message": "No purchase found for this session"
            })
        client_id = purchase.client_id

    if client_id:
        # Get latest job for this client
        job = db.scalar(
            select(PortfolioBuildJob)
            .where(PortfolioBuildJob.client_id == client_id)
            .order_by(PortfolioBuildJob.created_at.desc())
        )
        if not job:
            return JSONResponse({
                "status": "pending",
                "message": "No build job yet; likely still provisioning"
            })

        try:
            return get_job_status(db, job.id)
        except OrchestrationError as exc:
            return JSONResponse({
                "status": "error",
                "message": str(exc)
            }, status_code=500)

    return JSONResponse({"status": "unknown"})


@router.get("/builds/{job_id}")
def get_job_status_by_id(
    job_id: int,
    db: Session = Depends(get_db),
):
    """Get detailed status for a specific build job."""
    try:
        return get_job_status(db, job_id)
    except OrchestrationError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/builds/list")
def list_builds(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
):
    """List all portfolio builds (for dashboard/admin)."""
    from app.models import PortfolioBuildJobStatus

    query = select(PortfolioBuildJob).order_by(PortfolioBuildJob.created_at.desc())
    
    if status:
        # Validate status
        valid_statuses = [s.value for s in PortfolioBuildJobStatus]
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status; must be one of: {', '.join(valid_statuses)}"
            )
        query = query.where(PortfolioBuildJob.status == status)

    total = db.scalar(select(select(PortfolioBuildJob).with_entities()))
    jobs = db.scalars(query.offset(offset).limit(limit)).all()

    return JSONResponse({
        "total": total,
        "limit": limit,
        "offset": offset,
        "jobs": [
            {
                "id": job.id,
                "client_id": job.client_id,
                "status": job.status,
                "current_step": job.current_step,
                "portfolio_url": job.portfolio_url,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            }
            for job in jobs
        ]
    })
