from fastapi import APIRouter

from app.schemas.ticket import TicketCreate, TicketResponse
from app.services.ticket_service import ticket_service

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post("", response_model=TicketResponse)
def create_ticket(ticket: TicketCreate):
    return ticket_service.create_ticket(ticket)