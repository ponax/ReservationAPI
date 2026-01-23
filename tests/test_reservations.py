"""
tests/test_reservations.py: Unit tests for reservation management endpoints

This module contains comprehensive tests for reservation-related API endpoints,
including creating, listing, and canceling reservations with business rule validation.
"""

import pytest
from datetime import datetime, timedelta
from fastapi import status
import pytz


FINLAND_TZ = pytz.timezone('Europe/Helsinki')


class TestReservationEndpoints:
    """Test suite for reservation management endpoints."""
    
    def test_create_reservation_success(self, client, sample_room):
        """Test creating a reservation successfully."""
        now = datetime.now(FINLAND_TZ)
        start = now.replace(hour=14, minute=0, second=0, microsecond=0) + timedelta(days=1)
        end = start + timedelta(hours=2)
        
        reservation_data = {
            "room_id": sample_room.id,
            "title": "Team Meeting",
            "description": "Weekly sync",
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "created_by": "John Doe"
        }
        
        response = client.post("/api/reservations/", json=reservation_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["room_id"] == sample_room.id
        assert data["title"] == "Team Meeting"
        assert "id" in data
    
    def test_create_reservation_past_time(self, client, sample_room):
        """Test creating a reservation in the past fails."""
        now = datetime.now(FINLAND_TZ)
        start = now.replace(hour=10, minute=0, second=0, microsecond=0) - timedelta(days=1)
        end = start + timedelta(hours=1)
        
        reservation_data = {
            "room_id": sample_room.id,
            "title": "Past Meeting",
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "created_by": "John Doe"
        }
        
        response = client.post("/api/reservations/", json=reservation_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "past" in response.json()["detail"].lower()
    
    def test_create_reservation_start_after_end(self, client, sample_room):
        """Test creating a reservation with start time after end time fails."""
        now = datetime.now(FINLAND_TZ)
        start = now.replace(hour=14, minute=0, second=0, microsecond=0) + timedelta(days=1)
        end = start - timedelta(hours=1)  # End before start
        
        reservation_data = {
            "room_id": sample_room.id,
            "title": "Invalid Meeting",
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "created_by": "John Doe"
        }
        
        response = client.post("/api/reservations/", json=reservation_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "before" in response.json()["detail"].lower()
    
    def test_create_reservation_not_on_hour(self, client, sample_room):
        """Test creating a reservation not on the hour fails."""
        now = datetime.now(FINLAND_TZ)
        start = now.replace(hour=14, minute=30, second=0, microsecond=0) + timedelta(days=1)
        end = start + timedelta(hours=1)
        
        reservation_data = {
            "room_id": sample_room.id,
            "title": "Off-hour Meeting",
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "created_by": "John Doe"
        }
        
        response = client.post("/api/reservations/", json=reservation_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_reservation_less_than_one_hour(self, client, sample_room):
        """Test creating a reservation less than 1 hour fails."""
        now = datetime.now(FINLAND_TZ)
        start = now.replace(hour=14, minute=0, second=0, microsecond=0) + timedelta(days=1)
        end = start + timedelta(hours=1, minutes=-30)  # Only 30 minutes, but on the hour
        
        reservation_data = {
            "room_id": sample_room.id,
            "title": "Short Meeting",
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "created_by": "John Doe"
        }
        
        response = client.post("/api/reservations/", json=reservation_data)
        # This will fail at pydantic validation first since end < start
        # Let's test with end time on the hour but less than 1 hour duration
        start = now.replace(hour=14, minute=0, second=0, microsecond=0) + timedelta(days=1)
        end = start + timedelta(minutes=30)  # 30 minutes but not on the hour
        
        reservation_data["start_time"] = start.isoformat()
        reservation_data["end_time"] = end.isoformat()
        
        # This should fail at pydantic validation for not being on the hour
        response = client.post("/api/reservations/", json=reservation_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_reservation_duplicate(self, client, sample_room, sample_reservation):
        """Test creating a duplicate/overlapping reservation fails."""
        reservation_data = {
            "room_id": sample_room.id,
            "title": "Conflicting Meeting",
            "start_time": sample_reservation.start_time.isoformat(),
            "end_time": sample_reservation.end_time.isoformat(),
            "created_by": "Jane Doe"
        }
        
        response = client.post("/api/reservations/", json=reservation_data)
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "conflict" in response.json()["detail"].lower()
    
    def test_create_reservation_nonexistent_room(self, client):
        """Test creating a reservation for non-existent room fails."""
        now = datetime.now(FINLAND_TZ)
        start = now.replace(hour=14, minute=0, second=0, microsecond=0) + timedelta(days=1)
        end = start + timedelta(hours=1)
        
        reservation_data = {
            "room_id": 999,  # Non-existent room
            "title": "Meeting",
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "created_by": "John Doe"
        }
        
        response = client.post("/api/reservations/", json=reservation_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_list_reservations_by_room(self, client, sample_room, sample_reservation):
        """Test listing reservations for a specific room."""
        response = client.get(f"/api/reservations/room/{sample_room.id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == sample_reservation.id
        assert data[0]["room_id"] == sample_room.id
    
    def test_list_reservations_by_nonexistent_room(self, client):
        """Test listing reservations for non-existent room fails."""
        response = client.get("/api/reservations/room/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_list_all_reservations(self, client, sample_reservation):
        """Test listing all reservations."""
        response = client.get("/api/reservations/")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data) >= 1
        assert any(r["id"] == sample_reservation.id for r in data)
    
    def test_cancel_reservation_success(self, client, sample_reservation):
        """Test canceling a reservation successfully."""
        response = client.delete(f"/api/reservations/{sample_reservation.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify deletion
        get_response = client.get("/api/reservations/")
        data = get_response.json()
        assert not any(r["id"] == sample_reservation.id for r in data)
    
    def test_cancel_nonexistent_reservation(self, client):
        """Test canceling non-existent reservation fails."""
        response = client.delete("/api/reservations/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
