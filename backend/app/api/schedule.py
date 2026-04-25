from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from app.db import getSession
from app.models.schedule import ScheduledBlock
from app.schemas.schedule import ScheduleGenerateRequest, ScheduledBlockMove, ScheduledBlockRead
from app.services.export import ExportService
from app.services.schedule_persistence import listBlocksInRange, scheduledBlockToRead
from app.services.schedule_validation import computeEndFromStart, validateMovedBlock
from app.services.scheduler.engine import SchedulingEngine

router = APIRouter(prefix="/api/schedule", tags=["schedule"])


@router.get("", response_model=list[ScheduledBlockRead])
def listSchedule(
    start_date: datetime = Query(..., description="Range start (inclusive)"),
    end_date: datetime = Query(..., description="Range end (exclusive or overlap query)"),
    session: Session = Depends(getSession)
) -> list[ScheduledBlockRead]:
    """Return persisted schedule blocks overlapping the given range without regenerating."""
    return listBlocksInRange(session, start_date, end_date)


@router.post("", response_model=list[ScheduledBlockRead])
def generateSchedule(request: ScheduleGenerateRequest, session: Session = Depends(getSession)) -> list[ScheduledBlockRead]:
    """Generate a conflict-free schedule for the given date range and persist it."""
    engine = SchedulingEngine(session)
    return engine.generate(request.start_date, request.end_date)


@router.patch("/blocks/{block_id}", response_model=ScheduledBlockRead)
def moveScheduledBlock(
    block_id: int,
    body: ScheduledBlockMove,
    session: Session = Depends(getSession)
) -> ScheduledBlockRead:
    """Move a block to a new start time; duration is preserved. Validates hard constraints."""
    block = session.get(ScheduledBlock, block_id)
    if not block:
        raise HTTPException(status_code=404, detail="Scheduled block not found")

    engine = SchedulingEngine(session)
    fallback = engine.getFullDayAvailabilityWindows()
    newEnd = computeEndFromStart(body.start_time, block.duration_minutes)

    try:
        validateMovedBlock(session, block_id, body.start_time, newEnd, fallback)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    block.start_time = body.start_time
    block.end_time = newEnd
    session.add(block)
    session.commit()
    session.refresh(block)
    return scheduledBlockToRead(session, block)


@router.delete("/blocks/{block_id}", status_code=204)
def deleteScheduledBlock(block_id: int, session: Session = Depends(getSession)) -> None:
    """Delete a single scheduled block."""
    block = session.get(ScheduledBlock, block_id)
    if not block:
        raise HTTPException(status_code=404, detail="Scheduled block not found")
    session.delete(block)
    session.commit()


@router.post("/export")
def exportSchedule(request: ScheduleGenerateRequest, session: Session = Depends(getSession)) -> StreamingResponse:
    """Export persisted blocks in the date range as a downloadable .ics file."""
    blocks = listBlocksInRange(session, request.start_date, request.end_date)
    icsContent = ExportService.toIcs(blocks)

    return StreamingResponse(
        iter([icsContent]),
        media_type="text/calendar",
        headers={
            "Content-Disposition": "attachment; filename=chronos_schedule.ics"
        }
    )
