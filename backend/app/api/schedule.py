from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from app.db import getSession
from app.schemas.schedule import ScheduleGenerateRequest, ScheduledBlockRead
from app.services.scheduler import SchedulingEngine
from app.services.export import ExportService


router = APIRouter(prefix="/api/schedule", tags=["schedule"])


@router.post("", response_model=list[ScheduledBlockRead])
def generateSchedule(request: ScheduleGenerateRequest, session: Session = Depends(getSession)) -> list[ScheduledBlockRead]:
    """Generate a conflict-free schedule for the given date range."""
    engine = SchedulingEngine(session)
    blocks = engine.generate(request.start_date, request.end_date)
    return blocks



@router.post("/export")
def exportSchedule(request: ScheduleGenerateRequest, session: Session = Depends(getSession)) -> StreamingResponse:
    """Generate schedule and return as downloadable .ics file."""
    engine = SchedulingEngine(session)
    blocks = engine.generate(request.start_date, request.end_date)
    icsContent = ExportService.toIcs(blocks)

    return StreamingResponse(
        iter([icsContent]),
        media_type="text/calendar",
        headers={
            "Content-Disposition": "attachment; filename=chronos_schedule.ics"
        },
    )
