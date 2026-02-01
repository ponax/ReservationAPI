"""
tests/test_main.py: Unit tests for main application endpoints

This module contains tests for the root and health check endpoints
of the FastAPI application.
"""

from fastapi.testclient import TestClient
from fastapi import status

def test_root_endpoint(client: TestClient):
    """Test the root endpoint returns API information."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "name" in data
    assert data["name"] == "ReservationAPI"
    assert "version" in data
    assert "docs_url" in data
