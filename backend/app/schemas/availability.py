"""Availability request/response schemas."""

from typing import Optional

from pydantic import BaseModel, Field, model_validator


class AvailabilityBase(BaseModel):
    """Availability window. start must be before end."""

    day_of_week: int = Field(ge=0, le=6)
    start_minutes: int = Field(ge=0, le=1440)
    end_minutes: int = Field(ge=0, le=1440)

    @model_validator(mode="after")
    def startBeforeEnd(self):
        if self.start_minutes >= self.end_minutes:
            raise ValueError("start_minutes must be less than end_minutes")
        return self


class AvailabilityCreate(AvailabilityBase):
    """Create payload."""

    pass


class AvailabilityUpdate(BaseModel):
    """Partial update. API validates start < end after merge."""

    day_of_week: Optional[int] = Field(default=None, ge=0, le=6)
    start_minutes: Optional[int] = Field(default=None, ge=0, le=1440)
    end_minutes: Optional[int] = Field(default=None, ge=0, le=1440)


class AvailabilityRead(AvailabilityBase):
    """API response."""

    id: int
