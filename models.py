"""
models.py: SQLModel models for database tables and request/response validation

This module defines all SQLModel table models and schemas used for data validation
in the ReservationAPI. These models are used for database tables, request validation,
response serialization, and data transfer between layers.
"""

from datetime import datetime, timedelta, timezone
from typing_extensions import Self
from sqlmodel import SQLModel, Field, Relationship, DateTime
from pydantic import field_validator, model_validator


def get_datetime_now() -> datetime:
    """Get the current datetime in Finland timezone.

    Returns:
        datetime: Current datetime in Finland timezone
    """

    return datetime.now(timezone.utc).replace(tzinfo=None)


# Database Table Models
class Room(SQLModel, table=True):  # pylint: disable=too-few-public-methods
    """
    SQLModel table for the rooms table.

    Attributes:
        id: Primary key
        name: Unique room name
        capacity: Maximum occupancy
        location: Physical location description
        created_at: Record creation timestamp
        reservations: Relationship to Reservation model
    """

    __tablename__ = "rooms"

    id: int | None = Field(default=None, primary_key=True, index=True)
    name: str = Field(unique=True, max_length=255, index=True)
    capacity: int = Field(default=1, gt=0)
    location: str | None = Field(default=None, max_length=255)
    created_at: datetime | None = Field(
        default_factory=get_datetime_now,
        sa_type=DateTime,
    )

    # Relationship to reservations

    reservations: list["Reservation"] = Relationship(back_populates="room")


# Schema Models for Request/Response Validation
class RoomBase(SQLModel):
    """
    Base model for room data.

    Attributes:
        name: Unique name of the meeting room
        capacity: Maximum number of people the room can accommodate
        location: Physical location of the room (optional)
    """

    name: str = Field(..., min_length=1, max_length=255, description="Room name")
    capacity: int = Field(..., gt=0, description="Room capacity")
    location: str | None = Field(
        default=None, max_length=255, description="Room location"
    )


class RoomCreate(RoomBase):
    """
    Model for creating a new room.
    Inherits all fields from RoomBase.
    """

    pass


class RoomUpdate(RoomBase):
    """
    Model for updating an existing room.
    Inherits all fields from RoomBase.
    """

    name: str | None = Field(default=None, max_length=255, description="Room name")
    capacity: int | None = Field(default=None, gt=0, description="Room capacity")


class RoomResponse(RoomBase):
    """
    Model for room response data.

    Attributes:
        id: Unique identifier for the room
        created_at: Timestamp when the room was created
    """

    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ReservationBase(SQLModel):
    """
    Base model for reservation data.

    Attributes:
        room_id: ID of the room being reserved
        title: Title/purpose of the reservation
        description: Detailed description of the meeting (optional)
        start_time: Start time of the reservation (must be on the hour)
        end_time: End time of the reservation (must be on the hour)
        created_by: Name or identifier of the person making the reservation
    """

    room_id: int = Field(..., gt=0, description="Room ID")
    title: str = Field(
        ..., min_length=1, max_length=255, description="Reservation title"
    )
    description: str | None = Field(
        None, max_length=255, description="Reservation description"
    )
    start_time: datetime = Field(
        sa_type=DateTime(timezone=False), description="Start time (must be on the hour)"
    )
    end_time: datetime = Field(
        sa_type=DateTime(timezone=False), description="End time (must be on the hour)"
    )
    created_by: str = Field(
        ..., min_length=1, max_length=255, description="Creator name"
    )

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_on_the_hour(cls, v: datetime) -> datetime:
        """
        Validate that the time is on the hour (minute = 0, second = 0).

        Args:
            v: The datetime value to validate

        Returns:
            The validated datetime value

        Raises:
            ValueError: If the time is not on the hour
        """
        if v.minute != 0 or v.second != 0 or v.microsecond != 0:
            raise ValueError(
                "Reservation times must be on the hour (e.g., 10:00, 14:00)"
            )
        return v


class Reservation(SQLModel, table=True):  # pylint: disable=too-few-public-methods
    """
    SQLModel table for the reservations table.

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

    id: int | None = Field(default=None, primary_key=True, index=True)
    room_id: int = Field(foreign_key="rooms.id", index=True)
    title: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=255)
    start_time: datetime = Field(sa_type=DateTime(timezone=False), index=True)
    end_time: datetime = Field(sa_type=DateTime(timezone=False), index=True)
    created_by: str | None = Field(default=None)
    created_at: datetime | None = Field(
        default_factory=get_datetime_now,
        sa_type=DateTime,
    )

    # Relationship to room
    room: Room | None = Relationship(back_populates="reservations")


class ReservationCreate(ReservationBase):
    """
    Model for creating a new reservation.
    Inherits all fields from ReservationBase with validation.
    """

    @field_validator("start_time", "end_time")
    @classmethod
    def naive_datetime(cls, v: datetime) -> datetime:
        """
        Ensure datetime is naive (no timezone info).

        Args:
            v: The datetime value to validate
        Returns:
            The validated naive datetime value
        Raises:
            ValueError: If datetime has timezone info
        """
        if v.tzinfo is not None:
            raise ValueError("Datetime must be naive (no timezone info)")
        return v

    @model_validator(mode="after")
    def validate_reservation_times(self) -> Self:
        """
        Validate that the end_time is after the start_time.

        Args:
            values: Dictionary of field values
        Returns:
            Dictionary of validated field values
        Raises:
            ValueError: If end_time is not after start_time
        """
        start_time = self.start_time
        end_time = self.end_time
        if start_time and end_time and end_time <= start_time:
            raise ValueError("End time must be after start time")
        if start_time and start_time < get_datetime_now():
            raise ValueError(
                f"Start time cannot be in the past {start_time} < {get_datetime_now()})"
            )
        if start_time and end_time and end_time < start_time + timedelta(hours=1):
            raise ValueError("Reservation must be at least 1 hour long")
        return self


class ReservationUpdate(ReservationBase):
    """
    Model for updating an existing reservation.
    Inherits all fields from ReservationBase with validation.
    """

    room_id: int | None = Field(default=None, gt=0, description="Room ID")
    title: str | None = Field(
        default=None, min_length=1, max_length=255, description="Reservation title"
    )
    start_time: datetime | None = Field(default=None, description="Start time")
    end_time: datetime | None = Field(default=None, description="End time")
    created_by: str | None = Field(
        default=None, min_length=1, max_length=255, description="Creator name"
    )


class ReservationResponse(ReservationBase):
    """
    Model for reservation response data.

    Attributes:
        id: Unique identifier for the reservation
        created_at: Timestamp when the reservation was created
    """

    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class Message(SQLModel):
    """
    Model for simple message responses.

    Attributes:
        message: Message string
    """

    message: str


class ErrorResponse(SQLModel):
    """
    Model for error responses.

    Attributes:
        detail: Error message or description
    """

    detail: str
