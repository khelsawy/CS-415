# ============================================================
# CS415 - Lab 1
# Python Fundamentals for AI Agents
# ============================================================


# ============================================================
# 1. Variables and Basic Data Types
# ============================================================

ticket_id = 101
customer_name = "Ahmed"
priority_score = 0.8
is_resolved = False

print(ticket_id)
print(customer_name)
print(priority_score)
print(is_resolved)

print(type(ticket_id))
print(type(customer_name))
print(type(priority_score))
print(type(is_resolved))


# ============================================================
# 2. Strings and f-strings
# ============================================================

message = "My payment failed"

print(message)

print(
    f"Customer {customer_name} "
    f"has ticket #{ticket_id}"
)


# ============================================================
# 3. Lists
# ============================================================

messages = [
    "My payment failed",
    "I cannot login",
    "Where is my order?",
]

print(messages)

print(messages[0])
print(messages[1])

print(len(messages))


# ============================================================
# 4. Dictionaries
# ============================================================

ticket = {
    "id": 101,
    "customer": "Ahmed",
    "message": "My payment failed",
    "urgent": True,
}

print(ticket)

print(ticket["customer"])
print(ticket["message"])


# ============================================================
# 5. List of Dictionaries
# ============================================================

tickets = [
    {
        "id": 101,
        "customer": "Ahmed",
        "message": "My payment failed",
        "urgent": True,
    },
    {
        "id": 102,
        "customer": "Sara",
        "message": "I cannot login",
        "urgent": False,
    },
    {
        "id": 103,
        "customer": "Omar",
        "message": "Where is my order?",
        "urgent": False,
    },
]

print(tickets)


# ============================================================
# 6. Conditions
# ============================================================

message = "My payment failed"

if "payment" in message.lower():
    print("Billing issue")

elif "login" in message.lower():
    print("Technical issue")

else:
    print("General issue")


# ============================================================
# 7. Loops
# ============================================================

for ticket in tickets:
    print(ticket["message"])


# ============================================================
# 8. Functions
# ============================================================


def greet(name: str) -> str:
    """Return a greeting for the given name."""

    return f"Hello, {name}"


result = greet("Ahmed")

print(result)


# ============================================================
# 9. Ticket Classification Function
# ============================================================


def classify_ticket(message: str) -> str:
    """Classify a customer support message into a category."""

    text = message.lower()

    if "payment" in text or "invoice" in text:
        return "billing"

    elif "login" in text or "error" in text:
        return "technical"

    else:
        return "general"


category = classify_ticket(
    "My payment failed"
)

print(category)


# ============================================================
# 10. Priority Function
# ============================================================


def detect_priority(urgent: bool) -> str:
    """Return the priority of a ticket."""

    if urgent:
        return "high"

    return "normal"


priority = detect_priority(True)

print(priority)


# ============================================================
# 11. Process One Ticket
# ============================================================


def process_ticket(ticket: dict) -> dict:
    """Process a ticket and return its classification result."""

    category = classify_ticket(
        ticket["message"]
    )

    priority = detect_priority(
        ticket["urgent"]
    )

    return {
        "ticket_id": ticket["id"],
        "customer": ticket["customer"],
        "category": category,
        "priority": priority,
    }


result = process_ticket(tickets[0])

print(result)


# ============================================================
# 12. Process All Tickets
# ============================================================

for ticket in tickets:

    result = process_ticket(ticket)

    print(
        f"Ticket #{result['ticket_id']} "
        f"- Customer: {result['customer']} "
        f"- Category: {result['category']} "
        f"- Priority: {result['priority']}"
    )


# ============================================================
# 13. Count Tickets by Category
# ============================================================

counts = {
    "billing": 0,
    "technical": 0,
    "general": 0,
}

for ticket in tickets:

    category = classify_ticket(
        ticket["message"]
    )

    counts[category] += 1


print("\nSummary")

print(counts)


# ============================================================
# 14. Final Result
# ============================================================

print("\nAll Tickets")

for ticket in tickets:

    result = process_ticket(ticket)

    print(result)