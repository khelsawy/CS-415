from fastapi import APIRouter, HTTPException, Path, Response

from .models import (
    Ticket,
    TicketResult,
    TicketStatusUpdate,
    CustomerLookup,
    CustomerTicketCreate,
    CustomerRegister,
    ConversationCreate,
    ConversationLookup,
    ConversationHistoryRequest,
    ConversationMessage,
)

from .services import (
    classify_ticket,
    create_ticket,
    list_tickets,
    get_ticket,
    change_ticket_status,
    get_customer_by_phone,
    create_customer_ticket,
    register_customer,
)

from .conversation_service import (
    create_conversation,
    list_customer_conversations,
    get_conversation_history,
    send_conversation_message,
)

router = APIRouter()


@router.get("/")
def home() -> dict[str, str]:
    """Return a simple API status message."""

    return {"message": "CS415 Ticket API is running"}


# Example request body:
#   {"customer_name": "Ali", "message": "I have a payment issue", "urgent": true}
# Example response body:
#   {"category": "billing", "priority": "high"}


@router.post(
    "/tickets/classify",
    response_model=TicketResult,
)
def classify_ticket_endpoint(ticket: Ticket) -> TicketResult:
    """Classify an incoming customer support ticket."""

    return classify_ticket(ticket)

@router.post("/tickets", status_code=201)
def create_new_ticket(ticket: Ticket) -> dict:
    """Create a ticket using AI classification and Supabase."""

    saved_ticket = create_ticket(ticket)

    return saved_ticket

@router.get("/tickets")
def get_all_tickets() -> list[dict]:
    """Get the latest tickets from Supabase."""

    return list_tickets()

@router.get("/tickets/{ticket_id}")
def get_ticket_details(
    ticket_id: int = Path(gt=0),
) -> dict:
    """Get ticket details by ID."""

    ticket = get_ticket(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return ticket


@router.patch("/tickets/{ticket_id}/status")
def update_ticket_status(
    status_update: TicketStatusUpdate,
    ticket_id: int = Path(gt=0),
) -> dict:
    """Update a ticket's status."""

    updated_ticket = change_ticket_status(
        ticket_id,
        status_update.status,
    )

    if updated_ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return updated_ticket

@router.post("/customers/lookup")
def lookup_customer(data: CustomerLookup) -> dict:
    """Find an existing customer by phone number."""

    try:
        customer = get_customer_by_phone(data.phone)

    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    return customer


@router.post("/customers/tickets", status_code=201)
def submit_customer_ticket(
    data: CustomerTicketCreate,
) -> dict:
    """Create a ticket for an existing customer."""

    try:
        saved_ticket = create_customer_ticket(
            phone=data.phone,
            message=data.message,
            urgent=data.urgent,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    if saved_ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    return saved_ticket


@router.post("/customers/register")
def register_new_customer(
    data: CustomerRegister,
    response: Response,
) -> dict:
    """Register a new customer or return an existing customer."""

    try:
        customer, created = register_customer(
            phone=data.phone,
            customer_name=data.customer_name,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    response.status_code = 201 if created else 200

    return customer


@router.post(
    "/conversations",
    status_code=201,
)
def start_conversation(
    data: ConversationCreate,
) -> dict:
    """Create a persistent customer conversation."""

    try:
        conversation = create_conversation(
            phone=data.phone,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found.",
        )

    return conversation


@router.post("/conversations/list")
def get_conversations(
    data: ConversationLookup,
) -> list[dict]:
    """List conversations belonging to a customer."""

    try:
        conversations = list_customer_conversations(
            phone=data.phone,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    if conversations is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found.",
        )

    return conversations

@router.post("/conversations/history")
def get_history(
    data: ConversationHistoryRequest,
) -> list[dict]:
    """Retrieve messages from a customer-owned conversation."""

    try:
        history = get_conversation_history(
            phone=data.phone,
            conversation_id=str(data.conversation_id),
        )

    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    if history is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    return history

@router.post("/conversations/message")
def send_message(
    data: ConversationMessage,
) -> dict:
    """Send a message using persistent agent memory."""

    message = data.message.strip()

    if not message:
        raise HTTPException(
            status_code=422,
            detail="Message cannot be empty.",
        )

    try:
        answer = send_conversation_message(
            phone=data.phone,
            conversation_id=str(data.conversation_id),
            message=message,
        )

    except ValueError as error:

        if str(error) in (
            "Customer not found.",
            "Conversation not found.",
        ):
            raise HTTPException(
                status_code=404,
                detail="Conversation not found.",
            ) from error

        raise HTTPException(
            status_code=422,
            detail="Invalid conversation request.",
        ) from error

    if answer is None:
        raise HTTPException(
            status_code=503,
            detail="The AI assistant could not complete the request.",
        )

    return {
        "conversation_id": str(data.conversation_id),
        "answer": answer,
    }
