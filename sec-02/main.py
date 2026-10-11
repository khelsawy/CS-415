from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field


app = FastAPI(
    title="CS415 Ticket API",
    description="Lab 2 example: Pydantic + FastAPI",
    version="1.0.0",
)


class Ticket(BaseModel):
    """Represent an incoming customer support ticket."""

    customer_name: str = Field(min_length=2)
    message: str = Field(min_length=5)
    urgent: bool = False


class TicketResult(BaseModel):
    """Represent the classification result of a support ticket."""

    category: Literal["billing", "technical", "general"]
    priority: Literal["high", "normal"]

# Example usage:
#   TicketResult(category="billing", priority="high")    # ✅ works
#   TicketResult(category="sales", priority="high")      # ❌ ValidationError
#   TicketResult(category="billing", priority="urgent")  # ❌ ValidationError

def classify_ticket(ticket: Ticket) -> TicketResult:
    """Classify a customer support ticket and determine its priority."""

    text = ticket.message.lower()

    if "payment" in text or "invoice" in text:
        category = "billing"
    elif "login" in text or "error" in text:
        category = "technical"
    else:
        category = "general"

    priority = "high" if ticket.urgent else "normal"

    return TicketResult(
        category=category,
        priority=priority,
    )


@app.get("/")
def home() -> dict[str, str]:
    """Return a simple API status message."""

    return {"message": "CS415 Ticket API is running"}


# Example request body:
#   {"customer_name": "Ali", "message": "I have a payment issue", "urgent": true}
# Example response body:
#   {"category": "billing", "priority": "high"}


@app.post(
    "/tickets/classify",
    response_model=TicketResult,
)
def classify_ticket_endpoint(ticket: Ticket) -> TicketResult:
    """Classify an incoming customer support ticket."""

    return classify_ticket(ticket)
