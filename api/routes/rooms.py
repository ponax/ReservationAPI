"""
api/routes/rooms.py: Room management endpoints

This module provides REST API endpoints for managing meeting rooms,
including listing existing rooms and adding new rooms to the system.
"""

from typing import Any, List
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from api.deps import SessionDep
import crud
from models import Room, RoomCreate, RoomResponse, Message, RoomUpdate

router = APIRouter(
    prefix="/rooms",
    tags=["rooms"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/",
    response_model=List[RoomResponse],
    summary="List all rooms",
    description="Get a list of all available meeting rooms.",
)
def list_rooms(session: SessionDep) -> Any:
    """
    List all available meeting rooms.

    Args:
        session: Database session

    Returns:
        List of all rooms
    """
    rooms = crud.get_rooms(session=session)
    return rooms


@router.post(
    "/",
    response_model=RoomResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new room",
    description="Add a new meeting room to the system.",
)
def create_room(
    *,
    session: SessionDep,
    room_in: RoomCreate,
) -> Any:
    """
    Create a new meeting room.

    Args:
        session: Database session
        room_in: Room data

    Returns:
        Created room data
    """
    try:
        db_room = crud.create_room(session=session, room=room_in)
        return db_room
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Room with name '{room_in.name}' already exists",
        ) from e


@router.get(
    "/{room_id}",
    response_model=RoomResponse,
    summary="Get room details",
    description="Get details of a specific meeting room.",
)
def get_room(room_id: int, session: SessionDep) -> Any:
    """
    Get details of a specific room.

    Args:
        room_id: ID of the room
        session: Database session

    Returns:
        Room data

    Raises:
        HTTPException: If room not found
    """
    room = crud.get_room_by_id(session=session, room_id=room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with ID {room_id} not found",
        )

    return room


@router.put(
    "/{room_id}",
    response_model=RoomResponse,
    summary="Update a room",
    description="Update details of a specific meeting room.",
)
def update_room(
    *,
    session: SessionDep,
    room_id: int,
    room_in: RoomUpdate,
) -> Any:
    """
    Update details of a specific room.

    Args:
        session: Database session
        room_id: ID of the room
        room_in: Updated room data

    Returns:
        Updated room data

    Raises:
        HTTPException: If room not found or name conflict occurs
    """
    db_room = crud.get_room_by_id(session=session, room_id=room_id)
    # Check if room exists
    if not db_room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with ID {room_id} not found",
        )

    # Check for name conflict
    if room_in.name:
        existing_room = crud.get_room_by_name(session=session, name=room_in.name)
        if existing_room and existing_room.id != room_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Room with name '{room_in.name}' already exists",
            )

    db_room = crud.update_room(session=session, db_room=db_room, room_in=room_in)
    return db_room


@router.delete(
    "/{room_id}",
    summary="Delete a room",
    description="Delete a specific meeting room.",
)
def delete_room(session: SessionDep, room_id: int) -> Message:
    """
    Delete a specific room.

    Args:
        session: Database session
        room_id: ID of the room

    Raises:
        HTTPException: If room not found
    """
    room = session.get(Room, room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with ID {room_id} not found",
        )
    if room.reservations:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete room with existing reservations",
        )
    session.delete(room)
    session.commit()
    return Message(message=f"Room with ID {room_id} has been deleted.")
