"""Database configuration and session management."""

from typing import Generator

from sqlmodel import SQLModel, create_engine, Session

from app.models.task import Task
from app.models.availability import AvailabilityWindow
from app.models.constraint import Constraint
from app.models.schedule import ScheduledBlock


DATABASE_URL = "sqlite:///./chronos.db"
engine = create_engine(DATABASE_URL, echo=False)


def createDbAndTables() -> None:
    """Create tables if they don't exist."""
    SQLModel.metadata.create_all(engine)



def getSession() -> Generator[Session, None, None]:
    """Provide a DB session per request. Session is closed when request ends."""
    with Session(engine) as session:
        yield session
