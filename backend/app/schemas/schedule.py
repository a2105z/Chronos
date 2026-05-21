from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ScheduledBlockRead(BaseModel):
    """Scheduled block for calendar display."""

    id: int
    task_id: int
    task_name: str
    start_time: datetime
    end_time: datetime
    duration_minutes: int


class UnscheduledDiagnostic(BaseModel):
    """Why a task could not be fully placed."""

    task_id: int
    task_name: str
    reason: str
    detail: str


class ScheduleGenerateRequest(BaseModel):
    """Schedule generation request."""

    start_date: datetime
    end_date: datetime
    replace_existing: bool = True


class ScheduleGenerateResponse(BaseModel):
    """Structured generate result with diagnostics."""

    blocks: list[ScheduledBlockRead]
    unscheduled: list[UnscheduledDiagnostic]
    summary: str


class ScheduledBlockMove(BaseModel):
    """Move and/or resize a block. End can be derived from duration or set explicitly."""

    start_time: datetime = Field(..., description="New start datetime for the block")
    end_time: Optional[datetime] = Field(default=None, description="Optional new end (resize)")
    duration_minutes: Optional[int] = Field(default=None, ge=15, description="Optional new duration")


class ScheduledBlockCreate(BaseModel):
    """Create a calendar block (and task if needed) by dragging/selecting on the grid."""

    title: str = Field(min_length=1, max_length=200)
    start_time: datetime
    end_time: datetime
