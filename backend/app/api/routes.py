from fastapi import APIRouter, HTTPException

from app.models.ticket import TicketDetail, TicketSummary
from app.services.ticket_service import (
    get_ticket_detail,
    list_tickets,
)


router = APIRouter(prefix="/api")


@router.get("/tickets", response_model=list[TicketSummary])
def get_tickets() -> list[TicketSummary]:
    return list_tickets()

@router.get(
    "/tickets/{ticket_id}",
    response_model=TicketDetail,
)
def get_ticket(ticket_id: str) -> TicketDetail:
    ticket = get_ticket_detail(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return ticket