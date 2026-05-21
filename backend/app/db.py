from datetime import datetime, timedelta
from typing import Generator

from sqlalchemy import text
from sqlmodel import Session, SQLModel, create_engine, select

from app.core.config import getSettings
from app.core.security import hashPassword
from app.models.availability import AvailabilityWindow
from app.models.constraint import Constraint
from app.models.task import Task
from app.models.user import User

settings = getSettings()
engine = create_engine(settings.DATABASE_URL, echo=False)


def createDbAndTables() -> None:
    """Create tables if they don't exist and apply lightweight migrations."""
    SQLModel.metadata.create_all(engine)
    ensureUserIdColumns()
    ensureTaskColumns()


def _tableExists(conn, tableName: str) -> bool:
    row = conn.execute(
        text("SELECT name FROM sqlite_master WHERE type='table' AND name=:name"),
        {"name": tableName}
    ).fetchone()
    return row is not None


def _existingColumns(conn, tableName: str) -> set[str]:
    if not _tableExists(conn, tableName):
        return set()
    rows = conn.execute(text(f"PRAGMA table_info({tableName})")).fetchall()
    return {row[1] for row in rows}


def ensureUserIdColumns() -> None:
    """Best-effort local migration for user_id foreign keys."""
    tables = ["tasks", "availability_windows", "constraints", "scheduled_blocks"]
    with engine.begin() as conn:
        for tableName in tables:
            cols = _existingColumns(conn, tableName)
            if cols and "user_id" not in cols:
                conn.execute(text(f"ALTER TABLE {tableName} ADD COLUMN user_id INTEGER"))


def ensureTaskColumns() -> None:
    """Best-effort local migration for new task scheduling fields."""
    with engine.begin() as conn:
        existingColumns = _existingColumns(conn, "tasks")
        if existingColumns:
            if "earliest_start" not in existingColumns:
                conn.execute(text("ALTER TABLE tasks ADD COLUMN earliest_start DATETIME"))
            if "preferred_time_of_day" not in existingColumns:
                conn.execute(text("ALTER TABLE tasks ADD COLUMN preferred_time_of_day VARCHAR"))


def seedDemoUserIfNeeded() -> None:
    """Create demo@chronos.app with sample week data when no users exist."""
    with Session(engine) as session:
        existing = session.exec(select(User)).first()
        if existing is not None:
            return

        user = User(
            email="demo@chronos.app",
            hashed_password=hashPassword("chronos-demo"),
            name="Demo Intern",
            created_at=datetime.utcnow()
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        assert user.id is not None

        # Weekday availability 9–5
        for day in range(5):
            session.add(
                AvailabilityWindow(
                    user_id=user.id,
                    day_of_week=day,
                    start_minutes=9 * 60,
                    end_minutes=17 * 60
                )
            )

        # Protect lunch weekdays
        for day in range(5):
            session.add(
                Constraint(
                    user_id=user.id,
                    constraint_type="protected_block",
                    day_of_week=day,
                    start_minutes=12 * 60,
                    end_minutes=13 * 60
                )
            )

        session.add(
            Constraint(
                user_id=user.id,
                constraint_type="max_continuous_work",
                value=120
            )
        )

        tomorrow = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        friday = tomorrow
        while friday.weekday() != 4:
            friday = friday + timedelta(days=1)

        session.add(
            Task(
                user_id=user.id,
                name="Polish Chronos resume",
                estimated_duration_minutes=180,
                priority=8,
                preferred_time_of_day="morning",
                earliest_start=tomorrow,
                splittable=True
            )
        )
        session.add(
            Task(
                user_id=user.id,
                name="Study algorithms",
                estimated_duration_minutes=90,
                priority=6,
                deadline=friday.replace(hour=17, minute=0),
                splittable=True
            )
        )
        session.add(
            Task(
                user_id=user.id,
                name="Mock interview prep",
                estimated_duration_minutes=60,
                priority=7,
                preferred_time_of_day="afternoon"
            )
        )
        session.commit()


def getSession() -> Generator[Session, None, None]:
    """Provide a DB session per request. Session is closed when request ends."""
    with Session(engine) as session:
        yield session
