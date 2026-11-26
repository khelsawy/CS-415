from pydantic import BaseModel, Field
from typing import Literal
from uuid import UUID

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


class TicketStatusUpdate(BaseModel):
    """Validate ticket status updates."""

    status: Literal[
        "open",
        "in_progress",
        "resolved",
        "closed",
    ]

class CustomerLookup(BaseModel):
    """Customer identification using a phone number."""

    phone: str = Field(min_length=10, max_length=20)

class CustomerTicketCreate(BaseModel):
    """Request model for creating a customer support ticket."""

    phone: str = Field(min_length=10, max_length=20)

    message: str = Field(min_length=5)

    urgent: bool = False

class CustomerRegister(BaseModel):
    """Customer registration request."""

    phone: str = Field(min_length=10, max_length=20)

    customer_name: str = Field(
        min_length=2,
        max_length=100,
    )


class ConversationCreate(BaseModel):
    """Request to create a new conversation."""

    phone: str = Field(
        min_length=10,
        max_length=20,
    )


class ConversationLookup(BaseModel):
    """Request to list customer conversations."""

    phone: str = Field(
        min_length=10,
        max_length=20,
    )


class ConversationHistoryRequest(BaseModel):
    """Request to retrieve conversation history."""

    phone: str = Field(
        min_length=10,
        max_length=20,
    )

    conversation_id: UUID


class ConversationMessage(BaseModel):
    """Request to send a message to a conversation."""

    phone: str = Field(
        min_length=10,
        max_length=20,
    )

    conversation_id: UUID

    message: str = Field(
        min_length=1,
        max_length=4000,
    )