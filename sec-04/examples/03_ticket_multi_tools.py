"""CS 415 - Lab 04 / Example 03: Choose among multiple Ticket System tools.

The model requests a tool; Python validates and executes it.
This lesson deliberately stops after tool execution (no agent loop yet).
Run from sec-04: uv run python -m examples.03_ticket_multi_tools
"""

import json
from typing import Any
from pydantic import BaseModel, Field, ValidationError
from llm.client import LLMClient
from ticket_api.models import Ticket
from ticket_api.services import classify_ticket


# A temporary ticket for this lesson. It exists only in this Python process:
# no database, files, or existing tickets are modified.
TICKET_STORE: dict[int, dict[str, Any]] = {
    1: {
        "ticket": Ticket(
            customer_name="Ahmed",
            message="I cannot login to my account",
            urgent=True,
        ),
        "status": "open",
    },
    2: {
        "ticket": Ticket(
            customer_name="Mona",
            message="I have a payment issue",
            urgent=False,
        ),
        "status": "closed",
    },
}


class TicketIdInput(BaseModel):
    """Validate the input used by both lookup tools."""

    ticket_id: int = Field(gt=0, description="Positive ticket ID")


def classify_ticket_tool(
    customer_name: str, message: str, urgent: bool = False
) -> dict:
    """Adapt the original Ticket-based service to tool arguments."""
    ticket = Ticket(
        customer_name=customer_name,
        message=message,
        urgent=urgent,
    )
    return classify_ticket(ticket).model_dump()


def get_ticket_status(ticket_id: int) -> dict:
    """Read a ticket's status from our temporary in-memory store."""
    record = TICKET_STORE.get(ticket_id)
    if record is None:
        return {"error": f"Ticket {ticket_id} not found"}
    return {"ticket_id": ticket_id, "status": record["status"]}


def get_ticket_details(ticket_id: int) -> dict:
    """Read the full ticket from our temporary in-memory store."""
    record = TICKET_STORE.get(ticket_id)
    if record is None:
        return {"error": f"Ticket {ticket_id} not found"}
    return {
        "ticket_id": ticket_id,
        **record["ticket"].model_dump(),
        "status": record["status"],
    }


def tool_definition(name: str, description: str, schema: dict) -> dict:
    """Describe a Python tool to the LLM (does NOT execute it)."""
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": schema,
        },
    }


# Reuse Pydantic schemas instead of maintaining JSON Schema by hand.
TOOLS = [
    tool_definition(
        "classify_ticket",
        "Classify a support ticket using our existing billing/technical/general rules.",
        Ticket.model_json_schema(),
    ),
    tool_definition(
        "get_ticket_status",
        "Get only the status of an existing ticket by ticket_id.",
        TicketIdInput.model_json_schema(),
    ),
    tool_definition(
        "get_ticket_details",
        "Get the customer, message, urgency, and status of a ticket by ticket_id.",
        TicketIdInput.model_json_schema(),
    ),
]

# Allowlists: a returned name is only data until Python looks it up here.
TOOL_HANDLERS = {
    "classify_ticket": classify_ticket_tool,
    "get_ticket_status": get_ticket_status,
    "get_ticket_details": get_ticket_details,
}
TOOL_INPUT_MODELS = {
    "classify_ticket": Ticket,
    "get_ticket_status": TicketIdInput,
    "get_ticket_details": TicketIdInput,
}


def execute_requested_tool(call: dict) -> None:
    """Parse -> validate -> dispatch one tool request safely."""
    function = call.get("function") or {}
    name = function.get("name")
    print(f"Model requested: {name}")

    if name not in TOOL_HANDLERS:
        print("Skipped: unknown tool")
        return

    try:
        raw_arguments = function.get("arguments", "{}")
        arguments = (
            json.loads(raw_arguments)
            if isinstance(raw_arguments, str)
            else raw_arguments
        )
        validated = TOOL_INPUT_MODELS[name].model_validate(arguments)
        result = TOOL_HANDLERS[name](**validated.model_dump())
    except (json.JSONDecodeError, ValidationError, TypeError, ValueError) as error:
        print(f"Invalid arguments: {error}")
        return
    except Exception as error:
        # Keep one failed lookup/function from crashing the classroom demo.
        print(f"Tool execution failed: {type(error).__name__}: {error}")
        return

    print("Python executed ->", json.dumps(result, indent=2))


def main() -> None:
    client = LLMClient()
    questions = [
        (
            'Classify this ticket: {"customer_name": "Mona", '
            '"message": "I have a payment issue", "urgent": false}'
        ),
        "What is the status of ticket 2?",
        "Show me the details of ticket 2.",
    ]

    for question in questions:
        print(f"\n{'=' * 60}\nUser: {question}")
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a support ticket assistant. "
                    "For classification requests, request classify_ticket. "
                    "For status requests, request get_ticket_status. "
                    "For details requests, request get_ticket_details. "
                    "Do not invent classifications or stored ticket information."
                ),
            },
            {"role": "user", "content": question},
        ]

        response = client.chat(messages, tools=TOOLS)
        calls = response.get("tool_calls") or []
        if not calls:
            print("Model answered directly:", response.get("content"))
            continue

        for call in calls:
            execute_requested_tool(call)

    print("\nExample 03 ends here: tool results are NOT sent back to the LLM.")


if __name__ == "__main__":
    main()
