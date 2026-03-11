"""Availability window database model."""

from typing import Optional

from sqlmodel import Field, SQLModel


class AvailabilityWindow(SQLModel, table=True):
    """Recurring weekly window. day_of_week: 0=Mon, 6=Sun."""

    __tablename__ = "availability_windows"

    id: Optional[int] = Field(default=None, primary_key=True)
    day_of_week: int = Field(ge=0, le=6)
    start_minutes: int = Field(ge=0, le=1440)
    end_minutes: int = Field(ge=0, le=1440)
