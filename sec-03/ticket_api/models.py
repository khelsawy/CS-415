from pydantic import BaseModel, Field
from typing import Literal

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