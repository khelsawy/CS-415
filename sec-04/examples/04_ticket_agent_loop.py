"""CS 415 - Lab 05 / Example 04: First Agent Loop for our Ticket System.

New idea compared with Example 03:
  1. Ask the LLM which tool(s) it needs.
  2. Python validates and executes the requested tools.
  3. Send each tool result BACK to the LLM using its tool_call_id.
  4. Repeat until the LLM returns a final answer (or we hit a safety limit).

Run from sec-05:
    uv run python -m examples.04_ticket_agent_loop

This demo uses a single fake ticket stored in process memory, not a database.
"""

import json
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from llm.client import LLMClient
from ticket_api.models import Ticket
from ticket_api.services import classify_ticket


# Same read-only, in-memory demo data as Example 03.
TICKET_STORE: dict[int, dict[str, Any]] = {
    1: {
        "ticket": Ticket(
            customer_name="Ahmed",
            message="I cannot login to my account",
            urgent=True,
        ),
        "status": "open",
    }
}


class TicketIdInput(BaseModel):
    """Input contract for ticket lookup tools."""

    ticket_id: int = Field(gt=0)


def classify_ticket_tool(
    customer_name: str, message: str, urgent: bool = False
) -> dict:
    """Reuse the deterministic classifier that we built in Lab 02."""
    ticket = Ticket(customer_name=customer_name, message=message, urgent=urgent)
    return classify_ticket(ticket).model_dump()


def get_ticket_status(ticket_id: int) -> dict:
    """Read the status of a sample ticket."""
    record = TICKET_STORE.get(ticket_id)
    if record is None:
        return {"error": f"Ticket {ticket_id} not found"}
    return {"ticket_id": ticket_id, "status": record["status"]}


def get_ticket_details(ticket_id: int) -> dict:
    """Read a sample ticket's data and status."""
    record = TICKET_STORE.get(ticket_id)
    if record is None:
        return {"error": f"Ticket {ticket_id} not found"}
    return {
        "ticket_id": ticket_id,
        **record["ticket"].model_dump(),
        "status": record["status"],
    }


def tool_definition(name: str, description: str, schema: dict) -> dict:
    """Create the tool description the LLM will receive."""
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": schema,
        },
    }


TOOLS = [
    tool_definition(
        "classify_ticket",
        "Classify a ticket using our existing business rules. "
        "Use its real customer_name, message, and urgent fields.",
        Ticket.model_json_schema(),
    ),
    tool_definition(
        "get_ticket_status",
        "Retrieve the status of an existing ticket using its ticket_id.",
        TicketIdInput.model_json_schema(),
    ),
    tool_definition(
        "get_ticket_details",
        "Retrieve the customer name, message, urgency, and status "
        "of an existing ticket using ticket_id.",
        TicketIdInput.model_json_schema(),
    ),
]

# Explicitly allowlisted Python handlers and their Pydantic input contracts.
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

MAX_TOOL_ROUNDS = 6


def execute_requested_tool(call: dict) -> str:
    """Validate a model-requested call; return JSON for the LLM to read.

    Even errors become tool responses, so the model can recover or explain.
    No code is executed from an LLM-supplied string.
    """
    function = call.get("function") or {}
    name = function.get("name")

    if name not in TOOL_HANDLERS:
        return json.dumps({"error": f"Unknown or disallowed tool: {name}"})

    try:
        raw_arguments = function.get("arguments", "{}")
        arguments = (
            json.loads(raw_arguments)
            if isinstance(raw_arguments, str)
            else raw_arguments
        )
        validated = TOOL_INPUT_MODELS[name].model_validate(arguments)
        result = TOOL_HANDLERS[name](**validated.model_dump())
        return json.dumps(result, ensure_ascii=False)
    except (json.JSONDecodeError, ValidationError, TypeError, ValueError) as exc:
        return json.dumps({"error": f"Invalid tool arguments: {exc}"})
    except Exception as exc:
        # Keep the classroom demo alive when a handler fails.
        return json.dumps({"error": f"Tool execution failed: {type(exc).__name__}"})


def run_agent(client: LLMClient, question: str) -> str | None:
    """Keep calling the LLM until it answers or the loop limit is reached."""
    messages: list[dict] = [
        {
            "role": "system",
            "content": (
                "You are a customer support ticket assistant. "
                "Use available tools instead of inventing ticket data, "
                "status, category, or priority. "
                "For category and priority of a stored ticket, first get its "
                "details, then call classify_ticket with those exact details. "
                "After receiving tool results, answer the user's question clearly. "
                "If a tool reports an error, do not invent missing information."
            ),
        },
        {"role": "user", "content": question},
    ]

    for round_number in range(1, MAX_TOOL_ROUNDS + 1):
        print(f"\n--- LLM round {round_number} ---")
        response = client.chat(messages, tools=TOOLS)
        calls = response.get("tool_calls") or []

        # BASE CASE: The LLM has stopped requesting tools.
        if not calls:
            answer = response.get("content")
            print("Agent:", answer or "(No final answer returned)")
            return answer

        # The assistant message with the requests MUST precede tool results.
        # Keep the original call IDs: each tool reply refers to one ID.
        if any(not isinstance(call, dict) or not call.get("id") for call in calls):
            print("Stopped: provider returned a tool call without an ID.")
            return None
        messages.append({
            "role": "assistant",
            "content": response.get("content"),
            "tool_calls": calls,
        })

        for call in calls:
            function_name = (call.get("function") or {}).get("name")
            print(f"Model requested: {function_name}")

            # Python runs the function. The LLM only requested the action.
            result_text = execute_requested_tool(call)
            print("Tool result:", result_text)

            # IMPORTANT: return the result to the LLM, linked to its request.
            messages.append({
                "role": "tool",
                "tool_call_id": call["id"],
                "content": result_text,
            })

    print("Agent stopped: maximum tool rounds reached.")
    return None


def main() -> None:
    client = LLMClient()
    question = (
        "For ticket 1, tell me the customer name, current status, "
        "category, and priority. Use the ticket tools; do not guess."
    )
    print("User:", question)
    run_agent(client, question)


if __name__ == "__main__":
    main()
