"""Task request/response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    """Shared task fields."""

    name: str
    estimated_duration_minutes: int = Field(ge=1)
    priority: int = Field(default=0, ge=0)
    deadline: Optional[datetime] = None
    splittable: bool = False


class TaskCreate(TaskBase):
    """Create payload."""

    pass


class TaskUpdate(BaseModel):
    """Partial update. All fields optional."""

    name: Optional[str] = None
    estimated_duration_minutes: Optional[int] = Field(default=None, ge=1)
    priority: Optional[int] = Field(default=None, ge=0)
    deadline: Optional[datetime] = None
    splittable: Optional[bool] = None


class TaskRead(TaskBase):
    """API response with id and timestamps."""

    id: int
    created_at: datetime
    updated_at: datetime
