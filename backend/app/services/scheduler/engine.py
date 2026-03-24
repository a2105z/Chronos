"""Scheduling engine - generates conflict-free time blocks."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import select

from app.models.constraint import Constraint
from app.models.task import Task
from app.schemas.schedule import ScheduledBlockRead
from app.services.availability import getAvailabilityWindows
from app.services.scheduler.allocator import AllocatedBlock, allocateTasks
from app.services.scheduler.slots import buildAvailableSlots

if TYPE_CHECKING:
    from sqlmodel import Session


class SchedulingEngine:
    """Generates conflict-free schedules using greedy allocation."""

    def __init__(self, session: "Session") -> None:
        self.session = session



    def generate(self, startDate: datetime, endDate: datetime) -> list[ScheduledBlockRead]:
        """Generate schedule for date range. No overlaps, within availability."""
        allTasks = self.fetchTasks()
        tasks = []
        for t in allTasks:
            if t.id is not None:
                tasks.append(t)
        if not tasks:
            return []

        windows = getAvailabilityWindows(self.session)
        if not windows:
            return []

        constraints = self.fetchConstraints()
        slots = buildAvailableSlots(startDate, endDate, windows, constraints)
        if not slots:
            return []

        allocated = allocateTasks(tasks, slots, constraints)
        return self.toScheduledBlockReads(allocated)



    def fetchTasks(self) -> list[Task]:
        """Fetch all tasks ordered for scheduling."""
        stmt = select(Task).order_by(Task.created_at.asc())
        return list(self.session.exec(stmt).all())



    def fetchConstraints(self) -> list[Constraint]:
        """Fetch all constraints."""
        stmt = select(Constraint)
        return list(self.session.exec(stmt).all())



    def toScheduledBlockReads(self, blocks: list[AllocatedBlock]) -> list[ScheduledBlockRead]:
        """Convert allocated blocks to API response format."""
        result = []
        for i, b in enumerate(blocks):
            blockRead = ScheduledBlockRead(
                id=i + 1,
                task_id=b.task_id,
                task_name=b.task_name,
                start_time=b.start_time,
                end_time=b.end_time,
                duration_minutes=b.duration_minutes,
            )
            result.append(blockRead)
        return result
