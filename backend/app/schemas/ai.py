from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.schemas.schedule import ScheduleGenerateResponse


class AiPlanRequest(BaseModel):
    prompt: str = Field(min_length=1)
    start_date: datetime
    end_date: datetime
    apply: bool = True


class AiExplainRequest(BaseModel):
    start_date: datetime
    end_date: datetime


class PlannedTaskOut(BaseModel):
    name: str
    estimated_duration_minutes: int
    priority: int = 0
    preferred_time_of_day: Optional[str] = None
    deadline: Optional[datetime] = None
    earliest_start: Optional[datetime] = None
    splittable: bool = False


class PlannedAvailabilityOut(BaseModel):
    day_of_week: int
    start_minutes: int
    end_minutes: int
    weekdays_only: bool = False


class PlannedConstraintOut(BaseModel):
    constraint_type: str
    day_of_week: Optional[int] = None
    start_minutes: Optional[int] = None
    end_minutes: Optional[int] = None
    value: Optional[int] = None
    every_weekday: bool = False


class PlanIntentOut(BaseModel):
    raw_prompt: str
    tasks: list[PlannedTaskOut]
    availability: list[PlannedAvailabilityOut]
    constraints: list[PlannedConstraintOut]
    notes: list[str]
    parser: str


class AiPlanCreated(BaseModel):
    tasks: list[dict[str, Any]]
    availability: list[dict[str, Any]]
    constraints: list[dict[str, Any]]


class AiPlanResponse(BaseModel):
    intent: PlanIntentOut
    created: AiPlanCreated
    schedule: Optional[ScheduleGenerateResponse] = None
    assistant_message: str


class AiSuggestionsResponse(BaseModel):
    suggestions: list[str]
