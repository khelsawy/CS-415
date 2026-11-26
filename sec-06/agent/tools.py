from pydantic import BaseModel, Field, ConfigDict

from ticket_api.services import (
    list_customer_tickets,
    get_customer_ticket,
)


class TicketIdInput(BaseModel):
    ticket_id: int = Field(gt=0)


class NoArguments(BaseModel):
    """Input model for tools that require no arguments."""

    model_config = ConfigDict(extra="forbid")

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
