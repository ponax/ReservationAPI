""" "Tests for utility functions."""

from fastapi import status
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test the health check endpoint."""
    response = client.get("/api/utils/health")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["status"] == "healthy"
