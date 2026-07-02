from datetime import UTC, datetime
from uuid import uuid4
from app.services.rule_engine import rule_engine

from app.schemas.ticket import (
    TicketCreate,
    TicketPriority,
    TicketResponse,
    TicketStatus,
)


class TicketService:
    def create_ticket(self, ticket: TicketCreate) -> TicketResponse:
        return TicketResponse(
            id=uuid4(),
            title=ticket.title,
            description=ticket.description,
            created_by=ticket.created_by,
            priority=rule_engine.determine_priority(ticket),
            status=TicketStatus.NEW,
            source=ticket.source,
            created_at=datetime.now(UTC),
        )


ticket_service = TicketService()