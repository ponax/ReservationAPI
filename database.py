"""
database.py: Database configuration and session management

This module provides database configuration, session management,
and initialization functions for the ReservationAPI.
"""

import os
from sqlmodel import SQLModel, Session, create_engine, select
from models import Room

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./reservations.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def init_db() -> None:
    """Initialize the database by creating tables and loading initial data."""
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        room_exists = session.exec(select(Room)).first()
        if room_exists:
            return

        rooms = [
            Room(name="Conference Room A", location="Floor 1, Wing A", capacity=10),
            Room(name="Meeting Room B", location="Floor 2, Wing B", capacity=6),
            Room(name="Board Room", location="Floor 3, Executive Suite", capacity=20),
        ]

        session.add_all(rooms)
        session.commit()
