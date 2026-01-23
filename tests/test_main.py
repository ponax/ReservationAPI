"""
tests/test_main.py: Unit tests for main application endpoints

This module contains tests for the root and health check endpoints
of the FastAPI application.
"""

import pytest
from fastapi import status


class TestMainEndpoints:
    """Test suite for main application endpoints."""
    
    def test_root_endpoint(self, client):
        """Test the root endpoint returns API information."""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "name" in data
        assert data["name"] == "ReservationAPI"
        assert "version" in data
        assert "docs_url" in data
    
    def test_health_check(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["status"] == "healthy"
