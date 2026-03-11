"""Schedule request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class ScheduledBlockRead(BaseModel):
    """Scheduled block for calendar display."""

    id: int
    task_id: int
    task_name: str
    start_time: datetime
    end_time: datetime
    duration_minutes: int


class ScheduleGenerateRequest(BaseModel):
    """Schedule generation request."""

    start_date: datetime
    end_date: datetime
    replace_existing: bool = True
