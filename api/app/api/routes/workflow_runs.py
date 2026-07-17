from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.workflow_run import WorkflowRun
from app.schemas.approval import ApprovalDecision
from app.services.approval_service import approval_service
from app.services.audit_log_service import audit_log_service
from app.services.jira_service import jira_service
from app.services.slack_notification_service import slack_notification_service
from app.services.workflow_run_service import workflow_run_service
from app.services.workflow_service import workflow_service

router = APIRouter(prefix="/workflow-runs", tags=["Workflow Runs"])


def _get_pending_workflow_run(workflow_run_id: UUID, db: Session) -> WorkflowRun:
    workflow_run = (
        db.query(WorkflowRun)
        .options(joinedload(WorkflowRun.ticket))
        .filter(WorkflowRun.id == workflow_run_id)
        .first()
    )

    if workflow_run is None:
        raise HTTPException(status_code=404, detail="Workflow run not found")

    if workflow_run.status != "pending_approval":
        raise HTTPException(
            status_code=409,
            detail=f"Workflow run is not pending approval (current status: {workflow_run.status}).",
        )

    return workflow_run


@router.get("")
def list_workflow_runs(db: Session = Depends(get_db)):
    return db.query(WorkflowRun).order_by(WorkflowRun.created_at.desc()).all()


@router.get("/{workflow_run_id}")
def get_workflow_run(
    workflow_run_id: UUID,
    db: Session = Depends(get_db),
):
    workflow_run = db.query(WorkflowRun).filter(WorkflowRun.id == workflow_run_id).first()

    if workflow_run is None:
        raise HTTPException(status_code=404, detail="Workflow run not found")

    return workflow_run


@router.get("/{workflow_run_id}/audit-logs")
def get_workflow_run_audit_logs(
    workflow_run_id: UUID,
    db: Session = Depends(get_db),
):
    workflow_run = db.query(WorkflowRun).filter(WorkflowRun.id == workflow_run_id).first()

    if workflow_run is None:
        raise HTTPException(status_code=404, detail="Workflow run not found")

    return (
        db.query(AuditLog)
        .filter(AuditLog.workflow_run_id == workflow_run_id)
        .order_by(AuditLog.created_at.asc())
        .all()
    )


@router.post("/{workflow_run_id}/approve")
def approve_workflow_run(
    workflow_run_id: UUID,
    decision: ApprovalDecision,
    db: Session = Depends(get_db),
):
    workflow_run = _get_pending_workflow_run(workflow_run_id, db)
    approval = approval_service.get_by_workflow_run_id(db, workflow_run_id)

    if approval is None:
        # Shouldn't happen - every pending_approval workflow run gets an
        # Approval row created at the same time. Defensive check so a data
        # inconsistency surfaces as a clear error, not a confusing crash.
        raise HTTPException(status_code=500, detail="Approval record missing for this workflow run.")

    approval_service.mark_approved(
        db=db,
        approval=approval,
        decided_by=decision.decided_by,
        decision_notes=decision.decision_notes,
    )

    audit_log_service.record_event(
        db=db,
        workflow_run_id=workflow_run.id,
        event="approval_granted",
        message=f"Approved by {decision.decided_by}.",
    )

    return workflow_service.resume_after_approval(
        db=db,
        workflow_run=workflow_run,
        persisted_ticket=workflow_run.ticket,
    )


@router.post("/{workflow_run_id}/reject")
def reject_workflow_run(
    workflow_run_id: UUID,
    decision: ApprovalDecision,
    db: Session = Depends(get_db),
):
    workflow_run = _get_pending_workflow_run(workflow_run_id, db)
    approval = approval_service.get_by_workflow_run_id(db, workflow_run_id)

    if approval is None:
        raise HTTPException(status_code=500, detail="Approval record missing for this workflow run.")

    approval_service.mark_rejected(
        db=db,
        approval=approval,
        decided_by=decision.decided_by,
        decision_notes=decision.decision_notes,
    )

    workflow_run_service.mark_rejected(db=db, workflow_run=workflow_run)

    audit_log_service.record_event(
        db=db,
        workflow_run_id=workflow_run.id,
        event="approval_rejected",
        message=f"Rejected by {decision.decided_by}.",
    )

    # The rejection decision is already durably recorded above regardless
    # of what happens next - a Jira sync failure here means Jira is out of
    # sync, not that the rejection itself failed.
    jira_service.set_issue_priority_name(
        issue_key=workflow_run.ticket.jira_issue_key,
        priority_name=jira_service.REJECTED_PRIORITY_NAME,
    )

    audit_log_service.record_event(
        db=db,
        workflow_run_id=workflow_run.id,
        event="jira_priority_updated",
        message=f"Jira issue {workflow_run.ticket.jira_issue_key} priority set to "
        f"{jira_service.REJECTED_PRIORITY_NAME}.",
    )

    slack_notification_service.send_message(
        f"""
:no_entry: *Approval Rejected*

--------------------------------

*Ticket:* {workflow_run.ticket.title}

*Jira Issue:* {workflow_run.ticket.jira_issue_key}

*Rejected By:* {decision.decided_by}

*Notes:* {decision.decision_notes or "-"}

--------------------------------
"""
    )

    return {
        "status": "rejected",
        "jira_issue_key": workflow_run.ticket.jira_issue_key,
    }
