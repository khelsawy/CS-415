from pydantic import BaseModel, Field, ConfigDict

from typing import Callable

from ticket_api.services import (
    get_ticket,
    list_customer_tickets,
    get_customer_ticket,
)

# 1. Tool Input Validation
class TicketIdInput(BaseModel):
    ticket_id: int = Field(gt=0)


class NoArguments(BaseModel):
    """Input model for tools that require no arguments."""

    model_config = ConfigDict(extra="forbid")

# 2. Get Ticket Status
def get_ticket_status(ticket_id: int) -> dict:
    """Get the current status of a ticket."""

    ticket = get_ticket(ticket_id)

    if ticket is None:
        return {"error": f"Ticket {ticket_id} not found"}

    return {
        "ticket_id": ticket_id,
        "status": ticket["status"],
    }


# 3. Get Ticket Details
def get_ticket_details(ticket_id: int) -> dict:
    """Get the saved details of a ticket."""

    ticket = get_ticket(ticket_id)

    if ticket is None:
        return {"error": f"Ticket {ticket_id} not found"}

    return ticket


# 4. Tool Definition
def tool_definition(
    name: str,
    description: str,
    schema: dict,
) -> dict:
    """Describe a tool to the LLM."""

    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": schema,
        },
    }


# 5. Available Tools
TOOLS = [
    tool_definition(
        "get_ticket_status",
        "Get the current status of an existing ticket.",
        TicketIdInput.model_json_schema(),
    ),
    tool_definition(
        "get_ticket_details",
        "Get the customer, message, category, priority, "
        "and status of an existing ticket.",
        TicketIdInput.model_json_schema(),
    ),
]


# 6. Tool Handlers
TOOL_HANDLERS = {
    "get_ticket_status": get_ticket_status,
    "get_ticket_details": get_ticket_details,
}


# 7. Tool Input Models
TOOL_INPUT_MODELS = {
    "get_ticket_status": TicketIdInput,
    "get_ticket_details": TicketIdInput,
}


def build_customer_tools(customer_id: str):
    """Build ticket tools scoped to one customer."""

    # Tool 1: List my tickets
    def get_my_tickets() -> list[dict]:
        """Get tickets belonging to the current customer."""

        return list_customer_tickets(customer_id)

    # Tool 2: Get my latest ticket
    def get_my_latest_ticket() -> dict:
        """Get the latest ticket belonging to the customer."""

        tickets = list_customer_tickets(customer_id)

        if not tickets:
            return {"message": "You have no tickets yet."}

        return tickets[0]

    # Tool 3: Get details of one of my tickets
    def get_my_ticket_details(ticket_id: int) -> dict:
        """Get a ticket only if it belongs to this customer."""

        ticket = get_customer_ticket(
            customer_id=customer_id,
            ticket_id=ticket_id,
        )

        if ticket is None:
            return {
                "error": "Ticket not found for this customer."
            }

        return ticket

    # Tools visible to the LLM
    tools = [
        tool_definition(
            "get_my_tickets",
            "List the current customer's support tickets.",
            NoArguments.model_json_schema(),
        ),
        tool_definition(
            "get_my_latest_ticket",
            "Get the current customer's most recent ticket, "
            "including its status, category and priority.",
            NoArguments.model_json_schema(),
        ),
        tool_definition(
            "get_my_ticket_details",
            "Get details of a specific ticket belonging "
            "to the current customer.",
            TicketIdInput.model_json_schema(),
        ),
    ]

    # Python functions that can be executed
    handlers = {
        "get_my_tickets": get_my_tickets,
        "get_my_latest_ticket": get_my_latest_ticket,
        "get_my_ticket_details": get_my_ticket_details,
    }

    # Input validation models
    input_models = {
        "get_my_tickets": NoArguments,
        "get_my_latest_ticket": NoArguments,
        "get_my_ticket_details": TicketIdInput,
    }

    return tools, handlers, input_models