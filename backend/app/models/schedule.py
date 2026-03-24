"""Scheduled block database model."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class ScheduledBlock(SQLModel, table=True):
    """A time block assigned to a task (or part of a splittable task)."""

    __tablename__ = "scheduled_blocks"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id")
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    schedule_run_id: Optional[str] = None  # groups blocks from same run
