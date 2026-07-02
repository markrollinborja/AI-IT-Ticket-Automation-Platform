from uuid import UUID

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditLogService:
    def record_event(
        self,
        db: Session,
        workflow_run_id: UUID,
        event: str,
        message: str,
    ) -> AuditLog:
        audit_log = AuditLog(
            workflow_run_id=workflow_run_id,
            event=event,
            message=message,
        )

        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)

        return audit_log


audit_log_service = AuditLogService()