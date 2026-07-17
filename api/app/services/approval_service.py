from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.approval import Approval


class ApprovalService:
    def create_pending(
        self,
        db: Session,
        workflow_run_id: UUID,
    ) -> Approval:
        approval = Approval(
            workflow_run_id=workflow_run_id,
            status="pending",
        )

        db.add(approval)
        db.commit()
        db.refresh(approval)

        return approval

    def get_by_workflow_run_id(
        self,
        db: Session,
        workflow_run_id: UUID,
    ) -> Approval | None:
        return db.query(Approval).filter(Approval.workflow_run_id == workflow_run_id).first()

    def mark_approved(
        self,
        db: Session,
        approval: Approval,
        decided_by: str,
        decision_notes: str | None = None,
    ) -> Approval:
        approval.status = "approved"
        approval.decided_by = decided_by
        approval.decision_notes = decision_notes
        approval.decided_at = datetime.now(UTC)

        db.commit()
        db.refresh(approval)

        return approval

    def mark_rejected(
        self,
        db: Session,
        approval: Approval,
        decided_by: str,
        decision_notes: str | None = None,
    ) -> Approval:
        approval.status = "rejected"
        approval.decided_by = decided_by
        approval.decision_notes = decision_notes
        approval.decided_at = datetime.now(UTC)

        db.commit()
        db.refresh(approval)

        return approval


approval_service = ApprovalService()
