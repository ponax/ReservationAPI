"""Utility routes for the Reservation API."""

from typing import Dict
from fastapi import APIRouter


router = APIRouter(
    prefix="/utils",
    tags=["utils"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/health", summary="Health Check", description="Check the health status of the API."
)
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint for monitoring.

    Returns:
        Dictionary with status information
    """
    return {"status": "healthy"}
