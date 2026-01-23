"""
models.py: Pydantic models for request/response validation

This module defines all Pydantic models used for data validation
in the ReservationAPI. These models are used for request validation,
response serialization, and data transfer between layers.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class RoomBase(BaseModel):
    """
    Base model for room data.
    
    Attributes:
        name: Unique name of the meeting room
        capacity: Maximum number of people the room can accommodate
        location: Physical location of the room (optional)
    """
    name: str = Field(..., min_length=1, max_length=100, description="Room name")
    capacity: int = Field(..., gt=0, description="Room capacity")
    location: Optional[str] = Field(None, max_length=200, description="Room location")


class RoomCreate(RoomBase):
    """
    Model for creating a new room.
    Inherits all fields from RoomBase.
    """
    pass


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


class ReservationBase(BaseModel):
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
    title: str = Field(..., min_length=1, max_length=200, description="Reservation title")
    description: Optional[str] = Field(None, max_length=1000, description="Reservation description")
    start_time: datetime = Field(..., description="Start time (must be on the hour)")
    end_time: datetime = Field(..., description="End time (must be on the hour)")
    created_by: str = Field(..., min_length=1, max_length=100, description="Creator name")

    @field_validator('start_time', 'end_time')
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
            raise ValueError("Reservation times must be on the hour (e.g., 10:00, 14:00)")
        return v


class ReservationCreate(ReservationBase):
    """
    Model for creating a new reservation.
    Inherits all fields from ReservationBase with validation.
    """
    pass


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


class ErrorResponse(BaseModel):
    """
    Model for error responses.
    
    Attributes:
        detail: Error message or description
    """
    detail: str
