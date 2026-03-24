"""Time slot discretization - converts availability into 15-minute slots."""

from datetime import datetime, timedelta

from app.models.availability import AvailabilityWindow
from app.models.constraint import Constraint


SLOT_SIZE_MINUTES = 15


def slotOverlapsProtected(slotStart: datetime, slotEnd: datetime, constraint: Constraint) -> bool:
    """Return True if the slot overlaps this protected block."""
    if constraint.constraint_type != "protected_block":
        return False
    if (
        constraint.day_of_week is None
        or constraint.start_minutes is None
        or constraint.end_minutes is None
    ):
        return False
    if slotStart.weekday() != constraint.day_of_week:
        return False
    slotStartMins = slotStart.hour * 60 + slotStart.minute
    slotEndMins = slotEnd.hour * 60 + slotEnd.minute
    if slotEndMins <= constraint.start_minutes:
        return False
    if slotStartMins >= constraint.end_minutes:
        return False
    return True



def isSlotBlocked(slotStart: datetime, slotEnd: datetime, protectedConstraints: list[Constraint]) -> bool:
    """Return True if the slot falls inside any protected block."""
    for c in protectedConstraints:
        if slotOverlapsProtected(slotStart, slotEnd, c):
            return True
    return False



def buildAvailableSlots(startDate: datetime, endDate: datetime, availabilityWindows: list[AvailabilityWindow], constraints: list[Constraint]) -> list[tuple[datetime, datetime]]:
    """Build list of available (start, end) slot tuples. 15-min slots. Excludes protected blocks."""
    protected = []
    for c in constraints:
        if c.constraint_type == "protected_block":
            protected.append(c)
    slots: list[tuple[datetime, datetime]] = []

    current = startDate.replace(hour=0, minute=0, second=0, microsecond=0)
    end = endDate

    while current < end:
        dayOfWeek = current.weekday()
        windowsForDay = []
        for w in availabilityWindows:
            if w.day_of_week == dayOfWeek:
                windowsForDay.append(w)

        for window in windowsForDay:
            dayStart = current.replace(hour=0, minute=0, second=0, microsecond=0)
            slotStart = dayStart + timedelta(minutes=window.start_minutes)
            slotEnd = dayStart + timedelta(minutes=window.end_minutes)

            slotBegin = slotStart
            while slotBegin < slotEnd:
                slotFinish = slotBegin + timedelta(minutes=SLOT_SIZE_MINUTES)
                if slotFinish > slotEnd:
                    break
                if slotBegin >= end:
                    break
                if slotFinish <= startDate:
                    slotBegin = slotFinish
                    continue

                clippedStart = slotBegin
                clippedEnd = slotFinish
                if clippedStart < startDate:
                    clippedStart = startDate
                if clippedEnd > end:
                    clippedEnd = end
                if clippedStart >= clippedEnd:
                    slotBegin = slotFinish
                    continue

                if not isSlotBlocked(clippedStart, clippedEnd, protected):
                    slots.append((clippedStart, clippedEnd))

                slotBegin = slotFinish

        current += timedelta(days=1)

    return slots
