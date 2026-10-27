from ticket_api.models import Ticket
from ticket_api.services import classify_ticket
from llm.client import LLMClient


def main() -> None:

    # Step 1: Create a support ticket
    ticket = Ticket(
        customer_name="Ahmed",
        message="I cannot login to my account",
        urgent=True,
    )

    # Step 2: Classify using our existing rules
    result = classify_ticket(ticket)

    print("Category:", result.category)
    print("Priority:", result.priority)

    # Step 3: Prepare messages for the LLM
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful customer support assistant. "
                "Write short, professional responses to customers. "
                "Do not claim to have performed actions."
            ),
        },
        {
            "role": "user",
            "content": f"""
Customer: {ticket.customer_name}
Problem: {ticket.message}
Category: {result.category}
Priority: {result.priority}

Write a helpful reply to this customer.
""",
        },
    ]

    # Step 4: Call the LLM
    client = LLMClient()

    response = client.chat(messages)

    # Step 5: Display the generated reply
    print("\nAI Response:")
    print(response["content"])


if __name__ == "__main__":
    main()