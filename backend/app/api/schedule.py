import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.core.deps import CurrentUser, DbSession
from app.models.schedule import ScheduledBlock
from app.models.task import Task
from app.schemas.schedule import (
    ScheduledBlockCreate,
    ScheduledBlockMove,
    ScheduledBlockRead,
    ScheduleGenerateRequest,
    ScheduleGenerateResponse,
)
from app.services.export import ExportService
from app.services.schedule_persistence import listBlocksInRange, scheduledBlockToRead
from app.services.schedule_validation import (
    asNaiveLocal,
    computeEndFromStart,
    validateMovedBlock,
    validateNewBlock,
)
from app.services.scheduler.engine import SchedulingEngine

router = APIRouter(prefix="/api/schedule", tags=["schedule"])


@router.get("", response_model=list[ScheduledBlockRead])
def listSchedule(
    user: CurrentUser,
    session: DbSession,
    start_date: datetime = Query(..., description="Range start (inclusive)"),
    end_date: datetime = Query(..., description="Range end (exclusive or overlap query)")
) -> list[ScheduledBlockRead]:
    """Return persisted schedule blocks overlapping the given range without regenerating."""
    return listBlocksInRange(session, start_date, end_date, userId=user.id)


@router.post("", response_model=ScheduleGenerateResponse)
def generateSchedule(
    request: ScheduleGenerateRequest,
    user: CurrentUser,
    session: DbSession
) -> ScheduleGenerateResponse:
    """Generate a conflict-free schedule for the given date range and persist it."""
    engine = SchedulingEngine(session, userId=user.id)
    return engine.generate(request.start_date, request.end_date, replaceExisting=request.replace_existing)


@router.post("/blocks", response_model=ScheduledBlockRead, status_code=201)
def createScheduledBlock(
    body: ScheduledBlockCreate,
    user: CurrentUser,
    session: DbSession
) -> ScheduledBlockRead:
    """Create a task + block from a calendar drag/select (Google Calendar-style)."""
    if body.end_time <= body.start_time:
        raise HTTPException(status_code=422, detail="End must be after start")

    start = asNaiveLocal(body.start_time)
    end = asNaiveLocal(body.end_time)
    duration = int((end - start).total_seconds() / 60)
    if duration < 15:
        raise HTTPException(status_code=422, detail="Blocks must be at least 15 minutes")

    engine = SchedulingEngine(session, userId=user.id)
    fallback = engine.getFullDayAvailabilityWindows()
    try:
        validateNewBlock(session, user.id, start, end, fallback)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    task = Task(
        user_id=user.id,
        name=body.title.strip(),
        estimated_duration_minutes=duration,
        priority=5,
        splittable=False
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    block = ScheduledBlock(
        user_id=user.id,
        task_id=task.id,
        start_time=start,
        end_time=end,
        duration_minutes=duration,
        schedule_run_id=str(uuid.uuid4())
    )
    session.add(block)
    session.commit()
    session.refresh(block)
    return scheduledBlockToRead(session, block)


@router.patch("/blocks/{block_id}", response_model=ScheduledBlockRead)
def moveScheduledBlock(
    block_id: int,
    body: ScheduledBlockMove,
    user: CurrentUser,
    session: DbSession
) -> ScheduledBlockRead:
    """Move and/or resize a block. Validates hard constraints."""
    block = session.get(ScheduledBlock, block_id)
    if not block or block.user_id != user.id:
        raise HTTPException(status_code=404, detail="Scheduled block not found")

    if body.end_time is not None:
        newEnd = asNaiveLocal(body.end_time)
        allowResize = True
    elif body.duration_minutes is not None:
        newEnd = computeEndFromStart(body.start_time, body.duration_minutes)
        allowResize = True
    else:
        newEnd = computeEndFromStart(body.start_time, block.duration_minutes)
        allowResize = False

    newStart = asNaiveLocal(body.start_time)
    if newEnd <= newStart:
        raise HTTPException(status_code=422, detail="End must be after start")

    engine = SchedulingEngine(session, userId=user.id)
    fallback = engine.getFullDayAvailabilityWindows()

    try:
        validateMovedBlock(
            session,
            block_id,
            newStart,
            newEnd,
            fallback,
            allowDurationChange=allowResize
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    duration = int((newEnd - newStart).total_seconds() / 60)
    block.start_time = newStart
    block.end_time = newEnd
    block.duration_minutes = duration

    task = session.get(Task, block.task_id)
    if task is not None and allowResize:
        task.estimated_duration_minutes = duration
        task.updated_at = datetime.utcnow()
        session.add(task)

    session.add(block)
    session.commit()
    session.refresh(block)
    return scheduledBlockToRead(session, block)


@router.delete("/blocks/{block_id}", status_code=204)
def deleteScheduledBlock(block_id: int, user: CurrentUser, session: DbSession) -> None:
    """Delete a single scheduled block."""
    block = session.get(ScheduledBlock, block_id)
    if not block or block.user_id != user.id:
        raise HTTPException(status_code=404, detail="Scheduled block not found")
    session.delete(block)
    session.commit()


@router.post("/export")
def exportSchedule(
    request: ScheduleGenerateRequest,
    user: CurrentUser,
    session: DbSession
) -> StreamingResponse:
    """Export persisted blocks in the date range as a downloadable .ics file."""
    blocks = listBlocksInRange(session, request.start_date, request.end_date, userId=user.id)
    icsContent = ExportService.toIcs(blocks)

    return StreamingResponse(
        iter([icsContent]),
        media_type="text/calendar",
        headers={"Content-Disposition": "attachment; filename=chronos_schedule.ics"}
    )
