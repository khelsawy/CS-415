import logging

from requests import RequestException

from agent.agent import run_agent
from agent.memory import load_agent_memory
from llm.client import LLMClient

from .conversation_repository import (
    insert_conversation,
    fetch_conversation,
    fetch_customer_conversations,
    insert_messages,
    fetch_full_conversation_history,
)
from .services import get_customer_by_phone


logger = logging.getLogger(__name__)

def create_conversation(phone: str) -> dict | None:
    """Create a new conversation for an existing customer."""

    customer = get_customer_by_phone(phone)

    if customer is None:
        return None

    conversation = insert_conversation(
        customer_id=customer["id"]
    )

    return {
        "conversation_id": conversation["id"],
        "customer_name": customer["customer_name"],
        "created_at": conversation["created_at"],
    }

def list_customer_conversations(
    phone: str,
) -> list[dict] | None:
    """Return conversations belonging to a customer."""

    customer = get_customer_by_phone(phone)

    if customer is None:
        return None

    return fetch_customer_conversations(
        customer_id=customer["id"]
    )


def get_conversation_history(
    phone: str,
    conversation_id: str,
) -> list[dict] | None:
    """Load the history of a customer-owned conversation."""

    # Step 1: Identify the customer
    customer = get_customer_by_phone(phone)

    if customer is None:
        return None

    # Step 2: Check conversation ownership
    conversation = fetch_conversation(
        conversation_id=conversation_id,
        customer_id=customer["id"],
    )

    if conversation is None:
        return None

    # Step 3: Load conversation messages
    return fetch_full_conversation_history(
        conversation_id=conversation["id"]
    )


def send_conversation_message(
    phone: str,
    conversation_id: str,
    message: str,
) -> str | None:
    """Run the agent using persistent conversation memory."""

    # Step 1: Identify customer
    customer = get_customer_by_phone(phone)

    if customer is None:
        raise ValueError("Customer not found.")

    # Step 2: Verify conversation ownership
    conversation = fetch_conversation(
        conversation_id=conversation_id,
        customer_id=customer["id"],
    )

    if conversation is None:
        raise ValueError("Conversation not found.")

    # Step 3: Load agent memory
    history = load_agent_memory(
        conversation_id=conversation_id,
    )

    # Step 4: Initialize LLM client
    try:
        client = LLMClient()
    except ValueError as error:
        logger.warning("Conversation LLM configuration failed (%s).", type(error).__name__)
        return None

    # Step 5: Run the AI agent
    try:
        answer = run_agent(
            client=client,
            question=message,
            customer_id=customer["id"],
            history=history,
        )
    except RequestException as error:
        logger.warning("Conversation LLM request failed (%s).", type(error).__name__)
        return None

    # Step 6: Validate the answer
    if not isinstance(answer, str) or not answer.strip():
        return None

    # Step 7: Save the completed conversation turn
    insert_messages(
        conversation_id=conversation_id,
        question=message,
        answer=answer,
    )

    # Step 8: Return the answer
    return answer
