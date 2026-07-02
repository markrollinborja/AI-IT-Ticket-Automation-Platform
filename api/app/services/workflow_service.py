import logging

from sqlalchemy.orm import Session

from app.schemas.jira import JiraWebhookEvent
from app.schemas.ticket import TicketCreate, TicketResponse, TicketSource
from app.services.jira_service import jira_service
from app.services.ticket_persistence_service import ticket_persistence_service
from app.services.ticket_service import ticket_service
from app.services.workflow_run_service import workflow_run_service

logger = logging.getLogger(__name__)


class WorkflowService:
    def process_jira_issue(
        self,
        db: Session,
        event: JiraWebhookEvent,
    ) -> TicketResponse:

        logger.info("Workflow started for Jira issue %s", event.issue.key)

        persisted_ticket = ticket_persistence_service.get_or_create_from_jira_event(
            db=db,
            event=event,
        )

        logger.info(
            "Ticket persisted for Jira issue %s",
            persisted_ticket.jira_issue_key,
        )

        workflow_run = workflow_run_service.start_workflow(
            db=db,
            ticket_id=persisted_ticket.id,
        )

        logger.info(
            "WorkflowRun created for ticket %s",
            persisted_ticket.id,
        )

        try:
            ticket = TicketCreate(
                title=persisted_ticket.title,
                description=persisted_ticket.description,
                created_by=persisted_ticket.reporter,
                source=TicketSource.JIRA,
            )

            processed_ticket = ticket_service.create_ticket(ticket)

            logger.info(
                "Ticket classified with priority %s",
                processed_ticket.priority.value,
            )

            jira_service.update_issue_priority(
                issue_key=persisted_ticket.jira_issue_key,
                priority=processed_ticket.priority,
            )

            logger.info(
                "Jira priority updated for issue %s",
                persisted_ticket.jira_issue_key,
            )

            workflow_run_service.mark_completed(
                db=db,
                workflow_run=workflow_run,
                final_priority=processed_ticket.priority,
                classification_source="rule_engine_or_ai",
            )

            logger.info(
                "Workflow completed for Jira issue %s",
                persisted_ticket.jira_issue_key,
            )

            return processed_ticket

        except Exception as error:
            logger.exception(
                "Workflow failed for Jira issue %s",
                event.issue.key,
            )

            workflow_run_service.mark_failed(
                db=db,
                workflow_run=workflow_run,
                error_type=type(error).__name__,
                error_message=str(error),
            )

            raise


workflow_service = WorkflowService()