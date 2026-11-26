from .database import get_supabase_client


def insert_conversation(customer_id: str) -> dict:
    """Create a new conversation for a customer."""

    db = get_supabase_client()

    response = (
        db.table("conversations")
        .insert({
            "customer_id": customer_id,
        })
        .execute()
    )

    if not response.data:
        raise RuntimeError("Failed to create conversation.")

    return response.data[0]


def fetch_conversation(
    conversation_id: str,
    customer_id: str,
) -> dict | None:
    """Fetch a conversation belonging to a specific customer."""

    db = get_supabase_client()

    response = (
        db.table("conversations")
        .select("*")
        .eq("id", conversation_id)
        .eq("customer_id", customer_id)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]


def fetch_customer_conversations(
    customer_id: str,
) -> list[dict]:
    """Fetch conversations belonging to a customer."""

    db = get_supabase_client()

    response = (
        db.table("conversations")
        .select("*")
        .eq("customer_id", customer_id)
        .order("created_at", desc=True)
        .order("id", desc=True)
        .limit(50)
        .execute()
    )

    return response.data


def insert_messages(
    conversation_id: str,
    question: str,
    answer: str,
) -> list[dict]:
    """Save a completed conversation turn."""

    db = get_supabase_client()

    messages = [
        {
            "conversation_id": conversation_id,
            "role": "user",
            "content": question,
        },
        {
            "conversation_id": conversation_id,
            "role": "assistant",
            "content": answer,
        },
    ]

    response = (
        db.table("messages")
        .insert(messages)
        .execute()
    )

    if not response.data:
        raise RuntimeError("Failed to save messages.")

    return response.data


def fetch_conversation_messages(
    conversation_id: str,
    limit: int = 20,
) -> list[dict]:
    """Fetch recent conversation messages in chronological order."""

    db = get_supabase_client()

    response = (
        db.table("messages")
        .select("role, content")
        .eq("conversation_id", conversation_id)
        .order("id", desc=True)
        .limit(limit)
        .execute()
    )

    return list(reversed(response.data))

def fetch_full_conversation_history(
    conversation_id: str,
) -> list[dict]:
    """Fetch the complete conversation history."""

    db = get_supabase_client()

    messages = []

    page_size = 500
    last_id = 0

    while True:

        response = (
            db.table("messages")
            .select("id, role, content")
            .eq("conversation_id", conversation_id)
            .gt("id", last_id)
            .order("id", desc=False)
            .limit(page_size)
            .execute()
        )

        batch = response.data

        if not batch:
            break

        messages.extend(
            {"role": row["role"], "content": row["content"]}
            for row in batch
        )
        last_id = batch[-1]["id"]

    return messages
