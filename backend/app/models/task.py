"""Task database model."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    """A schedulable task with duration, priority, optional deadline."""

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    estimated_duration_minutes: int = Field(ge=1)
    priority: int = Field(default=0, ge=0)
    deadline: Optional[datetime] = None
    splittable: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
