from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.workflow_run import WorkflowRun

router = APIRouter(tags=["Dashboard"])

templates = Jinja2Templates(directory="app/templates")

def format_datetime(value):
    if value is None:
        return "-"

    return value.strftime("%b %d, %Y %I:%M %p UTC")


def format_duration(started_at, completed_at):
    if started_at is None or completed_at is None:
        return "-"

    seconds = (completed_at - started_at).total_seconds()
    return f"{seconds:.2f} sec"


templates.env.filters["format_datetime"] = format_datetime
templates.env.filters["format_duration"] = format_duration


@router.get("/dashboard")
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
):
    workflow_runs = (
        db.query(WorkflowRun)
        .order_by(WorkflowRun.created_at.desc())
        .limit(25)
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "workflow_runs": workflow_runs,
        },
    )


@router.get("/dashboard/workflow-runs/{workflow_run_id}")
def workflow_run_details(
    workflow_run_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
):
    workflow_run = (
        db.query(WorkflowRun)
        .filter(WorkflowRun.id == workflow_run_id)
        .first()
    )

    if workflow_run is None:
        raise HTTPException(status_code=404, detail="Workflow run not found")

    audit_logs = (
        db.query(AuditLog)
        .filter(AuditLog.workflow_run_id == workflow_run_id)
        .order_by(AuditLog.created_at.asc())
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="workflow_run_details.html",
        context={
            "workflow_run": workflow_run,
            "audit_logs": audit_logs,
        },
    )