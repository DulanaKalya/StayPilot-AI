from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.config import settings

from src.api.routers import (
    rooms,
    guests,
    reservations,
    service_requests
)
from src.api.routers import chat


app = FastAPI(
    title=settings.app_name,
    description="Multi-Agentic Voice AI Hotel Concierge",
    version="0.1.0"
)

app.include_router(
    chat.router,
    prefix="/api/v1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(
    rooms.router,
    prefix="/api/v1"
)

app.include_router(
    guests.router,
    prefix="/api/v1"
)

app.include_router(
    reservations.router,
    prefix="/api/v1"
)

app.include_router(
    service_requests.router,
    prefix="/api/v1"
)


@app.get("/")
def root():

    return {
        "application": settings.app_name,
        "version": "0.1.0",
        "environment": settings.app_env,
        "status": "running"
    }


@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }


