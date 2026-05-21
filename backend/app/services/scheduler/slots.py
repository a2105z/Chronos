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
    totalDays = (end - current).days + 1

    for dayOffset in range(totalDays):
        currentDay = current + timedelta(days=dayOffset)
        if currentDay >= end:
            break
        dayOfWeek = currentDay.weekday()
        windowsForDay = []
        for w in availabilityWindows:
            if w.day_of_week == dayOfWeek:
                windowsForDay.append(w)

        for window in windowsForDay:
            dayStart = currentDay.replace(hour=0, minute=0, second=0, microsecond=0)
            slotStart = dayStart + timedelta(minutes=window.start_minutes)
            slotEnd = dayStart + timedelta(minutes=window.end_minutes)

            totalWindowMinutes = int((slotEnd - slotStart).total_seconds() / 60)
            slotCount = (totalWindowMinutes + SLOT_SIZE_MINUTES - 1) // SLOT_SIZE_MINUTES
            for slotIndex in range(slotCount):
                slotBegin = slotStart + timedelta(minutes=SLOT_SIZE_MINUTES * slotIndex)
                slotFinish = slotBegin + timedelta(minutes=SLOT_SIZE_MINUTES)
                if slotFinish > slotEnd:
                    break
                if slotBegin >= end:
                    break
                if slotFinish <= startDate:
                    continue

                clippedStart = slotBegin
                clippedEnd = slotFinish
                if clippedStart < startDate:
                    clippedStart = startDate
                if clippedEnd > end:
                    clippedEnd = end
                if clippedStart >= clippedEnd:
                    continue

                if not isSlotBlocked(clippedStart, clippedEnd, protected):
                    slots.append((clippedStart, clippedEnd))

    return slots
