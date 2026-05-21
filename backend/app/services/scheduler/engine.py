from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import select

from app.core.timeutil import asCstNaive, nowCst
from app.models.availability import AvailabilityWindow
from app.models.constraint import Constraint
from app.models.task import Task
from app.schemas.schedule import ScheduledBlockRead, ScheduleGenerateResponse, UnscheduledDiagnostic
from app.services.availability import ensureDefaultAvailability, getAvailabilityWindows
from app.services.schedule_persistence import listBlocksInRange, replaceBlocksForRange
from app.services.scheduler.allocator import (
    REASON_NO_AVAILABILITY,
    AllocationResult,
    UnscheduledInfo,
    allocateTasks,
)
from app.services.scheduler.slots import buildAvailableSlots

if TYPE_CHECKING:
    from sqlmodel import Session


def _toDiagnostics(items: list[UnscheduledInfo]) -> list[UnscheduledDiagnostic]:
    return [
        UnscheduledDiagnostic(
            task_id=i.task_id,
            task_name=i.task_name,
            reason=i.reason,
            detail=i.detail
        )
        for i in items
    ]


def _summary(blocks: list[ScheduledBlockRead], unscheduled: list[UnscheduledDiagnostic], extra: str = "") -> str:
    placed = len(blocks)
    missed = len(unscheduled)
    base: str
    if missed == 0:
        base = f"Scheduled {placed} block(s). All tasks placed."
    else:
        reasons = sorted({u.reason for u in unscheduled})
        base = f"Scheduled {placed} block(s); {missed} task(s) incomplete ({', '.join(reasons)})."
    if extra:
        return f"{extra} {base}"
    return base


class SchedulingEngine:
    """Generates conflict-free schedules using greedy allocation."""

    def __init__(self, session: "Session", userId: Optional[int] = None) -> None:
        self.session = session
        self.userId = userId

    def generate(
        self,
        startDate: datetime,
        endDate: datetime,
        replaceExisting: bool = True
    ) -> ScheduleGenerateResponse:
        """Generate schedule for date range. No overlaps, within availability."""
        startDate = asCstNaive(startDate)
        endDate = asCstNaive(endDate)
        now = nowCst()
        if startDate < now:
            startDate = now
        if endDate <= startDate:
            return ScheduleGenerateResponse(
                blocks=[],
                unscheduled=[],
                summary="That range is in the past — try a time in the future (CST)."
            )

        if not replaceExisting:
            existing = listBlocksInRange(self.session, startDate, endDate, userId=self.userId)
            return ScheduleGenerateResponse(
                blocks=existing,
                unscheduled=[],
                summary=f"replace_existing=false; returned {len(existing)} existing block(s) without regenerating."
            )

        allTasks = self.fetchTasks()
        tasks = [t for t in allTasks if t.id is not None]
        if not tasks:
            blocks = replaceBlocksForRange(self.session, startDate, endDate, [], userId=self.userId)
            return ScheduleGenerateResponse(blocks=blocks, unscheduled=[], summary="No tasks to schedule.")

        defaultNote = ""
        windows = getAvailabilityWindows(self.session, userId=self.userId)
        if not windows and self.userId is not None:
            ensureDefaultAvailability(self.session, self.userId)
            windows = getAvailabilityWindows(self.session, userId=self.userId)
            defaultNote = "Assumed weekdays 8am–10pm (no availability configured)."

        if not windows:
            diagnostics = [
                UnscheduledDiagnostic(
                    task_id=t.id,
                    task_name=t.name,
                    reason=REASON_NO_AVAILABILITY,
                    detail="No availability windows configured; refusing full-day fallback for generate."
                )
                for t in tasks
                if t.id is not None
            ]
            blocks = replaceBlocksForRange(self.session, startDate, endDate, [], userId=self.userId)
            return ScheduleGenerateResponse(
                blocks=blocks,
                unscheduled=diagnostics,
                summary=_summary(blocks, diagnostics)
            )

        constraints = self.fetchConstraints()
        slots = buildAvailableSlots(startDate, endDate, windows, constraints)
        if not slots:
            diagnostics = [
                UnscheduledDiagnostic(
                    task_id=t.id,
                    task_name=t.name,
                    reason=REASON_NO_AVAILABILITY,
                    detail="Availability windows exist but no free slots in this range."
                )
                for t in tasks
                if t.id is not None
            ]
            blocks = replaceBlocksForRange(self.session, startDate, endDate, [], userId=self.userId)
            return ScheduleGenerateResponse(
                blocks=blocks,
                unscheduled=diagnostics,
                summary=_summary(blocks, diagnostics, defaultNote)
            )

        result: AllocationResult = allocateTasks(tasks, slots, constraints)
        blocks = replaceBlocksForRange(
            self.session,
            startDate,
            endDate,
            result.blocks,
            userId=self.userId
        )
        unscheduled = _toDiagnostics(result.unscheduled)
        return ScheduleGenerateResponse(
            blocks=blocks,
            unscheduled=unscheduled,
            summary=_summary(blocks, unscheduled, defaultNote)
        )

    def explain(self, startDate: datetime, endDate: datetime) -> ScheduleGenerateResponse:
        """Recompute diagnostics for current tasks vs existing schedule without wiping."""
        existing = listBlocksInRange(self.session, startDate, endDate, userId=self.userId)
        tasks = [t for t in self.fetchTasks() if t.id is not None]
        windows = getAvailabilityWindows(self.session, userId=self.userId)
        if not windows and self.userId is not None:
            ensureDefaultAvailability(self.session, self.userId)
            windows = getAvailabilityWindows(self.session, userId=self.userId)
        constraints = self.fetchConstraints()

        if not windows:
            diagnostics = [
                UnscheduledDiagnostic(
                    task_id=t.id,
                    task_name=t.name,
                    reason=REASON_NO_AVAILABILITY,
                    detail="No availability windows configured."
                )
                for t in tasks
                if t.id is not None
            ]
            return ScheduleGenerateResponse(
                blocks=existing,
                unscheduled=diagnostics,
                summary=_summary(existing, diagnostics)
            )

        slots = buildAvailableSlots(startDate, endDate, windows, constraints)

        from app.services.scheduler.allocator import AllocatedBlock, diagnoseUnscheduled

        allocated = [
            AllocatedBlock(
                task_id=b.task_id,
                task_name=b.task_name,
                start_time=b.start_time,
                end_time=b.end_time,
                duration_minutes=b.duration_minutes
            )
            for b in existing
        ]
        infos = diagnoseUnscheduled(tasks, allocated, slots, constraints)
        unscheduled = _toDiagnostics(infos)
        return ScheduleGenerateResponse(
            blocks=existing,
            unscheduled=unscheduled,
            summary=_summary(existing, unscheduled)
        )

    def getFullDayAvailabilityWindows(self) -> list[AvailabilityWindow]:
        """Fallback to full-day weekly availability for move validation only."""
        windows: list[AvailabilityWindow] = []
        for day in range(7):
            windows.append(
                AvailabilityWindow(
                    day_of_week=day,
                    start_minutes=0,
                    end_minutes=1440,
                    user_id=self.userId
                )
            )
        return windows

    def fetchTasks(self) -> list[Task]:
        """Fetch user tasks ordered for scheduling."""
        stmt = select(Task).order_by(Task.created_at.asc())
        if self.userId is not None:
            stmt = stmt.where(Task.user_id == self.userId)
        return list(self.session.exec(stmt).all())

    def fetchConstraints(self) -> list[Constraint]:
        """Fetch user constraints."""
        stmt = select(Constraint)
        if self.userId is not None:
            stmt = stmt.where(Constraint.user_id == self.userId)
        return list(self.session.exec(stmt).all())
