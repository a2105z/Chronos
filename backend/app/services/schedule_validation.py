from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional

from sqlmodel import select

from app.core.timeutil import asCstNaive, assertNotInPast
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
    validateWithinAvailability,
)

if TYPE_CHECKING:
    from sqlmodel import Session


def asNaiveLocal(dt: datetime) -> datetime:
    """Back-compat alias — Chronos wall-clock is America/Chicago."""
    return asCstNaive(dt)


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


def _friendlyValidationError(exc: AssertionError) -> str:
    msg = str(exc)
    lower = msg.lower()
    if "not within any availability" in lower:
        return "Outside your availability hours (check Availability — weekends may be empty)."
    if "overlap" in lower and "protected" in lower:
        return "That time hits a protected block (lunch/exam/etc)."
    if "overlap" in lower:
        return "That time overlaps another block."
    if "max_continuous" in lower:
        return "Block is longer than your max continuous work limit."
    return msg


def validateMovedBlock(
    session: "Session",
    blockId: int,
    newStart: datetime,
    newEnd: datetime,
    fallbackWindows: list[AvailabilityWindow],
    allowDurationChange: bool = False
) -> None:
    """Raise ValueError with a human-readable reason if the move/resize is invalid."""
    block = session.get(ScheduledBlock, blockId)
    if not block:
        raise ValueError("Scheduled block not found")

    newStart = asCstNaive(newStart)
    newEnd = asCstNaive(newEnd)

    durationMins = int((newEnd - newStart).total_seconds() / 60)
    if durationMins < 15:
        raise ValueError("Blocks must be at least 15 minutes")
    if not allowDurationChange and durationMins != block.duration_minutes:
        raise ValueError("New time range must preserve the block duration")

    assertNotInPast(newStart)

    task = session.get(Task, block.task_id)
    if not task:
        raise ValueError("Task not found for this block")

    if not isSlotAllowedForTask(task, newStart, newEnd):
        raise ValueError("That time is before the task’s earliest start or after its deadline.")

    windows = getAvailabilityWindows(session, userId=block.user_id)
    if not windows:
        windows = fallbackWindows

    constraintsStmt = select(Constraint)
    if block.user_id is not None:
        constraintsStmt = constraintsStmt.where(Constraint.user_id == block.user_id)
    constraints = list(session.exec(constraintsStmt).all())

    protected = _protectedAsDicts(constraints)
    maxContinuousWork = getMaxContinuousWorkMinutes(constraints)

    othersStmt = select(ScheduledBlock).where(ScheduledBlock.id != blockId)
    if block.user_id is not None:
        othersStmt = othersStmt.where(ScheduledBlock.user_id == block.user_id)
    others = list(session.exec(othersStmt).all())

    # Only check the moved block against others — do NOT re-validate old blocks.
    moved = {
        "start_time": newStart,
        "end_time": newEnd,
        "duration_minutes": durationMins
    }
    overlapCheck = [
        {
            "start_time": asCstNaive(o.start_time),
            "end_time": asCstNaive(o.end_time),
            "duration_minutes": o.duration_minutes
        }
        for o in others
    ]
    overlapCheck.append(moved)

    try:
        validateNoOverlap(overlapCheck)
        validateWithinAvailability([moved], _windowsAsDicts(windows))
        validateNoProtectedOverlap([moved], protected)
        if maxContinuousWork is not None:
            validateMaxContinuousWork([moved], maxContinuousWork)
    except AssertionError as exc:
        raise ValueError(_friendlyValidationError(exc)) from exc


def validateNewBlock(
    session: "Session",
    userId: int,
    newStart: datetime,
    newEnd: datetime,
    fallbackWindows: list[AvailabilityWindow],
    excludeBlockId: Optional[int] = None
) -> None:
    """Validate a brand-new block placement."""
    newStart = asCstNaive(newStart)
    newEnd = asCstNaive(newEnd)
    durationMins = int((newEnd - newStart).total_seconds() / 60)
    if durationMins < 15:
        raise ValueError("Blocks must be at least 15 minutes")

    assertNotInPast(newStart)

    windows = getAvailabilityWindows(session, userId=userId)
    if not windows:
        windows = fallbackWindows

    constraints = list(
        session.exec(select(Constraint).where(Constraint.user_id == userId)).all()
    )
    protected = _protectedAsDicts(constraints)
    maxContinuousWork = getMaxContinuousWorkMinutes(constraints)

    othersStmt = select(ScheduledBlock).where(ScheduledBlock.user_id == userId)
    if excludeBlockId is not None:
        othersStmt = othersStmt.where(ScheduledBlock.id != excludeBlockId)
    others = list(session.exec(othersStmt).all())

    created = {
        "start_time": newStart,
        "end_time": newEnd,
        "duration_minutes": durationMins
    }
    overlapCheck = [
        {
            "start_time": asCstNaive(o.start_time),
            "end_time": asCstNaive(o.end_time),
            "duration_minutes": o.duration_minutes
        }
        for o in others
    ]
    overlapCheck.append(created)

    try:
        validateNoOverlap(overlapCheck)
        validateWithinAvailability([created], _windowsAsDicts(windows))
        validateNoProtectedOverlap([created], protected)
        if maxContinuousWork is not None:
            validateMaxContinuousWork([created], maxContinuousWork)
    except AssertionError as exc:
        raise ValueError(_friendlyValidationError(exc)) from exc


def computeEndFromStart(start: datetime, durationMinutes: int) -> datetime:
    return asCstNaive(start) + timedelta(minutes=durationMinutes)
