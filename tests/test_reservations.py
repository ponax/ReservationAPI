"""Tests for reservation endpoints."""

from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlmodel import Session

from models import Room, Reservation


def test_create_reservation(client: TestClient, test_room: Room):
    """Test creating a new reservation."""
    start_time = datetime.now(timezone.utc).replace(
        minute=0, second=0, microsecond=0
    ) + timedelta(hours=3)
    end_time = start_time + timedelta(hours=2)

    response = client.post(
        "/api/reservations",
        json={
            "room_id": test_room.id,
            "title": "New Meeting",
            "description": "Test meeting",
            "start_time": start_time.replace(tzinfo=None).isoformat(),
            "end_time": end_time.replace(tzinfo=None).isoformat(),
            "created_by": "Test User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Meeting"
    assert data["room_id"] == test_room.id
    assert "id" in data


def test_create_reservation_invalid_room(client: TestClient):
    """Test creating a reservation with invalid room ID."""
    start_time = datetime.now(timezone.utc).replace(
        minute=0, second=0, microsecond=0
    ) + timedelta(hours=3)
    end_time = start_time + timedelta(hours=2)

    response = client.post(
        "/api/reservations",
        json={
            "room_id": 99999,
            "title": "New Meeting",
            "start_time": start_time.replace(tzinfo=None).isoformat(),
            "end_time": end_time.replace(tzinfo=None).isoformat(),
            "created_by": "Test User",
        },
    )
    assert response.status_code == 404


def test_create_reservation_past_time(client: TestClient, test_room: Room):
    """Test creating a reservation in the past."""
    start_time = datetime.now(timezone.utc).replace(
        minute=0, second=0, microsecond=0
    ) - timedelta(hours=1)
    end_time = start_time + timedelta(hours=2)

    response = client.post(
        "/api/reservations",
        json={
            "room_id": test_room.id,
            "title": "Past Meeting",
            "start_time": start_time.replace(tzinfo=None).isoformat(),
            "end_time": end_time.replace(tzinfo=None).isoformat(),
            "created_by": "Test User",
        },
    )
    assert response.status_code == 422


def test_create_reservation_end_before_start(client: TestClient, test_room: Room):
    """Test creating a reservation with end time before start time."""
    start_time = datetime.now(timezone.utc).replace(
        minute=0, second=0, microsecond=0
    ) + timedelta(hours=3)
    end_time = start_time - timedelta(hours=1)

    response = client.post(
        "/api/reservations",
        json={
            "room_id": test_room.id,
            "title": "Invalid Meeting",
            "start_time": start_time.replace(tzinfo=None).isoformat(),
            "end_time": end_time.replace(tzinfo=None).isoformat(),
            "created_by": "Test User",
        },
    )
    assert response.status_code == 422


def test_create_reservation_not_on_hour(client: TestClient, test_room: Room):
    """Test creating a reservation not on the hour."""
    start_time = datetime.now(timezone.utc).replace(
        minute=30, second=0, microsecond=0
    ) + timedelta(hours=3)
    end_time = start_time + timedelta(hours=2)

    response = client.post(
        "/api/reservations",
        json={
            "room_id": test_room.id,
            "title": "Invalid Time Meeting",
            "start_time": start_time.replace(tzinfo=None).isoformat(),
            "end_time": end_time.replace(tzinfo=None).isoformat(),
            "created_by": "Test User",
        },
    )
    assert response.status_code == 422

def test_create_reservation_with_timezone(client: TestClient, test_room: Room):
    """Test creating a reservation with timezone-aware datetime."""
    start_time = datetime.now(timezone.utc).replace(
        minute=0, second=0, microsecond=0
    ) + timedelta(hours=3)
    end_time = start_time + timedelta(hours=2)

    response = client.post(
        "/api/reservations",
        json={
            "room_id": test_room.id,
            "title": "Timezone Meeting",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "created_by": "Test User",
        },
    )
    assert response.status_code == 422

def test_create_reservation_too_short(client: TestClient, test_room: Room):
    """Test creating a reservation less than 1 hour."""
    start_time = datetime.now(timezone.utc).replace(
        minute=0, second=0, microsecond=0
    ) + timedelta(hours=3)
    end_time = start_time + timedelta(minutes=30)

    response = client.post(
        "/api/reservations",
        json={
            "room_id": test_room.id,
            "title": "Short Meeting",
            "start_time": start_time.replace(tzinfo=None).isoformat(),
            "end_time": end_time.isoformat(),
            "created_by": "Test User",
        },
    )
    assert response.status_code == 422


def test_create_reservation_overlap_exact(
    client: TestClient, test_room: Room, test_reservation: Reservation
):
    """Test creating a reservation with exact same time as existing."""
    response = client.post(
        "/api/reservations",
        json={
            "room_id": test_room.id,
            "title": "Overlapping Meeting",
            "start_time": test_reservation.start_time.replace(tzinfo=None).isoformat(),
            "end_time": test_reservation.end_time.replace(tzinfo=None).isoformat(),
            "created_by": "Test User",
        },
    )
    assert response.status_code == 409
    assert "already reserved" in response.json()["detail"].lower()


def test_create_reservation_overlap_partial_start(
    client: TestClient, test_room: Room, test_reservation: Reservation
):
    """Test creating a reservation that starts during existing reservation."""
    start_time = test_reservation.start_time + timedelta(hours=1)
    end_time = test_reservation.end_time + timedelta(hours=1)

    response = client.post(
        "/api/reservations",
        json={
            "room_id": test_room.id,
            "title": "Overlapping Meeting",
            "start_time": start_time.replace(tzinfo=None).isoformat(),
            "end_time": end_time.replace(tzinfo=None).isoformat(),
            "created_by": "Test User",
        },
    )
    assert response.status_code == 409
    assert "already reserved" in response.json()["detail"].lower()


def test_create_reservation_overlap_partial_end(
    client: TestClient, test_room: Room, test_reservation: Reservation
):
    """Test creating a reservation that ends during existing reservation."""
    start_time = test_reservation.start_time - timedelta(hours=1)
    end_time = test_reservation.start_time + timedelta(hours=1)

    response = client.post(
        "/api/reservations",
        json={
            "room_id": test_room.id,
            "title": "Overlapping Meeting",
            "start_time": start_time.replace(tzinfo=None).isoformat(),
            "end_time": end_time.replace(tzinfo=None).isoformat(),
            "created_by": "Test User",
        },
    )
    assert response.status_code == 409
    assert "already reserved" in response.json()["detail"].lower()


def test_create_reservation_overlap_encompasses(
    client: TestClient, test_room: Room, test_reservation: Reservation
):
    """Test creating a reservation that encompasses existing reservation."""
    start_time = test_reservation.start_time - timedelta(hours=1)
    end_time = test_reservation.end_time + timedelta(hours=1)

    response = client.post(
        "/api/reservations",
        json={
            "room_id": test_room.id,
            "title": "Overlapping Meeting",
            "start_time": start_time.replace(tzinfo=None).isoformat(),
            "end_time": end_time.replace(tzinfo=None).isoformat(),
            "created_by": "Test User",
        },
    )
    assert response.status_code == 409
    assert "already reserved" in response.json()["detail"].lower()


def test_create_reservation_no_overlap_before(
    client: TestClient, test_room: Room, test_reservation: Reservation
):
    """Test creating a reservation before existing reservation (no overlap)."""
    start_time = test_reservation.start_time - timedelta(hours=3)
    end_time = test_reservation.start_time - timedelta(hours=1)

    response = client.post(
        "/api/reservations",
        json={
            "room_id": test_room.id,
            "title": "Before Meeting",
            "start_time": start_time.replace(tzinfo=None).isoformat(),
            "end_time": end_time.replace(tzinfo=None).isoformat(),
            "created_by": "Test User",
        },
    )
    assert response.status_code == 201


def test_create_reservation_no_overlap_after(
    client: TestClient, test_room: Room, test_reservation: Reservation
):
    """Test creating a reservation after existing reservation (no overlap)."""
    start_time = test_reservation.end_time + timedelta(hours=1)
    end_time = start_time + timedelta(hours=2)

    response = client.post(
        "/api/reservations",
        json={
            "room_id": test_room.id,
            "title": "After Meeting",
            "start_time": start_time.replace(tzinfo=None).isoformat(),
            "end_time": end_time.replace(tzinfo=None).isoformat(),
            "created_by": "Test User",
        },
    )
    assert response.status_code == 201


def test_create_reservation_different_room(
    client: TestClient, session: Session, test_reservation: Reservation
):
    """Test creating a reservation for different room at same time (should succeed)."""
    other_room = Room(name="Other Room", capacity=5, location="Floor 2")
    session.add(other_room)
    session.commit()
    session.refresh(other_room)

    response = client.post(
        "/api/reservations",
        json={
            "room_id": other_room.id,
            "title": "Different Room Meeting",
            "start_time": test_reservation.start_time.replace(tzinfo=None).isoformat(),
            "end_time": test_reservation.end_time.replace(tzinfo=None).isoformat(),
            "created_by": "Test User",
        },
    )
    assert response.status_code == 201


def test_get_reservations(client: TestClient, test_reservation: Reservation):
    """Test listing all reservations."""
    response = client.get("/api/reservations")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(res["id"] == test_reservation.id for res in data)


def test_get_reservation_by_id(client: TestClient, test_reservation: Reservation):
    """Test getting a reservation by ID."""
    response = client.get(f"/api/reservations/{test_reservation.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_reservation.id
    assert data["title"] == test_reservation.title


def test_get_reservation_not_found(client: TestClient):
    """Test getting a non-existent reservation."""
    response = client.get("/api/reservations/99999")
    assert response.status_code == 404


def test_get_reservations_by_room(
    client: TestClient, test_room: Room, test_reservation: Reservation
):
    """Test getting reservations by room ID."""
    response = client.get(f"/api/reservations/room/{test_room.id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert all(res["room_id"] == test_room.id for res in data)


def test_update_reservation(client: TestClient, test_reservation: Reservation):
    """Test updating a reservation."""
    response = client.put(
        f"/api/reservations/{test_reservation.id}",
        json={"title": "Updated Meeting", "description": "Updated description"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Meeting"
    assert data["description"] == "Updated description"


def test_update_reservation_not_found(client: TestClient):
    """Test updating a non-existent reservation."""
    response = client.put("/api/reservations/99999", json={"title": "Updated"})
    assert response.status_code == 404


def test_delete_reservation(client: TestClient, session: Session, test_room: Room):
    """Test deleting a reservation."""
    start_time = datetime.now(timezone.utc).replace(
        minute=0, second=0, microsecond=0
    ) + timedelta(hours=5)
    end_time = start_time + timedelta(hours=2)

    reservation = Reservation(
        room_id=test_room.id,
        title="To Delete",
        start_time=start_time,
        end_time=end_time,
        created_by="Test User",
    )
    session.add(reservation)
    session.commit()
    session.refresh(reservation)

    response = client.delete(f"/api/reservations/{reservation.id}")
    assert response.status_code == 200
    assert "canceled" in response.json()["message"].lower()


def test_delete_reservation_not_found(client: TestClient):
    """Test deleting a non-existent reservation."""
    response = client.delete("/api/reservations/99999")
    assert response.status_code == 404
