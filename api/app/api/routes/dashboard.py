from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.workflow_run import WorkflowRun

router = APIRouter(tags=["Dashboard"])

templates = Jinja2Templates(directory="app/templates")


def format_datetime(value):
    if value is None:
        return "-"

    chicago_time = value.astimezone(ZoneInfo("America/Chicago"))
    return chicago_time.strftime("%b %d, %Y %I:%M %p %Z")


def format_status(value):
    if not value:
        return "-"

    return value.replace("_", " ").title()


def format_priority(value):
    if not value:
        return "-"

    return value.title()


def format_category(value):
    if not value:
        return "-"

    category_map = {
        "ai": "AI",
        "rule_engine": "Rule Engine",
        "rule_engine_or_ai": "Rule Engine or AI",
    }

    return category_map.get(value, value.replace("_", " ").title())


def format_confidence(value):
    if value is None:
        return "-"

    return f"{round(value * 100)}%"


def format_audit_event(value):
    event_map = {
        "workflow_started": "Workflow Started",
        "approval_required": "Approval Required",
        "ticket_classified": "Priority Classified",
        "jira_priority_updated": "Jira Updated",
        "workflow_completed": "Processing Completed",
        "workflow_failed": "Processing Failed",
    }

    return event_map.get(value, value.replace("_", " ").title())


def format_duration(started_at, completed_at):
    if started_at is None or completed_at is None:
        return "-"

    seconds = (completed_at - started_at).total_seconds()
    return f"{seconds:.2f} sec"


templates.env.filters["format_datetime"] = format_datetime
templates.env.filters["format_status"] = format_status
templates.env.filters["format_priority"] = format_priority
templates.env.filters["format_category"] = format_category
templates.env.filters["format_confidence"] = format_confidence
templates.env.filters["format_audit_event"] = format_audit_event
templates.env.filters["format_duration"] = format_duration


@router.get("/dashboard")
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
):
    workflow_runs = (
        db.query(WorkflowRun)
        .options(joinedload(WorkflowRun.ticket))
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
        .options(joinedload(WorkflowRun.ticket))
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
