"""API main router

This module serves as the entry point for the API package and
provides the main router that aggregates all sub-routes
"""

from fastapi import APIRouter
from api.routes import reservations, rooms, utils

api_router = APIRouter()
api_router.include_router(reservations.router)
api_router.include_router(rooms.router)
api_router.include_router(utils.router)
