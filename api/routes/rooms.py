"""
api/routes/rooms.py: Room management endpoints

This module provides REST API endpoints for managing meeting rooms,
including listing existing rooms and adding new rooms to the system.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db, Room
from models import RoomCreate, RoomResponse

router = APIRouter()


@router.get(
    "/",
    response_model=List[RoomResponse],
    summary="List all rooms",
    description="Get a list of all available meeting rooms."
)
def list_rooms(db: Session = Depends(get_db)) -> List[RoomResponse]:
    """
    List all available meeting rooms.
    
    Args:
        db: Database session
        
    Returns:
        List of all rooms
    """
    rooms = db.query(Room).order_by(Room.name).all()
    return rooms


@router.post(
    "/",
    response_model=RoomResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new room",
    description="Add a new meeting room to the system."
)
def create_room(
    room: RoomCreate,
    db: Session = Depends(get_db)
) -> RoomResponse:
    """
    Create a new meeting room.
    
    Args:
        room: Room data
        db: Database session
        
    Returns:
        Created room data
        
    Raises:
        HTTPException: If a room with the same name already exists
    """
    # Check if room with same name exists
    existing_room = db.query(Room).filter(Room.name == room.name).first()
    if existing_room:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Room with name '{room.name}' already exists"
        )
    
    # Create room
    db_room = Room(**room.model_dump())
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    
    return db_room


@router.get(
    "/{room_id}",
    response_model=RoomResponse,
    summary="Get room details",
    description="Get details of a specific meeting room."
)
def get_room(
    room_id: int,
    db: Session = Depends(get_db)
) -> RoomResponse:
    """
    Get details of a specific room.
    
    Args:
        room_id: ID of the room
        db: Database session
        
    Returns:
        Room data
        
    Raises:
        HTTPException: If room not found
    """
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with ID {room_id} not found"
        )
    
    return room
