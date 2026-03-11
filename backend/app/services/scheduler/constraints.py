"""Hard constraint extraction and invariant validation for scheduling."""

from datetime import datetime
from typing import Optional

from app.models.constraint import Constraint


def getMaxContinuousWorkMinutes(constraints: list[Constraint]) -> Optional[int]:
    """Return the max continuous work limit in minutes, or None if not set.
    If multiple max_continuous_work constraints exist, returns the smallest (strictest).
    """
    values = []
    for c in constraints:
        if c.constraint_type == "max_continuous_work" and c.value is not None and c.value >= 1:
            values.append(c.value)
    if not values:
        return None
    return min(values)



def blockOverlapsProtected(blockStart: datetime, blockEnd: datetime, constraint: Constraint) -> bool:
    """Return True if block overlaps this protected block."""
    if constraint.constraint_type != "protected_block":
        return False
    if (
        constraint.day_of_week is None
        or constraint.start_minutes is None
        or constraint.end_minutes is None
    ):
        return False
    if blockStart.weekday() != constraint.day_of_week:
        return False
    blockStartMins = blockStart.hour * 60 + blockStart.minute
    blockEndMins = blockEnd.hour * 60 + blockEnd.minute
    if blockEndMins <= constraint.start_minutes:
        return False
    if blockStartMins >= constraint.end_minutes:
        return False
    return True



def blockWithinAvailability(blockStart: datetime, blockEnd: datetime, dayOfWeek: int, startMinutes: int, endMinutes: int) -> bool:
    """Return True if block is fully within the given availability window."""
    if blockStart.weekday() != dayOfWeek or blockEnd.weekday() != dayOfWeek:
        return False
    blockStartMins = blockStart.hour * 60 + blockStart.minute
    blockEndMins = blockEnd.hour * 60 + blockEnd.minute
    if blockStartMins < startMinutes:
        return False
    if blockEndMins > endMinutes:
        return False
    return True



def validateNoOverlap(blocks: list[dict]) -> None:
    """Assert no two blocks overlap. Raises AssertionError if overlap found.
    Each block must have start_time and end_time (datetime or ISO string).
    """
    for i, b1 in enumerate(blocks):
        start1 = b1.get("start_time")
        end1 = b1.get("end_time")
        if isinstance(start1, str):
            start1 = datetime.fromisoformat(start1.replace("Z", "+00:00"))
        if isinstance(end1, str):
            end1 = datetime.fromisoformat(end1.replace("Z", "+00:00"))
        for b2 in blocks[i + 1:]:
            start2 = b2.get("start_time")
            end2 = b2.get("end_time")
            if isinstance(start2, str):
                start2 = datetime.fromisoformat(start2.replace("Z", "+00:00"))
            if isinstance(end2, str):
                end2 = datetime.fromisoformat(end2.replace("Z", "+00:00"))
            overlaps = end1 > start2 and end2 > start1
            if overlaps:
                raise AssertionError(f"Blocks overlap: {start1}-{end1} vs {start2}-{end2}")



def validateWithinAvailability(blocks: list[dict], windows: list[dict]) -> None:
    """Assert every block falls fully within at least one availability window.
    Windows: list of {day_of_week, start_minutes, end_minutes}.
    """
    for b in blocks:
        start = b.get("start_time")
        end = b.get("end_time")
        if isinstance(start, str):
            start = datetime.fromisoformat(start.replace("Z", "+00:00"))
        if isinstance(end, str):
            end = datetime.fromisoformat(end.replace("Z", "+00:00"))
        found = False
        for w in windows:
            if blockWithinAvailability(start, end, w["day_of_week"], w["start_minutes"], w["end_minutes"]):
                found = True
                break
        if not found:
            raise AssertionError(f"Block {start}-{end} not within any availability window")



def validateNoProtectedOverlap(blocks: list[dict], protectedConstraints: list[dict]) -> None:
    """Assert no block overlaps any protected block.
    protectedConstraints: list of {constraint_type, day_of_week, start_minutes, end_minutes}.
    """
    for b in blocks:
        start = b.get("start_time")
        end = b.get("end_time")
        if isinstance(start, str):
            start = datetime.fromisoformat(start.replace("Z", "+00:00"))
        if isinstance(end, str):
            end = datetime.fromisoformat(end.replace("Z", "+00:00"))
        for pc in protectedConstraints:
            if pc.get("constraint_type") != "protected_block":
                continue
            c = Constraint(
                constraint_type="protected_block",
                day_of_week=pc.get("day_of_week"),
                start_minutes=pc.get("start_minutes"),
                end_minutes=pc.get("end_minutes"),
            )
            if blockOverlapsProtected(start, end, c):
                raise AssertionError(f"Block {start}-{end} overlaps protected {pc}")



def validateMaxContinuousWork(blocks: list[dict], maxMinutes: int) -> None:
    """Assert no single block exceeds maxMinutes duration."""
    for b in blocks:
        duration = b.get("duration_minutes")
        if duration is None:
            start = b.get("start_time")
            end = b.get("end_time")
            if isinstance(start, str):
                start = datetime.fromisoformat(start.replace("Z", "+00:00"))
            if isinstance(end, str):
                end = datetime.fromisoformat(end.replace("Z", "+00:00"))
            duration = int((end - start).total_seconds() / 60)
        if duration > maxMinutes:
            raise AssertionError(f"Block exceeds max_continuous_work ({maxMinutes} min): duration={duration}")
