"""
api/__init__.py: API module initialization

This module serves as the entry point for the API package and
provides the main router that aggregates all sub-routes.
"""

from fastapi import APIRouter
from api.routes import reservations, rooms

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(
    reservations.router,
    prefix="/reservations",
    tags=["reservations"]
)

api_router.include_router(
    rooms.router,
    prefix="/rooms",
    tags=["rooms"]
)
