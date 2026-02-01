"""Tests for room endpoints."""

from datetime import datetime
from fastapi.testclient import TestClient
import pytest
from sqlmodel import Session

from models import Room


def test_create_room(client: TestClient):
    """Test creating a new room."""
    response = client.post(
        "/api/rooms",
        json={"name": "New Conference Room", "capacity": 15, "location": "Floor 2"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Conference Room"
    assert data["capacity"] == 15
    assert data["location"] == "Floor 2"
    assert "id" in data
    assert "created_at" in data


def test_create_room_duplicate_name(client: TestClient, test_room: Room):
    """Test creating a room with duplicate name."""
    response = client.post(
        "/api/rooms",
        json={"name": test_room.name, "capacity": 10, "location": "Floor 1"},
    )
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"].lower()


def test_create_room_invalid_capacity(client: TestClient):
    """Test creating a room with invalid capacity."""
    response = client.post(
        "/api/rooms",
        json={"name": "Invalid Room", "capacity": 0, "location": "Floor 1"},
    )
    assert response.status_code == 422


def test_get_rooms(client: TestClient, test_room: Room):
    """Test listing all rooms."""
    response = client.get("/api/rooms")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(room["id"] == test_room.id for room in data)


def test_get_room_by_id(client: TestClient, test_room: Room):
    """Test getting a room by ID."""
    response = client.get(f"/api/rooms/{test_room.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_room.id
    assert data["name"] == test_room.name


def test_get_room_not_found(client: TestClient):
    """Test getting a non-existent room."""
    response = client.get("/api/rooms/99999")
    assert response.status_code == 404


def test_update_room(client: TestClient, test_room: Room):
    """Test updating a room."""
    response = client.put(
        f"/api/rooms/{test_room.id}",
        json={"capacity": 20, "location": "Updated Floor 3"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["capacity"] == 20
    assert data["location"] == "Updated Floor 3"
    assert data["name"] == test_room.name


def test_update_room_not_found(client: TestClient):
    """Test updating a non-existent room."""
    response = client.put("/api/rooms/99999", json={"capacity": 20})
    assert response.status_code == 404


def test_delete_room(client: TestClient, session: Session):
    """Test deleting a room."""
    room = Room(name="Room to Delete", capacity=5, location="Floor 1")
    session.add(room)
    session.commit()
    session.refresh(room)

    response = client.delete(f"/api/rooms/{room.id}")
    assert response.status_code == 200
    assert "deleted" in response.json()["message"].lower()


def test_delete_room_not_found(client: TestClient):
    """Test deleting a non-existent room."""
    response = client.delete("/api/rooms/99999")
    assert response.status_code == 404


def test_delete_room_with_reservations(client: TestClient, test_room: Room, test_reservation):
    """Test deleting a room that has reservations."""
    response = client.delete(f"/api/rooms/{test_room.id}")
    assert response.status_code == 409
    assert "cannot delete" in response.json()["detail"].lower()
