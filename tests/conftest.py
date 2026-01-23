"""
tests/conftest.py: Pytest configuration and fixtures

This module provides shared fixtures for testing the ReservationAPI,
including test database setup and test client configuration.
"""

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from database import Base, get_db


# Use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite:///./test_reservations.db"


@pytest.fixture(scope="function")
def test_db():
    """
    Create a test database for each test function.
    
    Yields:
        SQLAlchemy database session for testing
    """
    # Create test engine
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop tables after test
        Base.metadata.drop_all(bind=engine)
        # Properly dispose the engine
        engine.dispose()
        # Remove test database file
        if os.path.exists("test_reservations.db"):
            try:
                os.remove("test_reservations.db")
            except PermissionError:
                pass  # Ignore on Windows if file is still locked


@pytest.fixture(scope="function")
def client(test_db):
    """
    Create a test client with overridden database dependency.
    
    Args:
        test_db: Test database session fixture
        
    Yields:
        FastAPI test client
    """
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_room(test_db):
    """
    Create a sample room for testing.
    
    Args:
        test_db: Test database session
        
    Returns:
        Created room object
    """
    from database import Room
    
    room = Room(
        name="Test Room",
        capacity=10,
        location="Test Location"
    )
    test_db.add(room)
    test_db.commit()
    test_db.refresh(room)
    return room


@pytest.fixture
def sample_reservation(test_db, sample_room):
    """
    Create a sample reservation for testing.
    
    Args:
        test_db: Test database session
        sample_room: Sample room fixture
        
    Returns:
        Created reservation object
    """
    from database import Reservation
    from datetime import datetime, timedelta
    import pytz
    
    tz = pytz.timezone('Europe/Helsinki')
    now = datetime.now(tz)
    start = now.replace(hour=14, minute=0, second=0, microsecond=0) + timedelta(days=1)
    end = start + timedelta(hours=2)
    
    reservation = Reservation(
        room_id=sample_room.id,
        title="Test Meeting",
        description="Test Description",
        start_time=start,
        end_time=end,
        created_by="Test User"
    )
    test_db.add(reservation)
    test_db.commit()
    test_db.refresh(reservation)
    return reservation
