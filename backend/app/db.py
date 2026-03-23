"""Database configuration and session management."""

from typing import Generator

from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import text

from app.models.task import Task
from app.models.availability import AvailabilityWindow
from app.models.constraint import Constraint
from app.models.schedule import ScheduledBlock


DATABASE_URL = "sqlite:///./chronos.db"
engine = create_engine(DATABASE_URL, echo=False)


def createDbAndTables() -> None:
    """Create tables if they don't exist."""
    SQLModel.metadata.create_all(engine)
    ensureTaskColumns()


def ensureTaskColumns() -> None:
    """Best-effort local migration for new task scheduling fields."""
    with engine.begin() as conn:
        rows = conn.execute(text("PRAGMA table_info(tasks)")).fetchall()
        existingColumns = {row[1] for row in rows}
        if "earliest_start" not in existingColumns:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN earliest_start DATETIME"))
        if "preferred_time_of_day" not in existingColumns:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN preferred_time_of_day VARCHAR"))



def getSession() -> Generator[Session, None, None]:
    """Provide a DB session per request. Session is closed when request ends."""
    with Session(engine) as session:
        yield session
