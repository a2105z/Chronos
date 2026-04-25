from __future__ import annotations

import uuid
from datetime import datetime

from sqlmodel import Session, select

from app.models.schedule import ScheduledBlock
from app.models.task import Task
from app.schemas.schedule import ScheduledBlockRead
from app.services.scheduler.allocator import AllocatedBlock


def deleteBlocksIntersectingRange(session: Session, rangeStart: datetime, rangeEnd: datetime) -> None:
    """Remove persisted blocks that overlap [rangeStart, rangeEnd)."""
    stmt = select(ScheduledBlock).where(ScheduledBlock.start_time < rangeEnd, ScheduledBlock.end_time > rangeStart)
    for block in session.exec(stmt).all():
        session.delete(block)


def insertAllocatedBlocks(session: Session, allocated: list[AllocatedBlock], runId: str) -> None:
    """Insert new rows for a scheduling run."""
    for b in allocated:
        row = ScheduledBlock(task_id=b.task_id, start_time=b.start_time, end_time=b.end_time, duration_minutes=b.duration_minutes, schedule_run_id=runId)
        session.add(row)


def scheduledBlockToRead(session: Session, block: ScheduledBlock) -> ScheduledBlockRead:
    task = session.get(Task, block.task_id)
    taskName = "Unknown task"
    if task is not None:
        taskName = task.name
    if block.id is None:
        raise ValueError("Scheduled block must have an id")
    return ScheduledBlockRead(id=block.id, task_id=block.task_id, task_name=taskName, start_time=block.start_time, end_time=block.end_time, duration_minutes=block.duration_minutes)


def listBlocksInRange(session: Session, rangeStart: datetime, rangeEnd: datetime) -> list[ScheduledBlockRead]:
    """Return blocks overlapping the given range, ordered by start time."""
    stmt = (
        select(ScheduledBlock)
        .where(ScheduledBlock.start_time < rangeEnd)
        .where(ScheduledBlock.end_time > rangeStart)
        .order_by(ScheduledBlock.start_time)
    )
    rows = list(session.exec(stmt).all())
    result: list[ScheduledBlockRead] = []
    for row in rows:
        result.append(scheduledBlockToRead(session, row))
    return result


def deleteBlocksForTask(session: Session, taskId: int) -> None:
    """Remove all scheduled blocks for a task (e.g. before task delete)."""
    stmt = select(ScheduledBlock).where(ScheduledBlock.task_id == taskId)
    for block in session.exec(stmt).all():
        session.delete(block)


def replaceBlocksForRange(
    session: Session,
    rangeStart: datetime,
    rangeEnd: datetime,
    allocated: list[AllocatedBlock]
) -> list[ScheduledBlockRead]:
    """Replace overlapping persisted blocks with a new allocation."""
    deleteBlocksIntersectingRange(session, rangeStart, rangeEnd)
    session.flush()
    runId = str(uuid.uuid4())
    insertAllocatedBlocks(session, allocated, runId)
    session.commit()
    return listBlocksInRange(session, rangeStart, rangeEnd)
