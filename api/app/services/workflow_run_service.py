from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.workflow_run import WorkflowRun
from app.schemas.ticket import TicketPriority


class WorkflowRunService:
    def start_workflow(
        self,
        db: Session,
        ticket_id: UUID,
    ) -> WorkflowRun:
        workflow_run = WorkflowRun(
            ticket_id=ticket_id,
            status="processing",
        )

        db.add(workflow_run)
        db.commit()
        db.refresh(workflow_run)

        return workflow_run

    def mark_completed(
        self,
        db: Session,
        workflow_run: WorkflowRun,
        final_priority: TicketPriority,
        classification_source: str,
    ) -> WorkflowRun:
        workflow_run.status = "completed"
        workflow_run.final_priority = final_priority.value
        workflow_run.final_category = classification_source
        workflow_run.completed_at = datetime.now(UTC)

        db.commit()
        db.refresh(workflow_run)

        return workflow_run

    def mark_failed(
        self,
        db: Session,
        workflow_run: WorkflowRun,
        error_type: str,
        error_message: str,
    ) -> WorkflowRun:
        workflow_run.status = "failed"
        workflow_run.error_type = error_type
        workflow_run.error_message = error_message
        workflow_run.completed_at = datetime.now(UTC)

        db.commit()
        db.refresh(workflow_run)

        return workflow_run


workflow_run_service = WorkflowRunService()