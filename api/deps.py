"""Dependencies for API endpoints."""

from typing import Annotated
from collections.abc import Generator
from fastapi import Depends
from sqlmodel import Session
from database import engine


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.

    Yields:
        Database session
    """
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
