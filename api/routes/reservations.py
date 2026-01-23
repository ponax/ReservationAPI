"""
api/routes/reservations.py: Reservation management endpoints

This module provides REST API endpoints for managing meeting room reservations,
including creating, listing, and canceling reservations with business logic validation.
"""

from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import pytz

from database import get_db, Reservation, Room
from models import ReservationCreate, ReservationResponse

router = APIRouter()

# Finland timezone
FINLAND_TZ = pytz.timezone('Europe/Helsinki')


def validate_reservation_business_rules(
    db: Session,
    reservation: ReservationCreate,
    exclude_reservation_id: int = None
) -> None:
    """
    Validate reservation against business rules.
    
    Args:
        db: Database session
        reservation: Reservation data to validate
        exclude_reservation_id: Optional reservation ID to exclude from duplicate check (for updates)
        
    Raises:
        HTTPException: If any business rule is violated
    """
    # Get current time in Finland timezone
    now = datetime.now(FINLAND_TZ)
    
    # Make start_time and end_time timezone-aware if they aren't already
    start_time = reservation.start_time
    end_time = reservation.end_time
    
    if start_time.tzinfo is None:
        start_time = FINLAND_TZ.localize(start_time)
    if end_time.tzinfo is None:
        end_time = FINLAND_TZ.localize(end_time)
    
    # Business Rule 2: Reservation time cannot be in the past
    if start_time < now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reservation start time cannot be in the past"
        )
    
    # Business Rule 3: Start time must be before end time
    if start_time >= end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reservation start time must be before end time"
        )
    
    # Validate minimum duration (1 hour)
    duration_hours = (end_time - start_time).total_seconds() / 3600
    if duration_hours < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Minimum reservation duration is 1 hour"
        )
    
    # Verify room exists
    room = db.query(Room).filter(Room.id == reservation.room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with ID {reservation.room_id} not found"
        )
    
    # Business Rule 1: Check for duplicate/overlapping reservations
    query = db.query(Reservation).filter(
        Reservation.room_id == reservation.room_id,
        Reservation.start_time < end_time,
        Reservation.end_time > start_time
    )
    
    if exclude_reservation_id:
        query = query.filter(Reservation.id != exclude_reservation_id)
    
    overlapping = query.first()
    if overlapping:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Time slot conflicts with existing reservation (ID: {overlapping.id})"
        )


@router.post(
    "/",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new reservation",
    description="Create a reservation for a meeting room. Reservations must be at least 1 hour long and start on the hour."
)
def create_reservation(
    reservation: ReservationCreate,
    db: Session = Depends(get_db)
) -> ReservationResponse:
    """
    Create a new meeting room reservation.
    
    Args:
        reservation: Reservation data
        db: Database session
        
    Returns:
        Created reservation data
        
    Raises:
        HTTPException: If validation fails or conflicts exist
    """
    # Validate business rules
    validate_reservation_business_rules(db, reservation)
    
    # Create reservation
    db_reservation = Reservation(**reservation.model_dump())
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    
    return db_reservation


@router.get(
    "/room/{room_id}",
    response_model=List[ReservationResponse],
    summary="List reservations for a room",
    description="Get all reservations for a specific meeting room."
)
def list_reservations_by_room(
    room_id: int,
    db: Session = Depends(get_db)
) -> List[ReservationResponse]:
    """
    List all reservations for a specific room.
    
    Args:
        room_id: ID of the room
        db: Database session
        
    Returns:
        List of reservations for the room
        
    Raises:
        HTTPException: If room not found
    """
    # Verify room exists
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with ID {room_id} not found"
        )
    
    # Get reservations ordered by start time
    reservations = db.query(Reservation)\
        .filter(Reservation.room_id == room_id)\
        .order_by(Reservation.start_time)\
        .all()
    
    return reservations


@router.delete(
    "/{reservation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel a reservation",
    description="Delete/cancel an existing reservation."
)
def cancel_reservation(
    reservation_id: int,
    db: Session = Depends(get_db)
) -> None:
    """
    Cancel (delete) a reservation.
    
    Args:
        reservation_id: ID of the reservation to cancel
        db: Database session
        
    Raises:
        HTTPException: If reservation not found
    """
    # Find reservation
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reservation with ID {reservation_id} not found"
        )
    
    # Delete reservation
    db.delete(reservation)
    db.commit()


@router.get(
    "/",
    response_model=List[ReservationResponse],
    summary="List all reservations",
    description="Get all reservations across all rooms."
)
def list_all_reservations(
    db: Session = Depends(get_db)
) -> List[ReservationResponse]:
    """
    List all reservations in the system.
    
    Args:
        db: Database session
        
    Returns:
        List of all reservations
    """
    reservations = db.query(Reservation)\
        .order_by(Reservation.start_time)\
        .all()
    
    return reservations
