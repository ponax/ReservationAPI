"""
database.py: SQLAlchemy models and database configuration

This module defines the SQLAlchemy ORM models for the database tables
and provides database session management and initialization functions.
"""

import os
from datetime import datetime, UTC
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./reservations.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class Room(Base):
    """
    SQLAlchemy model for the rooms table.
    
    Attributes:
        id: Primary key
        name: Unique room name
        capacity: Maximum occupancy
        location: Physical location description
        created_at: Record creation timestamp
        reservations: Relationship to Reservation model
    """
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    capacity = Column(Integer, nullable=False)
    location = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    # Relationship to reservations
    reservations = relationship("Reservation", back_populates="room", cascade="all, delete-orphan")


class Reservation(Base):
    """
    SQLAlchemy model for the reservations table.
    
    Attributes:
        id: Primary key
        room_id: Foreign key to rooms table
        title: Reservation title/purpose
        description: Optional detailed description
        start_time: Reservation start time
        end_time: Reservation end time
        created_by: User who created the reservation
        created_at: Record creation timestamp
        room: Relationship to Room model
    """
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False, index=True)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    # Relationship to room
    room = relationship("Room", back_populates="reservations")


def get_db():
    """
    Dependency function to get database session.
    
    Yields:
        SQLAlchemy database session
        
    Usage:
        Used as a FastAPI dependency to provide database access to route handlers.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize the database by creating tables and loading initial data.
    
    This function:
    1. Creates all tables defined in the Base metadata
    2. Executes the schema.sql file to populate initial data
    
    Should be called once when the application starts.
    """
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Execute schema.sql for initial data
    schema_file = os.path.join(os.path.dirname(__file__), "schema.sql")
    if os.path.exists(schema_file):
        with open(schema_file, "r") as f:
            sql_script = f.read()
            # Split by semicolons and execute each statement
            statements = [stmt.strip() for stmt in sql_script.split(";") if stmt.strip()]
            with engine.connect() as conn:
                for statement in statements:
                    try:
                        conn.execute(text(statement))
                    except Exception as e:
                        # Skip errors for statements that might already be executed
                        pass
                conn.commit()


# Import text for raw SQL execution
from sqlalchemy import text
