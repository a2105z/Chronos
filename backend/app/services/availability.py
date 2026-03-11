"""Availability helpers - fetch windows, check if time is available."""

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlmodel import Session

from app.models.availability import AvailabilityWindow
from sqlmodel import select


def getAvailabilityWindows(session: "Session") -> list[AvailabilityWindow]:
    """Fetch all availability windows, ordered by day then start."""
    stmt = select(AvailabilityWindow)
    stmt = stmt.order_by(AvailabilityWindow.day_of_week, AvailabilityWindow.start_minutes)
    rows = session.exec(stmt).all()
    return list(rows)



def minutesToTime(minutes: int) -> tuple[int, int]:
    """Convert minutes-from-midnight to (hour, minute)."""
    hour = minutes // 60
    minute = minutes % 60
    return (hour, minute)



def isWithinWindow(dt: datetime, dayOfWeek: int, startMinutes: int, endMinutes: int) -> bool:
    """Check if dt falls inside the given window (same day, within range)."""
    if dt.weekday() != dayOfWeek:
        return False
    minutes = dt.hour * 60 + dt.minute
    if startMinutes <= minutes and minutes < endMinutes:
        return True
    return False



def isAvailable(dt: datetime, windows: list[AvailabilityWindow]) -> bool:
    """Check if dt falls inside any of the given availability windows."""
    for w in windows:
        if isWithinWindow(dt, w.day_of_week, w.start_minutes, w.end_minutes):
            return True
    return False
