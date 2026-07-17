from datetime import UTC, datetime
from uuid import uuid4

from app.schemas.ticket import (
    TicketCreate,
    TicketPriority,
    TicketResponse,
    TicketStatus,
)
from app.services.ai_classification_service import ai_classification_service
from app.services.rule_engine import rule_engine


class TicketService:
    def create_ticket(self, ticket: TicketCreate) -> TicketResponse:
        rule_result = rule_engine.evaluate_ticket(ticket)

        ai_priority = None
        ai_confidence_score = None
        classification_source = "rule_engine"

        if rule_result.matched and rule_result.priority is not None:
            priority = rule_result.priority
        else:
            ai_result = ai_classification_service.classify_ticket(ticket)

            priority = ai_result.recommended_priority
            ai_priority = ai_result.recommended_priority
            ai_confidence_score = ai_result.confidence
            classification_source = "ai"

            if priority not in TicketPriority:
                priority = TicketPriority.MEDIUM

        return TicketResponse(
            id=uuid4(),
            title=ticket.title,
            description=ticket.description,
            created_by=ticket.created_by,
            priority=priority,
            status=TicketStatus.NEW,
            source=ticket.source,
            created_at=datetime.now(UTC),
            ai_priority=ai_priority,
            ai_confidence_score=ai_confidence_score,
            classification_source=classification_source,
        )


ticket_service = TicketService()
