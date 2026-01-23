"""
tests/test_rooms.py: Unit tests for room management endpoints

This module contains comprehensive tests for room-related API endpoints,
including listing rooms, creating rooms, and retrieving room details.
"""

import pytest
from fastapi import status


class TestRoomEndpoints:
    """Test suite for room management endpoints."""
    
    def test_list_rooms_empty(self, client):
        """Test listing rooms when database is empty."""
        response = client.get("/api/rooms/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    def test_create_room_success(self, client):
        """Test creating a new room successfully."""
        room_data = {
            "name": "Conference Room A",
            "capacity": 10,
            "location": "Floor 1"
        }
        response = client.post("/api/rooms/", json=room_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["name"] == room_data["name"]
        assert data["capacity"] == room_data["capacity"]
        assert data["location"] == room_data["location"]
        assert "id" in data
        assert "created_at" in data
    
    def test_create_room_duplicate_name(self, client, sample_room):
        """Test creating a room with duplicate name fails."""
        room_data = {
            "name": sample_room.name,
            "capacity": 5,
            "location": "Floor 2"
        }
        response = client.post("/api/rooms/", json=room_data)
        assert response.status_code == status.HTTP_409_CONFLICT
    
    def test_create_room_invalid_capacity(self, client):
        """Test creating a room with invalid capacity fails."""
        room_data = {
            "name": "Invalid Room",
            "capacity": 0,  # Invalid: must be > 0
            "location": "Floor 1"
        }
        response = client.post("/api/rooms/", json=room_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_list_rooms_with_data(self, client, sample_room):
        """Test listing rooms when rooms exist."""
        response = client.get("/api/rooms/")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == sample_room.id
        assert data[0]["name"] == sample_room.name
    
    def test_get_room_success(self, client, sample_room):
        """Test retrieving a specific room successfully."""
        response = client.get(f"/api/rooms/{sample_room.id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == sample_room.id
        assert data["name"] == sample_room.name
        assert data["capacity"] == sample_room.capacity
    
    def test_get_room_not_found(self, client):
        """Test retrieving non-existent room fails."""
        response = client.get("/api/rooms/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_create_room_no_location(self, client):
        """Test creating a room without location (optional field)."""
        room_data = {
            "name": "Room Without Location",
            "capacity": 8
        }
        response = client.post("/api/rooms/", json=room_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["name"] == room_data["name"]
        assert data["location"] is None
