"""Lab 04 / Example 02: Let the LLM request our existing ticket classifier.
This example deliberately stops after running the requested tool.
The next lab will send tool results back to the model in an agent loop.
"""

import json

from pydantic import ValidationError

from llm.client import LLMClient
from ticket_api.models import Ticket
from ticket_api.services import classify_ticket


# Our LLMClient accepts OpenAI-compatible JSON schemas, not Python callables.
CLASSIFY_TICKET_TOOL = {
    "type": "function",
    "function": {
        "name": "classify_ticket",
        "description": "Classify a support ticket using the application's existing rules.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_name": {"type": "string", "description": "Customer name"},
                "message": {"type": "string", "description": "Customer's support request"},
                "urgent": {"type": "boolean", "description": "Whether the ticket is urgent"},
            },
            "required": ["customer_name", "message", "urgent"],
        },
    },
}


def main() -> None:
    # A normal Ticket System request, validated by Pydantic.
    ticket = Ticket(
        customer_name="Ahmed",
        message="I cannot login to my account",
        urgent=True,
    )

    messages = [
        {
            "role": "system",
            "content": (
                "You are a support ticket assistant. "
                "When asked to classify a ticket, request the classify_ticket tool. "
                "Do not invent the category or priority yourself."
            ),
        },
        {
            "role": "user",
            "content": f"Classify this support ticket: {ticket.model_dump_json()}",
        },
    ]

    print("Ticket:", ticket.model_dump_json(indent=2))
    client = LLMClient()
    response = client.chat(messages, tools=[CLASSIFY_TICKET_TOOL])

    # The LLM proposes tool calls; only our Python application executes them.
    tool_calls = response.get("tool_calls") or []
    if not tool_calls:
        print("\nNo tool was requested by the model.")
        print("Model reply:", response.get("content"))
        return

    for call in tool_calls:
        function = call.get("function") or {}
        name = function.get("name")
        print("\nModel requested tool:", name)

        # An LLM is untrusted input: dispatch only explicitly allowed functions.
        if name != "classify_ticket":
            print("Skipped: unknown tool")
            continue

        try:
            raw_arguments = function.get("arguments", "{}")
            arguments = (
                json.loads(raw_arguments)
                if isinstance(raw_arguments, str)
                else raw_arguments
            )
            validated_ticket = Ticket.model_validate(arguments)
        except (json.JSONDecodeError, ValidationError, TypeError, ValueError) as exc:
            print("Invalid tool arguments:", exc)
            continue

        print("Validated tool arguments:", validated_ticket.model_dump())
        result = classify_ticket(validated_ticket)
        print("Tool executed by Python:", result.model_dump())

    print("\nExample 02 ends here: no follow-up LLM call yet.")


if __name__ == "__main__":
    main()