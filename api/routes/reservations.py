"""
api/routes/reservations.py: Reservation management endpoints

This module provides REST API endpoints for managing meeting room reservations,
including creating, listing, and canceling reservations with business logic validation.
"""

from typing import List, Any
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
import crud
from api.deps import SessionDep
from models import Message, Reservation, ReservationCreate, ReservationResponse, ReservationUpdate

router = APIRouter(
    prefix="/reservations",
    tags=["reservations"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new reservation",
    description="Create a reservation for a meeting room. "
    "Reservations must be at least 1 hour long and start on the hour.", 
)
def create_reservation(
    *, session: SessionDep, reservation_in: ReservationCreate
) -> Any:
    """
    Create a new meeting room reservation.

    Args:
        reservation: Reservation data
        session: Database session

    Returns:
        Created reservation data
    """
    if not crud.get_room_by_id(
        session=session, room_id=reservation_in.room_id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with ID {reservation_in.room_id} not found",
        )
    statement = (
        select(Reservation)
        .where(Reservation.room_id == reservation_in.room_id)
        .where(Reservation.start_time < reservation_in.end_time)
        .where(Reservation.end_time > reservation_in.start_time)
    )
    existing_reservation = session.exec(statement).first()

    if existing_reservation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Room {reservation_in.room_id}"
            f" is already reserved during the selected time range "
            f"(from {existing_reservation.start_time} to {existing_reservation.end_time})",
        )
    db_reservation = crud.create_reservation(
        session=session, reservation_in=reservation_in
    )
    return db_reservation

@router.get(
    "/{reservation_id}",
    response_model=ReservationResponse,
    summary="Get reservation details",
    description="Get details of a specific reservation.",
)
def get_reservation_by_id(session: SessionDep, reservation_id: int) -> Any:
    """
    Get details of a specific reservation.

    Args:
        reservation_id: ID of the reservation
        session: Database session

    Returns:
        Reservation data

    Raises:
        HTTPException: If reservation not found
    """
    reservation = crud.get_reservation_by_id(
        session=session, reservation_id=reservation_id
    )
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reservation with ID {reservation_id} not found",
        )

    return reservation


@router.get(
    "/room/{room_id}",
    response_model=List[ReservationResponse],
    summary="List reservations for a room",
    description="Get all reservations for a specific meeting room.",
)
def list_reservations_by_room(session: SessionDep, room_id: int) -> Any:
    """
    List all reservations for a specific room.

    Args:
        room_id: ID of the room
        session: Database session

    Returns:
        List of reservations for the room

    Raises:
        HTTPException: If room not found
    """
    # Verify room exists
    room = crud.get_room_by_id(session=session, room_id=room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with ID {room_id} not found",
        )

    # Get reservations ordered by start time
    reservations = crud.get_reservations_by_room(session=session, room_id=room_id)
    return reservations


@router.put(
    "/{reservation_id}",
    response_model=ReservationResponse,
    summary="Update a reservation",
    description="Update an existing reservation's details.",
)
def update_reservation(
    *, session: SessionDep, reservation_id: int, reservation_in: ReservationUpdate
) -> Any:
    """
    Update an existing reservation.

    Args:
        reservation_id: ID of the reservation to update
        reservation_in: Updated reservation data
        session: Database session

    Returns:
        Updated reservation data

    Raises:
        HTTPException: If reservation not found
    """
    db_reservation = crud.get_reservation_by_id(
        session=session, reservation_id=reservation_id
    )
    if not db_reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reservation with ID {reservation_id} not found",
        )
    db_reservation = crud.update_reservation(
        session=session, db_reservation=db_reservation, reservation_in=reservation_in
    )
    return db_reservation


@router.delete(
    "/{reservation_id}",
    summary="Cancel a reservation",
    description="Delete/cancel an existing reservation.",
)
def cancel_reservation(session: SessionDep, reservation_id: int) -> Message:
    """
    Cancel (delete) a reservation.

    Args:
        session: Database session
        reservation_id: ID of the reservation to cancel

    Raises:
        HTTPException: If reservation not found
    """
    # Find reservation
    reservation = crud.get_reservation_by_id(
        session=session, reservation_id=reservation_id
    )
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reservation with ID {reservation_id} not found",
        )
    session.delete(reservation)
    session.commit()
    return Message(message=f"Reservation with ID {reservation_id} has been canceled")


@router.get(
    "/",
    response_model=List[ReservationResponse],
    summary="List all reservations",
    description="Get all reservations across all rooms.",
)
def list_all_reservations(session: SessionDep) -> List[ReservationResponse]:
    """
    List all reservations in the system.

    Args:
        session: Database session

    Returns:
        List of all reservations
    """
    reservations = crud.get_reservations(session=session)
    return reservations
