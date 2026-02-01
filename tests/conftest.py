"""Fixtures for testing the Reservation API."""
from datetime import datetime, timedelta, timezone
import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from fastapi.testclient import TestClient
from main import app
from api.deps import get_db
from models import Room, Reservation

@pytest.fixture(name="engine")
def engine_fixture():
    """Create a test database engine."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)
    engine.dispose()
    
@pytest.fixture(name="session")
def session_fixture(engine):
    """Create a fresh test database session for each test."""
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with overridden database session."""

    def get_db_override():
        return session

    app.dependency_overrides[get_db] = get_db_override

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(name="test_room")
def test_room_fixture(session: Session):
    """Create a test room."""
    room = Room(name="Test Conference Room", capacity=10, location="Test Floor 1")
    session.add(room)
    session.commit()
    session.refresh(room)
    return room


@pytest.fixture(name="test_reservation")
def test_reservation_fixture(session: Session, test_room: Room):
    """Create a test reservation."""

    start_time = datetime.now(timezone.utc).replace(
        minute=0, second=0, microsecond=0
    ) + timedelta(hours=12)
    end_time = start_time + timedelta(hours=2)

    reservation = Reservation(
        room_id=test_room.id,
        title="Test Meeting",
        description="Test Description",
        start_time=start_time,
        end_time=end_time,
        created_by="Test User",
    )
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    return reservation
