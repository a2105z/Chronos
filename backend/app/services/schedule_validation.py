from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from sqlmodel import select

from app.models.availability import AvailabilityWindow
from app.models.constraint import Constraint
from app.models.schedule import ScheduledBlock
from app.models.task import Task
from app.services.availability import getAvailabilityWindows
from app.services.scheduler.allocator import isSlotAllowedForTask
from app.services.scheduler.constraints import (
    getMaxContinuousWorkMinutes,
    validateMaxContinuousWork,
    validateNoOverlap,
    validateNoProtectedOverlap,
    validateWithinAvailability
)

if TYPE_CHECKING:
    from sqlmodel import Session


def _windowsAsDicts(windows: list[AvailabilityWindow]) -> list[dict]:
    return [
        {"day_of_week": w.day_of_week, "start_minutes": w.start_minutes, "end_minutes": w.end_minutes}
        for w in windows
    ]


def _protectedAsDicts(constraints: list[Constraint]) -> list[dict]:
    out = []
    for c in constraints:
        if c.constraint_type != "protected_block":
            continue
        out.append(
            {
                "constraint_type": "protected_block",
                "day_of_week": c.day_of_week,
                "start_minutes": c.start_minutes,
                "end_minutes": c.end_minutes
            }
        )
    return out


def validateMovedBlock(
    session: "Session",
    blockId: int,
    newStart: datetime,
    newEnd: datetime,
    fallbackWindows: list[AvailabilityWindow]
) -> None:
    """Raise ValueError with a human-readable reason if the move is invalid."""
    block = session.get(ScheduledBlock, blockId)
    if not block:
        raise ValueError("Scheduled block not found")

    durationMins = int((newEnd - newStart).total_seconds() / 60)
    if durationMins != block.duration_minutes:
        raise ValueError("New time range must preserve the block duration")

    task = session.get(Task, block.task_id)
    if not task:
        raise ValueError("Task not found for this block")

    if not isSlotAllowedForTask(task, newStart, newEnd):
        raise ValueError("Block violates task earliest start, deadline, or preferred time of day")

    windows = getAvailabilityWindows(session)
    if not windows:
        windows = fallbackWindows

    constraints = list(session.exec(select(Constraint)).all())

    protected = _protectedAsDicts(constraints)
    maxContinuousWork = getMaxContinuousWorkMinutes(constraints)

    others = list(session.exec(select(ScheduledBlock).where(ScheduledBlock.id != blockId)).all())

    blockDicts: list[dict] = []
    for o in others:
        blockDicts.append(
            {
                "start_time": o.start_time,
                "end_time": o.end_time,
                "duration_minutes": o.duration_minutes
            }
        )
    blockDicts.append(
        {
            "start_time": newStart,
            "end_time": newEnd,
            "duration_minutes": durationMins
        }
    )

    try:
        windowDicts = _windowsAsDicts(windows)
        validateNoOverlap(blockDicts)
        validateWithinAvailability(blockDicts, windowDicts)
        validateNoProtectedOverlap(blockDicts, protected)
        if maxContinuousWork is not None:
            validateMaxContinuousWork(blockDicts, maxContinuousWork)
    except AssertionError as exc:
        raise ValueError(str(exc)) from exc


def computeEndFromStart(start: datetime, durationMinutes: int) -> datetime:
    return start + timedelta(minutes=durationMinutes)
