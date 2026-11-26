from ticket_api.conversation_repository import (
    fetch_conversation_messages,
)


MAX_HISTORY_TURNS = 10


def load_agent_memory(
    conversation_id: str,
) -> list[dict]:
    """Load recent conversation turns for the AI agent."""

    return fetch_conversation_messages(
        conversation_id=conversation_id,
        limit=MAX_HISTORY_TURNS * 2,
    )