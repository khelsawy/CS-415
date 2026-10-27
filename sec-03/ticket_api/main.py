from fastapi import FastAPI

from .routes import router


app = FastAPI(
    title="CS415 Ticket API",
    description="Lab 2 example: Pydantic + FastAPI",
    version="1.0.0",
)



app.include_router(router)