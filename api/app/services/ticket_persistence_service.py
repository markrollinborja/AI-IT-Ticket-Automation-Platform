from sqlalchemy.orm import Session

from app.models.ticket import Ticket
from app.schemas.jira import JiraWebhookEvent


class TicketPersistenceService:
    def get_or_create_from_jira_event(
        self,
        db: Session,
        event: JiraWebhookEvent,
    ) -> Ticket:
        existing_ticket = db.query(Ticket).filter(Ticket.jira_issue_key == event.issue.key).first()

        if existing_ticket:
            return existing_ticket

        ticket = Ticket(
            jira_issue_key=event.issue.key,
            title=event.issue.fields.summary,
            description=event.issue.fields.description,
            reporter=event.issue.fields.reporter.displayName,
            source="jira",
        )

        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        return ticket


ticket_persistence_service = TicketPersistenceService()
