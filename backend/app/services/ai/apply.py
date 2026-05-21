from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlmodel import Session

from app.models.availability import AvailabilityWindow
from app.models.constraint import Constraint
from app.models.task import Task
from app.models.user import User
from app.schemas.schedule import ScheduleGenerateResponse
from app.services.ai.parser import PlanIntent
from app.services.availability import ensureDefaultAvailability
from app.services.scheduler.engine import SchedulingEngine


def applyPlanIntent(
    session: Session,
    user: User,
    intent: PlanIntent,
    startDate: datetime,
    endDate: datetime,
    runSchedule: bool = True
) -> dict[str, Any]:
    """Create tasks/constraints/availability from intent, then optionally schedule."""
    createdTasks: list[Task] = []
    createdAvailability: list[AvailabilityWindow] = []
    createdConstraints: list[Constraint] = []

    for planned in intent.tasks:
        task = Task(
            user_id=user.id,
            name=planned.name,
            estimated_duration_minutes=planned.estimated_duration_minutes,
            priority=planned.priority,
            preferred_time_of_day=planned.preferred_time_of_day,
            deadline=planned.deadline,
            earliest_start=planned.earliest_start,
            splittable=planned.splittable
        )
        session.add(task)
        createdTasks.append(task)

    for planned in intent.availability:
        days = list(range(5)) if planned.weekdays_only or planned.day_of_week < 0 else [planned.day_of_week]
        for day in days:
            window = AvailabilityWindow(
                user_id=user.id,
                day_of_week=day,
                start_minutes=planned.start_minutes,
                end_minutes=planned.end_minutes
            )
            session.add(window)
            createdAvailability.append(window)

    for planned in intent.constraints:
        days: list[Optional[int]]
        if planned.every_weekday:
            days = list(range(5))
        else:
            days = [planned.day_of_week]

        for day in days:
            constraint = Constraint(
                user_id=user.id,
                constraint_type=planned.constraint_type,
                day_of_week=day,
                start_minutes=planned.start_minutes,
                end_minutes=planned.end_minutes,
                value=planned.value
            )
            session.add(constraint)
            createdConstraints.append(constraint)

    session.commit()
    for t in createdTasks:
        session.refresh(t)
    for a in createdAvailability:
        session.refresh(a)
    for c in createdConstraints:
        session.refresh(c)

    assert user.id is not None
    defaults = ensureDefaultAvailability(session, user.id)
    if defaults:
        createdAvailability.extend(defaults)
        intent.notes.append(
            "No availability set yet — assumed weekdays 8am–10pm so Chronos can place blocks."
        )

    # Snapshot before generate() commits — expired ORM rows dump as empty dicts.
    taskSnapshots = [_snapshotModel(t) for t in createdTasks]
    availabilitySnapshots = [_snapshotModel(a) for a in createdAvailability]
    constraintSnapshots = [_snapshotModel(c) for c in createdConstraints]

    schedule: Optional[ScheduleGenerateResponse] = None
    if runSchedule:
        engine = SchedulingEngine(session, userId=user.id)
        schedule = engine.generate(startDate, endDate, replaceExisting=True)

    return {
        "tasks": taskSnapshots,
        "availability": availabilitySnapshots,
        "constraints": constraintSnapshots,
        "schedule": schedule
    }


def _snapshotModel(obj: Any) -> dict[str, Any]:
    """Stable JSON-friendly copy of an ORM row before session expire."""
    if hasattr(obj, "model_dump"):
        data = obj.model_dump()
        return data if isinstance(data, dict) else dict(data)
    return {k: getattr(obj, k) for k in obj.__dict__ if not k.startswith("_")}
