"""CRUD operations for Room and Reservation models."""

from sqlmodel import Session, select
from models import (
    Reservation,
    ReservationCreate,
    ReservationUpdate,
    Room,
    RoomCreate,
    RoomUpdate,
)


def create_room(*, session: Session, room: RoomCreate) -> Room:
    """Create a new room in the database.

    Args:
        session (Session): SQLModel Session object
        room (RoomCreate): RoomCreate object containing room data

    Returns:
        Room: Returns the created Room object
    """
    db_room = Room.model_validate(room)

    session.add(db_room)
    session.commit()
    session.refresh(db_room)

    return db_room


def update_room(*, session: Session, db_room: Room, room_in: RoomUpdate) -> Room:
    """Update an existing room in the database.

    Args:
        session (Session): SQLModel Session object
        db_room (Room): Room object to update
        room_in (RoomUpdate): RoomUpdate object containing updated room data

    Returns:
        Room: Returns the updated Room object
    """
    room_data = room_in.model_dump(exclude_unset=True)
    db_room.sqlmodel_update(room_data)
    session.add(db_room)
    session.commit()
    session.refresh(db_room)

    return db_room


def get_room_by_id(*, session: Session, room_id: int) -> Room | None:
    """Retrieve a room by its ID.

    Args:
        session (Session): SQLModel Session object
        room_id (int): ID of the room to retrieve

    Returns:
        Room | None: Returns the Room object if found, else None
    """
    statement = select(Room).where(Room.id == room_id)
    return session.exec(statement).first()


def get_room_by_name(*, session: Session, name: str) -> Room | None:
    """Retrieve a room by its name.

    Args:
        session (Session): SQLModel Session object
        name (str): Name of the room to retrieve

    Returns:
        Room | None: Returns the Room object if found, else None
    """
    statement = select(Room).where(Room.name == name)
    return session.exec(statement).first()


def get_rooms(*, session: Session) -> list[Room]:
    """List all rooms.

    Args:
        session (Session): SQLModel Session object

    Returns:
        list[Room]: List of Room objects
    """
    statement = select(Room)
    session_rooms = session.exec(statement).all()
    return session_rooms


def get_reservations(*, session: Session) -> list[Reservation]:
    """List all reservations.

    Args:
        session (Session): SQLModel Session object

    Returns:
        list[Reservation]: List of Reservation objects
    """
    statement = select(Reservation)
    session_reservations = session.exec(statement).all()
    return session_reservations


def create_reservation(
    *, session: Session, reservation_in: ReservationCreate
) -> Reservation:
    """Create a new reservation in the database.

    Args:
        session (Session): SQLModel Session object
        reservation_in (ReservationCreate): ReservationCreate object containing reservation data

    Returns:
        Reservation: Returns the created Reservation object

    Raises:
        ValueError: If a reservation already exists for the room in the selected time range
    """
    db_reservation = Reservation.model_validate(reservation_in)
    session.add(db_reservation)
    session.commit()
    session.refresh(db_reservation)

    return db_reservation


def update_reservation(
    *, session: Session, db_reservation: Reservation, reservation_in: ReservationUpdate
) -> Reservation:
    """Update an existing reservation in the database.

    Args:
        session (Session): SQLModel Session object
        db_reservation (Reservation): Reservation object to update
        reservation_in (ReservationUpdate): ReservationUpdate object
                                            containing updated reservation data

    Returns:
        Reservation: Returns the updated Reservation object
    """
    reservation_data = reservation_in.model_dump(exclude_unset=True)
    db_reservation.sqlmodel_update(reservation_data)
    session.add(db_reservation)
    session.commit()
    session.refresh(db_reservation)

    return db_reservation


def get_reservation_by_id(
    *, session: Session, reservation_id: int
) -> Reservation | None:
    """Retrieve a reservation by its ID.

    Args:
        session (Session): SQLModel Session object
        reservation_id (int): ID of the reservation to retrieve

    Returns:
        Reservation | None: Returns the Reservation object if found, else None
    """
    statement = select(Reservation).where(Reservation.id == reservation_id)
    return session.exec(statement).first()


def get_reservation_by_title(
    *, session: Session, reservation_title: str
) -> Reservation | None:
    """Retrieve a reservation by its title.

    Args:
        session (Session): SQLModel Session object
        reservation_title (str): Title of the reservation to retrieve

    Returns:
        Reservation | None: Returns the Reservation object if found, else None
    """
    statement = select(Reservation).where(Reservation.title == reservation_title)
    return session.exec(statement).first()


def get_reservations_by_room(*, session: Session, room_id: int) -> list[Reservation]:
    """List all reservations for a specific room.

    Args:
        session (Session): SQLModel Session object
        room_id (int): ID of the room
    Returns:
        list[Reservation]: List of Reservation objects for the specified room
    """
    statement = (
        select(Reservation)
        .where(Reservation.room_id == room_id)
        .order_by(Reservation.start_time)
    )
    return session.exec(statement).all()
