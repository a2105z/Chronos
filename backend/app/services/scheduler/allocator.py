from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.models.constraint import Constraint
from app.models.task import Task
from app.services.scheduler.constraints import getMaxContinuousWorkMinutes
from app.services.scheduler.intervals import BusyTimeline
from app.services.scheduler.scoring import (
    choose_allocation_style,
    score_fixed_candidate,
    score_splittable_candidate,
    weights_for_style,
)

REASON_NO_CAPACITY = "no_capacity"
REASON_DEADLINE_IMPOSSIBLE = "deadline_impossible"
REASON_PREFERENCE_MISMATCH = "preference_mismatch"
REASON_MAX_CONTINUOUS_TRUNCATION = "max_continuous_truncation"
REASON_EARLIEST_START_BLOCKS = "earliest_start_blocks"
REASON_NO_AVAILABILITY = "no_availability"


@dataclass
class AllocatedBlock:
    """A block of time assigned to a task."""

    task_id: int
    task_name: str
    start_time: datetime
    end_time: datetime
    duration_minutes: int


@dataclass
class UnscheduledInfo:
    """Diagnostic for a task that was not fully scheduled."""

    task_id: int
    task_name: str
    reason: str
    detail: str


@dataclass
class AllocationResult:
    """Blocks plus unscheduled diagnostics."""

    blocks: list[AllocatedBlock] = field(default_factory=list)
    unscheduled: list[UnscheduledInfo] = field(default_factory=list)


def slotOverlapsAny(slotStart: datetime, slotEnd: datetime, usedRanges: list[tuple[datetime, datetime]]) -> bool:
    """Return True if slot overlaps any used range."""
    for (uStart, uEnd) in usedRanges:
        if slotEnd <= uStart:
            continue
        if slotStart >= uEnd:
            continue
        return True
    return False


def matchesTaskTimePreference(task: Task, slotStart: datetime) -> bool:
    """Return True if slot start time respects task's preferred period."""
    preferred = task.preferred_time_of_day
    if preferred is None or preferred == "anytime":
        return True
    hour = slotStart.hour
    if preferred == "morning":
        return 6 <= hour < 12
    if preferred == "afternoon":
        return 12 <= hour < 18
    if preferred == "evening":
        return 18 <= hour < 24
    return True


def isSlotAllowedForTask(task: Task, slotStart: datetime, slotEnd: datetime) -> bool:
    """Return True if slot respects hard constraints (earliest start + deadline). Preference is soft."""
    comparableStart = toUtcNaive(slotStart)
    comparableEnd = toUtcNaive(slotEnd)
    if task.earliest_start is not None and comparableStart < toUtcNaive(task.earliest_start):
        return False
    if task.deadline is not None and comparableEnd > toUtcNaive(task.deadline):
        return False
    return True


def toUtcNaive(value: datetime) -> datetime:
    """Normalize datetime for safe comparisons across timezone-aware/naive values."""
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)


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


def minutesAllocatedForTask(taskId: int, blocks: list[AllocatedBlock]) -> int:
    total = 0
    for b in blocks:
        if b.task_id == taskId:
            total += b.duration_minutes
    return total


def diagnoseUnscheduled(
    tasks: list[Task],
    blocks: list[AllocatedBlock],
    slots: list[tuple[datetime, datetime]],
    constraints: Optional[list[Constraint]] = None
) -> list[UnscheduledInfo]:
    """Explain why tasks were not fully placed."""
    diagnostics: list[UnscheduledInfo] = []
    maxContinuous = getMaxContinuousWorkMinutes(constraints or [])

    for task in tasks:
        if task.id is None:
            continue
        allocated = minutesAllocatedForTask(task.id, blocks)
        remaining = task.estimated_duration_minutes - allocated
        if remaining <= 0:
            continue

        reason, detail = _pickUnscheduledReason(task, remaining, slots, maxContinuous, allocated)
        diagnostics.append(
            UnscheduledInfo(task_id=task.id, task_name=task.name, reason=reason, detail=detail)
        )
    return diagnostics


def _pickUnscheduledReason(
    task: Task,
    remaining: int,
    slots: list[tuple[datetime, datetime]],
    maxContinuous: Optional[int],
    allocated: int
) -> tuple[str, str]:
    if not slots:
        return REASON_NO_AVAILABILITY, "No available time slots in the requested range."

    hardAllowed = []
    for slotStart, slotEnd in slots:
        if isSlotAllowedForTask(task, slotStart, slotEnd):
            hardAllowed.append((slotStart, slotEnd))

    if not hardAllowed:
        if task.earliest_start is not None:
            anyBeforeEarliest = True
            for slotStart, _ in slots:
                if toUtcNaive(slotStart) >= toUtcNaive(task.earliest_start):
                    anyBeforeEarliest = False
                    break
            if anyBeforeEarliest:
                return (
                    REASON_EARLIEST_START_BLOCKS,
                    f"No slots start on or after earliest_start={task.earliest_start.isoformat()}."
                )
        if task.deadline is not None:
            return (
                REASON_DEADLINE_IMPOSSIBLE,
                f"No slots finish before deadline={task.deadline.isoformat()}."
            )
        return REASON_NO_CAPACITY, f"{remaining} minutes remain with no hard-feasible slots."

    # Preference soft mismatch: all hard-allowed slots miss preference, and nothing was placed
    preferred = task.preferred_time_of_day
    if preferred and preferred != "anytime" and allocated == 0:
        prefMatches = [s for s in hardAllowed if matchesTaskTimePreference(task, s[0])]
        if not prefMatches:
            # Still could place elsewhere — if remaining, check capacity
            totalMinutes = 0
            for s, e in hardAllowed:
                totalMinutes += int((e - s).total_seconds() / 60)
            if totalMinutes < remaining:
                return (
                    REASON_PREFERENCE_MISMATCH,
                    f"Preferred {preferred} had no matching capacity; remaining {remaining} min could not fit elsewhere either."
                )

    if maxContinuous is not None and task.estimated_duration_minutes > maxContinuous and not task.splittable:
        if allocated > 0 and remaining > 0:
            return (
                REASON_MAX_CONTINUOUS_TRUNCATION,
                f"max_continuous_work={maxContinuous} truncated placement; {remaining} min left unscheduled."
            )

    if task.deadline is not None:
        # Check if remaining duration cannot fit before deadline even ignoring other tasks
        capacityBeforeDeadline = 0
        for s, e in hardAllowed:
            capacityBeforeDeadline += int((e - s).total_seconds() / 60)
        if capacityBeforeDeadline < remaining:
            return (
                REASON_DEADLINE_IMPOSSIBLE,
                f"Only {capacityBeforeDeadline} min feasible before deadline; need {remaining} more."
            )

    return REASON_NO_CAPACITY, f"{remaining} minutes could not be placed (capacity taken or fragmented)."


def allocateTasks(
    tasks: list[Task],
    slots: list[tuple[datetime, datetime]],
    constraints: Optional[list[Constraint]] = None
) -> AllocationResult:
    """Allocate tasks with scored greedy selection under hard constraints."""
    ordered = orderTasks(tasks)
    timeline = BusyTimeline()
    blocks: list[AllocatedBlock] = []
    lastEndByTask: dict[int, datetime] = {}
    style = choose_allocation_style(ordered)
    weights = weights_for_style(style)
    maxContinuousWork: Optional[int] = None
    if constraints:
        maxContinuousWork = getMaxContinuousWorkMinutes(constraints)

    for task in ordered:
        remaining = task.estimated_duration_minutes
        if remaining <= 0:
            continue

        mustSplit = maxContinuousWork is not None and remaining > maxContinuousWork
        if task.splittable or mustSplit:
            allocateSplittable(task, remaining, slots, timeline, blocks, lastEndByTask, weights, maxContinuousWork)
        else:
            allocateFixed(task, remaining, slots, timeline, blocks, lastEndByTask, weights, maxContinuousWork)

    blocks = coalesceContiguousBlocks(blocks, maxContinuousWork)
    unscheduled = diagnoseUnscheduled(tasks, blocks, slots, constraints)
    return AllocationResult(blocks=blocks, unscheduled=unscheduled)


def coalesceContiguousBlocks(
    blocks: list[AllocatedBlock],
    maxContinuousWork: Optional[int] = None
) -> list[AllocatedBlock]:
    """Merge adjacent same-task fragments into real time blocks (respect max continuous)."""
    if not blocks:
        return []

    ordered = sorted(blocks, key=lambda b: (b.task_id, b.start_time, b.end_time))
    merged: list[AllocatedBlock] = []

    for block in ordered:
        if not merged:
            merged.append(block)
            continue

        prev = merged[-1]
        sameTask = prev.task_id == block.task_id
        contiguous = prev.end_time == block.start_time
        combinedMinutes = prev.duration_minutes + block.duration_minutes
        withinCap = maxContinuousWork is None or combinedMinutes <= maxContinuousWork

        if sameTask and contiguous and withinCap:
            merged[-1] = AllocatedBlock(
                task_id=prev.task_id,
                task_name=prev.task_name,
                start_time=prev.start_time,
                end_time=block.end_time,
                duration_minutes=combinedMinutes
            )
        else:
            merged.append(block)

    return merged


def allocateSplittable(
    task: Task,
    remaining: int,
    slots: list[tuple[datetime, datetime]],
    timeline: BusyTimeline,
    blocks: list[AllocatedBlock],
    lastEndByTask: dict[int, datetime],
    weights,
    maxContinuousWork: Optional[int] = None
) -> None:
    """Allocate a splittable task by repeatedly choosing the best-scored chunk."""
    for _ in range(len(slots)):
        if remaining <= 0:
            break
        bestChoice: tuple[float, datetime, datetime, int] | None = None
        previousEnd = lastEndByTask.get(task.id)

        for (slotStart, slotEnd) in slots:
            if not isSlotAllowedForTask(task, slotStart, slotEnd):
                continue
            if timeline.overlaps(slotStart, slotEnd):
                continue

            slotMinutes = int((slotEnd - slotStart).total_seconds() / 60)
            allocMinutes = min(remaining, slotMinutes)
            if maxContinuousWork is not None and allocMinutes > maxContinuousWork:
                allocMinutes = maxContinuousWork
            if allocMinutes <= 0:
                continue

            blockEnd = slotStart + timedelta(minutes=allocMinutes)
            score = score_splittable_candidate(
                task=task,
                slot_start=slotStart,
                slot_end=blockEnd,
                allocated_minutes=allocMinutes,
                remaining_before_pick=remaining,
                previous_end_for_task=previousEnd,
                weights=weights
            )

            if bestChoice is None:
                bestChoice = (score, slotStart, blockEnd, allocMinutes)
                continue

            currentScore, currentStart, _, _ = bestChoice
            if score > currentScore or (score == currentScore and slotStart < currentStart):
                bestChoice = (score, slotStart, blockEnd, allocMinutes)

        if bestChoice is None:
            break

        _, bestStart, bestEnd, bestMinutes = bestChoice
        newBlock = AllocatedBlock(
            task_id=task.id,
            task_name=task.name,
            start_time=bestStart,
            end_time=bestEnd,
            duration_minutes=bestMinutes
        )
        blocks.append(newBlock)
        timeline.add(bestStart, bestEnd)
        lastEndByTask[task.id] = bestEnd
        remaining -= bestMinutes


def _findFixedCandidates(
    task: Task,
    requiredMinutes: int,
    slots: list[tuple[datetime, datetime]],
    timeline: BusyTimeline
) -> list[tuple[datetime, datetime]]:
    """Return all contiguous candidate ranges that can hold requiredMinutes."""
    candidates: list[tuple[datetime, datetime]] = []

    for startIndex in range(len(slots)):
        startSlot, firstEnd = slots[startIndex]
        if not isSlotAllowedForTask(task, startSlot, firstEnd):
            continue
        if timeline.overlaps(startSlot, firstEnd):
            continue

        contiguousMinutes = 0
        expectedNextStart = startSlot

        for cursor in range(startIndex, len(slots)):
            slotStart, slotEnd = slots[cursor]
            if slotStart != expectedNextStart:
                break
            if not isSlotAllowedForTask(task, slotStart, slotEnd):
                break
            if timeline.overlaps(slotStart, slotEnd):
                break

            slotMinutes = int((slotEnd - slotStart).total_seconds() / 60)
            contiguousMinutes += slotMinutes
            expectedNextStart = slotEnd

            if contiguousMinutes >= requiredMinutes:
                blockEnd = startSlot + timedelta(minutes=requiredMinutes)
                candidates.append((startSlot, blockEnd))
                break

    return candidates


def allocateFixed(
    task: Task,
    remaining: int,
    slots: list[tuple[datetime, datetime]],
    timeline: BusyTimeline,
    blocks: list[AllocatedBlock],
    lastEndByTask: dict[int, datetime],
    weights,
    maxContinuousWork: Optional[int] = None
) -> None:
    """Allocate a non-splittable task by choosing the best contiguous candidate."""
    allocMinutes = remaining
    if maxContinuousWork is not None and allocMinutes > maxContinuousWork:
        allocMinutes = maxContinuousWork
    if allocMinutes <= 0:
        return

    candidates = _findFixedCandidates(task, allocMinutes, slots, timeline)
    if not candidates:
        return

    bestRange: tuple[datetime, datetime] | None = None
    bestScore: float | None = None
    for candidateStart, candidateEnd in candidates:
        score = score_fixed_candidate(task, candidateStart, candidateEnd, weights=weights)
        if bestScore is None:
            bestScore = score
            bestRange = (candidateStart, candidateEnd)
            continue
        assert bestRange is not None
        currentStart, _ = bestRange
        if score > bestScore or (score == bestScore and candidateStart < currentStart):
            bestScore = score
            bestRange = (candidateStart, candidateEnd)

    if bestRange is None:
        return

    chosenStart, chosenEnd = bestRange
    newBlock = AllocatedBlock(
        task_id=task.id,
        task_name=task.name,
        start_time=chosenStart,
        end_time=chosenEnd,
        duration_minutes=allocMinutes
    )
    blocks.append(newBlock)
    timeline.add(chosenStart, chosenEnd)
    lastEndByTask[task.id] = chosenEnd
