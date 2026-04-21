"""Interval utilities for fast overlap checks during allocation."""

from __future__ import annotations

from bisect import bisect_left
from datetime import datetime


class BusyTimeline:
    """Track allocated ranges in sorted order for efficient overlap checks."""

    def __init__(self) -> None:
        self._ranges: list[tuple[datetime, datetime]] = []
        self._starts: list[datetime] = []

    def overlaps(self, start: datetime, end: datetime) -> bool:
        """Return True if [start, end) intersects any allocated range."""
        insert_at = bisect_left(self._starts, start)

        if insert_at > 0:
            previous_start, previous_end = self._ranges[insert_at - 1]
            if not (end <= previous_start or start >= previous_end):
                return True

        if insert_at < len(self._ranges):
            next_start, next_end = self._ranges[insert_at]
            if not (end <= next_start or start >= next_end):
                return True

        return False

    def add(self, start: datetime, end: datetime) -> None:
        """Insert a non-overlapping range while preserving sorted order."""
        insert_at = bisect_left(self._starts, start)
        self._starts.insert(insert_at, start)
        self._ranges.insert(insert_at, (start, end))

    def as_list(self) -> list[tuple[datetime, datetime]]:
        """Expose a copy for compatibility with existing call sites."""
        return list(self._ranges)
