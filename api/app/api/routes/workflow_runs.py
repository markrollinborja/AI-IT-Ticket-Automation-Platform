from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.workflow_run import WorkflowRun

router = APIRouter(prefix="/workflow-runs", tags=["Workflow Runs"])


@router.get("")
def list_workflow_runs(db: Session = Depends(get_db)):
    return (
        db.query(WorkflowRun)
        .order_by(WorkflowRun.created_at.desc())
        .all()
    )


@router.get("/{workflow_run_id}")
def get_workflow_run(
    workflow_run_id: UUID,
    db: Session = Depends(get_db),
):
    workflow_run = (
        db.query(WorkflowRun)
        .filter(WorkflowRun.id == workflow_run_id)
        .first()
    )

    if workflow_run is None:
        raise HTTPException(status_code=404, detail="Workflow run not found")

    return workflow_run


@router.get("/{workflow_run_id}/audit-logs")
def get_workflow_run_audit_logs(
    workflow_run_id: UUID,
    db: Session = Depends(get_db),
):
    workflow_run = (
        db.query(WorkflowRun)
        .filter(WorkflowRun.id == workflow_run_id)
        .first()
    )

    if workflow_run is None:
        raise HTTPException(status_code=404, detail="Workflow run not found")

    return (
        db.query(AuditLog)
        .filter(AuditLog.workflow_run_id == workflow_run_id)
        .order_by(AuditLog.created_at.asc())
        .all()
    )