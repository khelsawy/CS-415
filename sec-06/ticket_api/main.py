from fastapi import FastAPI

from .routes import router
from pathlib import Path

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


app = FastAPI(
    title="CS415 Ticket API",
    description="Section 6: Support tickets and persistent customer conversations",
    version="1.0.0",
)

WEB_DIR = Path(__file__).resolve().parent.parent / "web"

app.mount(
    "/static",
    StaticFiles(directory=WEB_DIR),
    name="static",
)


@app.get("/login", include_in_schema=False)
def login_page():
    """Serve the customer login page."""

    return FileResponse(WEB_DIR / "login.html")


@app.get("/chat", include_in_schema=False)
def chat_page():
    """Serve the customer chat page."""

    return FileResponse(WEB_DIR / "chat.html")

@app.get("/create-ticket", include_in_schema=False)
def create_ticket_page():
    """Serve the support ticket creation page."""

    return FileResponse(
        WEB_DIR / "create-ticket.html"
    )

app.include_router(router)
