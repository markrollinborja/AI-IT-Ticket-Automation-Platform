from fastapi import APIRouter

from app.schemas.jira import JiraWebhookEvent
from app.schemas.ticket import TicketCreate, TicketResponse, TicketSource
from app.services.jira_service import jira_service
from app.services.ticket_service import ticket_service

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/jira", response_model=TicketResponse)
def handle_jira_webhook(event: JiraWebhookEvent):
    ticket = TicketCreate(
        title=event.issue.fields.summary,
        description=event.issue.fields.description,
        created_by=event.issue.fields.reporter.displayName,
        source=TicketSource.JIRA,
    )

    processed_ticket = ticket_service.create_ticket(ticket)

    jira_service.update_issue_priority(
        issue_key=event.issue.key,
        priority=processed_ticket.priority,
    )

    return processed_ticket