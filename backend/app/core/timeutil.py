"""Chronos operates on America/Chicago (CST/CDT) wall-clock time."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

CHRONOS_TZ = ZoneInfo("America/Chicago")
PAST_TIME_MESSAGE = "That time has already passed — try a time in the future (CST)."


def nowCst() -> datetime:
    """Current time in America/Chicago as naive wall-clock datetime."""
    return datetime.now(CHRONOS_TZ).replace(tzinfo=None, microsecond=0)


def asCstNaive(dt: datetime) -> datetime:
    """
    Normalize datetimes to naive America/Chicago wall-clock.

    - Aware values are converted into Chicago.
    - Naive values are treated as already Chicago local (calendar UI contract).
    """
    if dt.tzinfo is not None:
        return dt.astimezone(CHRONOS_TZ).replace(tzinfo=None, microsecond=0)
    return dt.replace(microsecond=0)


def assertNotInPast(start: datetime) -> None:
    """Reject placements that start before now in CST."""
    startCst = asCstNaive(start)
    if startCst < nowCst():
        raise ValueError(PAST_TIME_MESSAGE)
