from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from sqlmodel import Session

from sqlmodel import select

from app.models.availability import AvailabilityWindow

DEFAULT_AVAIL_START = 8 * 60
DEFAULT_AVAIL_END = 22 * 60


def getAvailabilityWindows(session: "Session", userId: Optional[int] = None) -> list[AvailabilityWindow]:
    """Fetch availability windows, ordered by day then start."""
    stmt = select(AvailabilityWindow)
    if userId is not None:
        stmt = stmt.where(AvailabilityWindow.user_id == userId)
    stmt = stmt.order_by(AvailabilityWindow.day_of_week, AvailabilityWindow.start_minutes)
    rows = session.exec(stmt).all()
    return list(rows)


def ensureDefaultAvailability(session: "Session", userId: int) -> list[AvailabilityWindow]:
    """If the user has no windows, assume weekdays 8am–10pm so planning can proceed."""
    existing = getAvailabilityWindows(session, userId=userId)
    if existing:
        return []

    created: list[AvailabilityWindow] = []
    for day in range(5):
        window = AvailabilityWindow(
            user_id=userId,
            day_of_week=day,
            start_minutes=DEFAULT_AVAIL_START,
            end_minutes=DEFAULT_AVAIL_END
        )
        session.add(window)
        created.append(window)
    session.commit()
    for w in created:
        session.refresh(w)
    return created


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
