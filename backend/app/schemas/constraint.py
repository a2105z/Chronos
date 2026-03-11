"""Constraint request/response schemas and validation."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class ConstraintType(str, Enum):
    """Supported constraint types."""

    protected_block = "protected_block"
    max_continuous_work = "max_continuous_work"


def validateConstraintFields(constraintType: str, dayOfWeek: Optional[int], startMinutes: Optional[int], endMinutes: Optional[int], value: Optional[int]) -> None:
    """Validate that fields match the constraint type."""
    if constraintType == ConstraintType.protected_block:
        if dayOfWeek is None or startMinutes is None or endMinutes is None:
            raise ValueError(
                "protected_block requires day_of_week, start_minutes, end_minutes"
            )
        if startMinutes >= endMinutes:
            raise ValueError("start_minutes must be less than end_minutes")
    elif constraintType == ConstraintType.max_continuous_work:
        if value is None or value < 1:
            raise ValueError("max_continuous_work requires value >= 1 (minutes)")
    else:
        valid = []
        for t in ConstraintType:
            valid.append(t.value)
        raise ValueError(f"constraint_type must be one of: {valid}")


class ConstraintBase(BaseModel):
    """Base constraint fields."""

    constraint_type: str
    day_of_week: Optional[int] = Field(default=None, ge=0, le=6)
    start_minutes: Optional[int] = Field(default=None, ge=0, le=1440)
    end_minutes: Optional[int] = Field(default=None, ge=0, le=1440)
    value: Optional[int] = None
    metadata_json: Optional[str] = None


class ConstraintCreate(ConstraintBase):
    """Create payload. Validates based on type."""

    @model_validator(mode="after")
    def validateByType(self):
        validateConstraintFields(self.constraint_type, self.day_of_week, self.start_minutes, self.end_minutes, self.value)
        return self


class ConstraintUpdate(BaseModel):
    """Partial update."""

    constraint_type: Optional[str] = None
    day_of_week: Optional[int] = Field(default=None, ge=0, le=6)
    start_minutes: Optional[int] = Field(default=None, ge=0, le=1440)
    end_minutes: Optional[int] = Field(default=None, ge=0, le=1440)
    value: Optional[int] = None
    metadata_json: Optional[str] = None


class ConstraintRead(ConstraintBase):
    """API response."""

    id: int
