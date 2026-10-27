from fastapi import APIRouter

from .models import Ticket, TicketResult
from .services import classify_ticket


router = APIRouter()


@router.get("/")
def home() -> dict[str, str]:
    """Return a simple API status message."""

    return {"message": "CS415 Ticket API is running"}


# Example request body:
#   {"customer_name": "Ali", "message": "I have a payment issue", "urgent": true}
# Example response body:
#   {"category": "billing", "priority": "high"}


@router.post(
    "/tickets/classify",
    response_model=TicketResult,
)
def classify_ticket_endpoint(ticket: Ticket) -> TicketResult:
    """Classify an incoming customer support ticket."""

    return classify_ticket(ticket)