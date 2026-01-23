"""
main.py: FastAPI application entry point

This is the main application file that initializes the FastAPI application,
configures middleware, includes routers, and provides database initialization.
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager

from api import api_router
from database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events for the FastAPI application.
    On startup, initializes the database and loads initial data.
    
    Args:
        app: FastAPI application instance
    """
    # Startup: Initialize database
    init_db()
    yield
    # Shutdown: Cleanup (if needed)


# Create FastAPI application
app = FastAPI(
    title="ReservationAPI",
    description="Meeting room reservation API with FastAPI",
    version="0.1.0",
    lifespan=lifespan
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
        "openapi_url": "/openapi.json"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns:
        Dictionary with status information
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
