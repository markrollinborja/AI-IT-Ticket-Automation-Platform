from datetime import datetime, UTC
from uuid import uuid4

from fastapi import APIRouter

from app.schemas.ticket import (
    TicketCreate,
    TicketPriority,
    TicketResponse,
    TicketStatus,
)

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post("", response_model=TicketResponse)
def create_ticket(ticket: TicketCreate):
    return TicketResponse(
        id=uuid4(),
        title=ticket.title,
        description=ticket.description,
        created_by=ticket.created_by,
        priority=TicketPriority.MEDIUM,
        status=TicketStatus.NEW,
        source=ticket.source,
        created_at=datetime.now(UTC),
    )