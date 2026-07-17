import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.models.ticket import Ticket
from app.models.workflow_run import WorkflowRun
from app.schemas.jira import JiraWebhookEvent
from app.schemas.ticket import TicketCreate, TicketPriority, TicketSource
from app.services.approval_policy_service import approval_policy_service
from app.services.approval_service import approval_service
from app.services.audit_log_service import audit_log_service
from app.services.jira_service import jira_service
from app.services.slack_notification_service import slack_notification_service
from app.services.ticket_persistence_service import ticket_persistence_service
from app.services.ticket_service import ticket_service
from app.services.workflow_run_service import workflow_run_service

logger = logging.getLogger(__name__)


def format_processed_at() -> str:
    return datetime.now(ZoneInfo("America/Chicago")).strftime("%b %d, %Y %I:%M %p %Z")


def format_priority(priority: str) -> str:
    priority_map = {
        "critical": "Critical",
        "high": "High",
        "medium": "Medium",
        "low": "Low",
    }

    return priority_map.get(priority.lower(), priority.title())


def format_classification_source(classification_source: str) -> str:
    source_map = {
        "ai": "AI",
        "rule_engine": "Rule Engine",
    }

    return source_map.get(classification_source, classification_source)


def truncate_text(text: str, max_length: int = 500) -> str:
    if not text:
        return "-"

    cleaned_text = text.strip()

    if len(cleaned_text) <= max_length:
        return cleaned_text

    return f"{cleaned_text[:max_length].rstrip()}..."


class WorkflowService:
    def process_jira_issue(
        self,
        db: Session,
        event: JiraWebhookEvent,
    ) -> dict:
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

            approval_result = approval_policy_service.evaluate(
                reporter=persisted_ticket.reporter,
                title=persisted_ticket.title,
                description=persisted_ticket.description,
            )

            if approval_result.approval_required:
                return self._gate_for_approval(
                    db=db,
                    workflow_run=workflow_run,
                    persisted_ticket=persisted_ticket,
                    priority=processed_ticket.priority,
                    classification_source=processed_ticket.classification_source,
                    ai_priority=processed_ticket.ai_priority,
                    ai_confidence_score=processed_ticket.ai_confidence_score,
                    reason=approval_result.reason,
                )

            return self._finalize_workflow(
                db=db,
                workflow_run=workflow_run,
                persisted_ticket=persisted_ticket,
                priority=processed_ticket.priority,
                classification_source=processed_ticket.classification_source,
                ai_priority=processed_ticket.ai_priority,
                ai_confidence_score=processed_ticket.ai_confidence_score,
            )

        except Exception as error:
            self._handle_workflow_failure(db, workflow_run, persisted_ticket, error)
            raise

    def resume_after_approval(
        self,
        db: Session,
        workflow_run: WorkflowRun,
        persisted_ticket: Ticket,
    ) -> dict:
        """
        Runs the finalize step for a workflow run that was previously
        gated for approval. Reuses the classification already computed and
        stored on the workflow run during the gate step - approving a
        ticket doesn't reclassify it, it just unblocks what was already
        decided.
        """
        try:
            priority = TicketPriority(workflow_run.final_priority)
            ai_priority = TicketPriority(workflow_run.ai_priority) if workflow_run.ai_priority else None

            return self._finalize_workflow(
                db=db,
                workflow_run=workflow_run,
                persisted_ticket=persisted_ticket,
                priority=priority,
                classification_source=workflow_run.final_category,
                ai_priority=ai_priority,
                ai_confidence_score=workflow_run.ai_confidence_score,
            )
        except Exception as error:
            self._handle_workflow_failure(db, workflow_run, persisted_ticket, error)
            raise

    def _gate_for_approval(
        self,
        db: Session,
        workflow_run: WorkflowRun,
        persisted_ticket: Ticket,
        priority: TicketPriority,
        classification_source: str,
        ai_priority: TicketPriority | None,
        ai_confidence_score: float | None,
        reason: str | None,
    ) -> dict:
        approval_reason = reason or "Human approval required."

        workflow_run_service.mark_pending_approval(
            db=db,
            workflow_run=workflow_run,
            approval_reason=approval_reason,
            final_priority=priority,
            classification_source=classification_source,
            ai_priority=ai_priority,
            ai_confidence_score=ai_confidence_score,
        )

        approval_service.create_pending(db=db, workflow_run_id=workflow_run.id)

        audit_log_service.record_event(
            db=db,
            workflow_run_id=workflow_run.id,
            event="approval_required",
            message=approval_reason,
        )

        # Reflect the pending state in Jira immediately, unlike the final
        # priority which waits for a decision - so anyone looking at the
        # Jira issue directly can see it's stuck on approval, not silently
        # dropped.
        jira_service.set_issue_priority_name(
            issue_key=persisted_ticket.jira_issue_key,
            priority_name=jira_service.PENDING_APPROVAL_PRIORITY_NAME,
        )

        jira_pending_message = (
            f"Jira issue {persisted_ticket.jira_issue_key} priority set to "
            f"{jira_service.PENDING_APPROVAL_PRIORITY_NAME} while awaiting approval."
        )
        audit_log_service.record_event(
            db=db,
            workflow_run_id=workflow_run.id,
            event="jira_priority_updated",
            message=jira_pending_message,
        )

        logger.info(
            "Workflow pending approval for Jira issue %s",
            persisted_ticket.jira_issue_key,
        )

        slack_notification_service.send_message(
            f"""
:hourglass_flowing_sand: *Approval Required*

--------------------------------

*Ticket:* {persisted_ticket.title}

*Processed At:* {format_processed_at()}

*Reporter:* {persisted_ticket.reporter}

*Jira Issue:* {persisted_ticket.jira_issue_key}

*Classified Priority:* {format_priority(priority.value)}

*Reason:* {approval_reason}

--------------------------------

*Issue Description*

{truncate_text(persisted_ticket.description)}

--------------------------------
"""
        )

        return {
            "status": "pending_approval",
            "jira_issue_key": persisted_ticket.jira_issue_key,
            "approval_required": True,
            "approval_reason": approval_reason,
            "classified_priority": priority.value,
        }

    def _finalize_workflow(
        self,
        db: Session,
        workflow_run: WorkflowRun,
        persisted_ticket: Ticket,
        priority: TicketPriority,
        classification_source: str,
        ai_priority: TicketPriority | None,
        ai_confidence_score: float | None,
    ) -> dict:
        jira_service.update_issue_priority(
            issue_key=persisted_ticket.jira_issue_key,
            priority=priority,
        )

        jira_priority_update_message = (
            f"Jira issue {persisted_ticket.jira_issue_key} priority updated to {priority.value}."
        )
        audit_log_service.record_event(
            db=db,
            workflow_run_id=workflow_run.id,
            event="jira_priority_updated",
            message=jira_priority_update_message,
        )

        workflow_run_service.mark_completed(
            db=db,
            workflow_run=workflow_run,
            final_priority=priority,
            classification_source=classification_source,
            ai_priority=ai_priority,
            ai_confidence_score=ai_confidence_score,
        )

        audit_log_service.record_event(
            db=db,
            workflow_run_id=workflow_run.id,
            event="workflow_completed",
            message=f"Workflow completed for Jira issue {persisted_ticket.jira_issue_key}.",
        )

        slack_notification_service.send_message(
            f"""
:white_check_mark: *Ticket Processed*

--------------------------------

*Ticket:* {persisted_ticket.title}

*Processed At:* {format_processed_at()}

*Reporter:* {persisted_ticket.reporter}

*Jira Issue:* {persisted_ticket.jira_issue_key}

*Priority:* {format_priority(priority.value)}

*Classification:* {format_classification_source(classification_source)}

--------------------------------

*Issue Description*

{truncate_text(persisted_ticket.description)}

--------------------------------
"""
        )

        logger.info("Workflow completed for Jira issue %s", persisted_ticket.jira_issue_key)

        return {
            "status": "completed",
            "jira_issue_key": persisted_ticket.jira_issue_key,
            "priority": priority.value,
            "classification_source": classification_source,
        }

    def _handle_workflow_failure(
        self,
        db: Session,
        workflow_run: WorkflowRun,
        persisted_ticket: Ticket,
        error: Exception,
    ) -> None:
        logger.exception("Workflow failed for Jira issue %s", persisted_ticket.jira_issue_key)

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
*Ticket Processing Failed*

--------------------------------

*Ticket:* {persisted_ticket.title}

*Processed At:* {format_processed_at()}

*Reporter:* {persisted_ticket.reporter}

*Jira Issue:* {persisted_ticket.jira_issue_key}

*Error:* {type(error).__name__}

*Message:* {str(error)}

--------------------------------

*Issue Description*

{truncate_text(persisted_ticket.description)}

--------------------------------
"""
        )


workflow_service = WorkflowService()
