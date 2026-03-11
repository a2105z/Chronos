"""Greedy task allocation into available slots."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from app.models.constraint import Constraint
from app.models.task import Task
from app.services.scheduler.constraints import getMaxContinuousWorkMinutes


@dataclass
class AllocatedBlock:
    """A block of time assigned to a task."""

    task_id: int
    task_name: str
    start_time: datetime
    end_time: datetime
    duration_minutes: int


def slotOverlapsAny(slotStart: datetime, slotEnd: datetime, usedRanges: list[tuple[datetime, datetime]]) -> bool:
    """Return True if slot overlaps any used range."""
    for (uStart, uEnd) in usedRanges:
        if slotEnd <= uStart:
            continue
        if slotStart >= uEnd:
            continue
        return True
    return False



def orderTasks(tasks: list[Task]) -> list[Task]:
    """Order tasks by deadline (soonest first), then by priority (higher first)."""
    withDeadline = []
    withoutDeadline = []
    for t in tasks:
        if t.deadline is not None:
            withDeadline.append(t)
        else:
            withoutDeadline.append(t)

    def byDeadlineThenPriority(t: Task):
        key = (t.deadline, -t.priority)
        return key

    def byPriorityDesc(t: Task):
        key = -t.priority
        return key

    withDeadline.sort(key=byDeadlineThenPriority)
    withoutDeadline.sort(key=byPriorityDesc)

    result = []
    result.extend(withDeadline)
    result.extend(withoutDeadline)
    return result



def allocateTasks(tasks: list[Task], slots: list[tuple[datetime, datetime]], constraints: Optional[list[Constraint]] = None) -> list[AllocatedBlock]:
    """Greedily allocate tasks to slots. No overlaps. Respects splittable flag and max_continuous_work."""
    ordered = orderTasks(tasks)
    usedRanges: list[tuple[datetime, datetime]] = []
    blocks: list[AllocatedBlock] = []
    maxContinuousWork: Optional[int] = None
    if constraints:
        maxContinuousWork = getMaxContinuousWorkMinutes(constraints)

    for task in ordered:
        remaining = task.estimated_duration_minutes
        if remaining <= 0:
            continue

        mustSplit = maxContinuousWork is not None and remaining > maxContinuousWork
        if task.splittable or mustSplit:
            allocateSplittable(task, remaining, slots, usedRanges, blocks, maxContinuousWork)
        else:
            allocateFixed(task, remaining, slots, usedRanges, blocks, maxContinuousWork)

    return blocks



def allocateSplittable(task: Task, remaining: int, slots: list[tuple[datetime, datetime]], usedRanges: list[tuple[datetime, datetime]], blocks: list[AllocatedBlock], maxContinuousWork: Optional[int] = None) -> None:
    """Allocate a splittable task across one or more slot runs."""
    for (slotStart, slotEnd) in slots:
        if remaining <= 0:
            break
        if slotOverlapsAny(slotStart, slotEnd, usedRanges):
            continue

        slotMins = int((slotEnd - slotStart).total_seconds() / 60)
        allocMins = min(remaining, slotMins)
        if maxContinuousWork is not None and allocMins > maxContinuousWork:
            allocMins = maxContinuousWork
        if allocMins <= 0:
            continue

        blockEnd = slotStart + timedelta(minutes=allocMins)
        newBlock = AllocatedBlock(
            task_id=task.id,
            task_name=task.name,
            start_time=slotStart,
            end_time=blockEnd,
            duration_minutes=allocMins,
        )
        blocks.append(newBlock)
        usedRanges.append((slotStart, blockEnd))
        remaining -= allocMins



def allocateFixed(task: Task, remaining: int, slots: list[tuple[datetime, datetime]], usedRanges: list[tuple[datetime, datetime]], blocks: list[AllocatedBlock], maxContinuousWork: Optional[int] = None) -> None:
    """Allocate a non-splittable task in one contiguous block."""
    runStart = None
    runEnd = None
    runMins = 0

    for (slotStart, slotEnd) in slots:
        if runMins >= remaining:
            break
        if slotOverlapsAny(slotStart, slotEnd, usedRanges):
            runStart = None
            runEnd = None
            runMins = 0
            continue

        slotMins = int((slotEnd - slotStart).total_seconds() / 60)

        if runEnd is None or slotStart != runEnd:
            runStart = slotStart
            runEnd = slotEnd
            runMins = slotMins
        else:
            runEnd = slotEnd
            runMins += slotMins

        if runMins >= remaining:
            allocMins = remaining
            if maxContinuousWork is not None and allocMins > maxContinuousWork:
                allocMins = maxContinuousWork
            blockEnd = runStart + timedelta(minutes=allocMins)
            newBlock = AllocatedBlock(
                task_id=task.id,
                task_name=task.name,
                start_time=runStart,
                end_time=blockEnd,
                duration_minutes=allocMins,
            )
            blocks.append(newBlock)
            usedRanges.append((runStart, blockEnd))
            break
