from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import getSession
from app.utils import applyPartialUpdate
from app.models.availability import AvailabilityWindow
from app.schemas.availability import (
    AvailabilityCreate,
    AvailabilityRead,
    AvailabilityUpdate,
)


router = APIRouter(prefix="/api/availability", tags=["availability"])


@router.get("", response_model=list[AvailabilityRead])
def listAvailability(session: Session = Depends(getSession)) -> list[AvailabilityWindow]:
    """List all availability windows, ordered by day then start time."""
    stmt = select(AvailabilityWindow)
    stmt = stmt.order_by(AvailabilityWindow.day_of_week, AvailabilityWindow.start_minutes)
    rows = session.exec(stmt).all()
    return list(rows)



@router.post("", response_model=AvailabilityRead, status_code=201)
def createAvailability(availIn: AvailabilityCreate, session: Session = Depends(getSession)) -> AvailabilityWindow:
    """Add a new availability window (e.g. Mon 9am–5pm)."""
    window = AvailabilityWindow(**availIn.model_dump())
    session.add(window)
    session.commit()
    session.refresh(window)
    return window



@router.get("/{window_id}", response_model=AvailabilityRead)
def getAvailability(window_id: int, session: Session = Depends(getSession)) -> AvailabilityWindow:
    """Get a single availability window."""
    window = session.get(AvailabilityWindow, window_id)
    if not window:
        raise HTTPException(status_code=404, detail="Availability window not found")
    return window



@router.put("/{window_id}", response_model=AvailabilityRead)
def updateAvailability(window_id: int, availIn: AvailabilityUpdate, session: Session = Depends(getSession)) -> AvailabilityWindow:
    """Update an availability window. Start must stay before end."""
    window = session.get(AvailabilityWindow, window_id)
    if not window:
        raise HTTPException(status_code=404, detail="Availability window not found")

    applyPartialUpdate(window, availIn.model_dump(exclude_unset=True))

    if window.start_minutes >= window.end_minutes:
        raise HTTPException(
            status_code=422,
            detail="start_minutes must be less than end_minutes",
        )

    session.add(window)
    session.commit()
    session.refresh(window)
    return window



@router.delete("/{window_id}", status_code=204)
def deleteAvailability(window_id: int, session: Session = Depends(getSession)) -> None:
    """Remove an availability window."""
    window = session.get(AvailabilityWindow, window_id)
    if not window:
        raise HTTPException(status_code=404, detail="Availability window not found")
    session.delete(window)
    session.commit()
