from .database import get_supabase_client
from .models import Ticket, TicketResult
from datetime import datetime, timezone

def insert_ticket(
    ticket: Ticket,
    result: TicketResult,
    customer_id: str | None = None,
) -> dict:
    """Insert a ticket into Supabase."""

    db = get_supabase_client()

    ticket_data = {
        "customer_name": ticket.customer_name,
        "message": ticket.message,
        "urgent": ticket.urgent,
        "category": result.category,
        "priority": result.priority,
    }

    # Link the ticket to its customer
    if customer_id is not None:
        ticket_data["customer_id"] = customer_id

    response = (
        db.table("tickets")
        .insert(ticket_data)
        .execute()
    )

    if not response.data:
        raise RuntimeError("Failed to create ticket.")

    return response.data[0]

def fetch_tickets() -> list[dict]:
    """Fetch tickets from Supabase."""

    db = get_supabase_client()

    response = (
        db.table("tickets")
        .select("*")
        .order("created_at", desc=True)
        .limit(100)
        .execute()
    )

    return response.data


def fetch_ticket_by_id(ticket_id: int) -> dict | None:
    """Fetch a single ticket by its ID."""

    db = get_supabase_client()

    response = (
        db.table("tickets")
        .select("*")
        .eq("id", ticket_id)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]


def update_ticket_status_in_db(
    ticket_id: int,
    status: str,
) -> dict | None:
    """Update a ticket's status in Supabase."""

    db = get_supabase_client()

    update_data = {
        "status": status,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    response = (
        db.table("tickets")
        .update(update_data)
        .eq("id", ticket_id)
        .select("*")
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]

def fetch_customer_by_phone(phone: str) -> dict | None:
    """Find a customer by phone number."""

    db = get_supabase_client()

    response = (
        db.table("customers")
        .select("id, customer_name, phone")
        .eq("phone", phone)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]

def insert_customer(
    phone: str,
    customer_name: str,
) -> dict:
    """Save a new customer in Supabase."""

    db = get_supabase_client()

    response = (
        db.table("customers")
        .insert({
            "phone": phone,
            "customer_name": customer_name,
        })
        .execute()
    )

    if not response.data:
        raise RuntimeError("Failed to create customer.")

    return response.data[0]

def fetch_customer_tickets(customer_id: str) -> list[dict]:
    """Fetch tickets belonging to a specific customer."""

    db = get_supabase_client()

    response = (
        db.table("tickets")
        .select("*")
        .eq("customer_id", customer_id)
        .order("created_at", desc=True)
        .limit(100)
        .execute()
    )

    return response.data

def fetch_customer_ticket_by_id(
    customer_id: str,
    ticket_id: int,
) -> dict | None:
    """Fetch a ticket only if it belongs to the customer."""

    db = get_supabase_client()

    response = (
        db.table("tickets")
        .select("*")
        .eq("customer_id", customer_id)
        .eq("id", ticket_id)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]