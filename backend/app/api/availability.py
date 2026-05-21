from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.core.deps import CurrentUser, DbSession
from app.models.availability import AvailabilityWindow
from app.schemas.availability import AvailabilityCreate, AvailabilityRead, AvailabilityUpdate
from app.utils import applyPartialUpdate

router = APIRouter(prefix="/api/availability", tags=["availability"])


def _ownedOr404(session: DbSession, windowId: int, userId: int) -> AvailabilityWindow:
    window = session.get(AvailabilityWindow, windowId)
    if not window or window.user_id != userId:
        raise HTTPException(status_code=404, detail="Availability window not found")
    return window


@router.get("", response_model=list[AvailabilityRead])
def listAvailability(user: CurrentUser, session: DbSession) -> list[AvailabilityWindow]:
    stmt = (
        select(AvailabilityWindow)
        .where(AvailabilityWindow.user_id == user.id)
        .order_by(AvailabilityWindow.day_of_week, AvailabilityWindow.start_minutes)
    )
    return list(session.exec(stmt).all())


@router.post("", response_model=AvailabilityRead, status_code=201)
def createAvailability(
    availIn: AvailabilityCreate,
    user: CurrentUser,
    session: DbSession
) -> AvailabilityWindow:
    window = AvailabilityWindow(**availIn.model_dump(), user_id=user.id)
    session.add(window)
    session.commit()
    session.refresh(window)
    return window


@router.get("/{window_id}", response_model=AvailabilityRead)
def getAvailability(window_id: int, user: CurrentUser, session: DbSession) -> AvailabilityWindow:
    return _ownedOr404(session, window_id, user.id)


@router.put("/{window_id}", response_model=AvailabilityRead)
def updateAvailability(
    window_id: int,
    availIn: AvailabilityUpdate,
    user: CurrentUser,
    session: DbSession
) -> AvailabilityWindow:
    window = _ownedOr404(session, window_id, user.id)
    applyPartialUpdate(window, availIn.model_dump(exclude_unset=True))
    if window.start_minutes >= window.end_minutes:
        raise HTTPException(status_code=422, detail="start_minutes must be less than end_minutes")
    session.add(window)
    session.commit()
    session.refresh(window)
    return window


@router.delete("/{window_id}", status_code=204)
def deleteAvailability(window_id: int, user: CurrentUser, session: DbSession) -> None:
    window = _ownedOr404(session, window_id, user.id)
    session.delete(window)
    session.commit()
