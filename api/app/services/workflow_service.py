import logging

from sqlalchemy.orm import Session

from app.schemas.jira import JiraWebhookEvent
from app.schemas.ticket import TicketCreate, TicketResponse, TicketSource
from app.services.approval_policy_service import approval_policy_service
from app.services.audit_log_service import audit_log_service
from app.services.jira_service import jira_service
from app.services.slack_notification_service import slack_notification_service
from app.services.ticket_persistence_service import ticket_persistence_service
from app.services.ticket_service import ticket_service
from app.services.workflow_run_service import workflow_run_service

logger = logging.getLogger(__name__)


class WorkflowService:
    def process_jira_issue(
        self,
        db: Session,
        event: JiraWebhookEvent,
    ) -> TicketResponse | dict:
        logger.info("Workflow started for Jira issue %s", event.issue.key)

        persisted_ticket = ticket_persistence_service.get_or_create_from_jira_event(
            db=db,
            event=event,
        )

        logger.info("Ticket persisted for Jira issue %s", persisted_ticket.jira_issue_key)

        workflow_run = workflow_run_service.start_workflow(
            db=db,
            ticket_id=persisted_ticket.id,
        )

        audit_log_service.record_event(
            db=db,
            workflow_run_id=workflow_run.id,
            event="workflow_started",
            message=f"Workflow started for Jira issue {persisted_ticket.jira_issue_key}.",
        )

        approval_result = approval_policy_service.evaluate(
            reporter=persisted_ticket.reporter,
        )

        if approval_result.approval_required:
            workflow_run_service.mark_pending_approval(
                db=db,
                workflow_run=workflow_run,
                approval_reason=approval_result.reason or "Human approval required.",
            )

            audit_log_service.record_event(
                db=db,
                workflow_run_id=workflow_run.id,
                event="approval_required",
                message=approval_result.reason or "Human approval required.",
            )

            slack_notification_service.send_message(
                f"""
:warning: Approval Required

Issue: {persisted_ticket.jira_issue_key}
Reporter: {persisted_ticket.reporter}
Reason: {approval_result.reason}
"""
            )

            logger.info(
                "Workflow pending approval for Jira issue %s",
                persisted_ticket.jira_issue_key,
            )

            return {
                "status": "pending_approval",
                "jira_issue_key": persisted_ticket.jira_issue_key,
                "approval_required": True,
                "approval_reason": approval_result.reason,
            }

        try:
            ticket = TicketCreate(
                title=persisted_ticket.title,
                description=persisted_ticket.description,
                created_by=persisted_ticket.reporter,
                source=TicketSource.JIRA,
            )

            processed_ticket = ticket_service.create_ticket(ticket)

            audit_log_service.record_event(
                db=db,
                workflow_run_id=workflow_run.id,
                event="ticket_classified",
                message=f"Ticket classified with priority {processed_ticket.priority.value}.",
            )

            logger.info("Ticket classified with priority %s", processed_ticket.priority.value)

            jira_service.update_issue_priority(
                issue_key=persisted_ticket.jira_issue_key,
                priority=processed_ticket.priority,
            )

            audit_log_service.record_event(
                db=db,
                workflow_run_id=workflow_run.id,
                event="jira_priority_updated",
                message=f"Jira issue {persisted_ticket.jira_issue_key} priority updated to {processed_ticket.priority.value}.",
            )

            workflow_run_service.mark_completed(
                db=db,
                workflow_run=workflow_run,
                final_priority=processed_ticket.priority,
                classification_source="rule_engine_or_ai",
            )

            audit_log_service.record_event(
                db=db,
                workflow_run_id=workflow_run.id,
                event="workflow_completed",
                message=f"Workflow completed for Jira issue {persisted_ticket.jira_issue_key}.",
            )

            slack_notification_service.send_message(
                f"""
:white_check_mark: Workflow Completed

Issue: {persisted_ticket.jira_issue_key}
Priority: {processed_ticket.priority.value}
Status: Completed
Classification: Rule Engine
"""
            )

            logger.info("Workflow completed for Jira issue %s", persisted_ticket.jira_issue_key)

            return processed_ticket

        except Exception as error:
            logger.exception("Workflow failed for Jira issue %s", event.issue.key)

            workflow_run_service.mark_failed(
                db=db,
                workflow_run=workflow_run,
                error_type=type(error).__name__,
                error_message=str(error),
            )

            audit_log_service.record_event(
                db=db,
                workflow_run_id=workflow_run.id,
                event="workflow_failed",
                message=f"Workflow failed: {type(error).__name__}: {str(error)}",
            )

            slack_notification_service.send_message(
                f"""
:x: Workflow Failed

Issue: {persisted_ticket.jira_issue_key}
Error: {type(error).__name__}
Message: {str(error)}
"""
            )

            raise


workflow_service = WorkflowService()