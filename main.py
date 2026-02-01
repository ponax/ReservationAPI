"""
main.py: FastAPI application entry point

This is the main application file that initializes the FastAPI application,
configures middleware, includes routers, and provides database initialization.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.main import api_router
from database import init_db


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):  # pylint: disable=unused-argument, redefined-outer-name
    """
    Application lifespan manager.

    Handles startup and shutdown events for the FastAPI application.
    On startup, initializes the database and loads initial data.

    Args:
        app: FastAPI application instance
    """
    init_db()
    yield


# Create FastAPI application
app = FastAPI(
    title="ReservationAPI",
    description="Meeting room reservation API with FastAPI",
    version="0.1.0",
    lifespan=lifespan,
)

# Include API router
app.include_router(api_router, prefix="/api")


@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint providing API information.

    Returns:
        Dictionary with API name and documentation URL
    """
    return {
        "name": "ReservationAPI",
        "version": "0.1.0",
        "description": "Meeting room reservation API",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
    }
