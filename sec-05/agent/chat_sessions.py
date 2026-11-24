from uuid import uuid4

from llm.client import LLMClient
from ticket_api.services import get_customer_by_phone

from .agent import run_agent


# Temporary in-memory chat sessions
SESSIONS: dict[str, dict] = {}


def create_chat_session(phone: str) -> dict | None:
    """Start a new chat session for an existing customer."""

    customer = get_customer_by_phone(phone)

    if customer is None:
        return None

    session_id = str(uuid4())

    SESSIONS[session_id] = {
        "customer_id": customer["id"],
        "history": [],
    }

    return {
        "session_id": session_id,
        "customer_name": customer["customer_name"],
    }


def send_chat_message(
    session_id: str,
    message: str,
) -> str | None:
    """Send a message to the customer-aware agent."""

    session = SESSIONS.get(session_id)

    if session is None:
        raise KeyError("Chat session not found")

    client = LLMClient()

    answer = run_agent(
        client=client,
        question=message,
        customer_id=session["customer_id"],
        history=session["history"],
    )

    return answer