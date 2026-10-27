"""Lab 04 / Example 01: Stream an AI-generated ticket reply."""

from ticket_api.models import Ticket
from ticket_api.services import classify_ticket
from llm.client import LLMClient


def main() -> None:
    ticket = Ticket(
        customer_name="Ahmed",
        message="I cannot login to my account",
        urgent=True,
    )

    # Reuse the existing deterministic business rules from Lab 02.
    result = classify_ticket(ticket)
    print("Category:", result.category)
    print("Priority:", result.priority)

    messages = [
        {
            "role": "system",
            "content": (
                "You are a customer support assistant. "
                "Write a brief, helpful customer-facing reply (3-5 sentences). "
                "Do not claim that you performed any account actions."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Customer: {ticket.customer_name}\n"
                f"Problem: {ticket.message}\n"
                f"Category: {result.category}\n"
                f"Priority: {result.priority}\n\n"
                "Draft a reply for this ticket."
            ),
        },
    ]

    client = LLMClient()
    print("\nAI Response:")
    for piece in client.chat_stream(messages):
        print(piece, end="", flush=True)
    print()


if __name__ == "__main__":
    main()

