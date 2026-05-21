from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.core.deps import CurrentUser, DbSession
from app.models.constraint import Constraint
from app.schemas.constraint import (
    ConstraintCreate,
    ConstraintRead,
    ConstraintUpdate,
    validateConstraintFields,
)
from app.utils import applyPartialUpdate

router = APIRouter(prefix="/api/constraints", tags=["constraints"])


def validateConstraint(constraint: Constraint) -> None:
    try:
        validateConstraintFields(
            constraint.constraint_type,
            constraint.day_of_week,
            constraint.start_minutes,
            constraint.end_minutes,
            constraint.value
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e


def _ownedOr404(session: DbSession, constraintId: int, userId: int) -> Constraint:
    constraint = session.get(Constraint, constraintId)
    if not constraint or constraint.user_id != userId:
        raise HTTPException(status_code=404, detail="Constraint not found")
    return constraint


@router.get("", response_model=list[ConstraintRead])
def listConstraints(user: CurrentUser, session: DbSession) -> list[Constraint]:
    return list(session.exec(select(Constraint).where(Constraint.user_id == user.id)).all())


@router.post("", response_model=ConstraintRead, status_code=201)
def createConstraint(
    constraintIn: ConstraintCreate,
    user: CurrentUser,
    session: DbSession
) -> Constraint:
    constraint = Constraint(**constraintIn.model_dump(), user_id=user.id)
    session.add(constraint)
    session.commit()
    session.refresh(constraint)
    return constraint


@router.get("/{constraint_id}", response_model=ConstraintRead)
def getConstraint(constraint_id: int, user: CurrentUser, session: DbSession) -> Constraint:
    return _ownedOr404(session, constraint_id, user.id)


@router.put("/{constraint_id}", response_model=ConstraintRead)
def updateConstraint(
    constraint_id: int,
    constraintIn: ConstraintUpdate,
    user: CurrentUser,
    session: DbSession
) -> Constraint:
    constraint = _ownedOr404(session, constraint_id, user.id)
    applyPartialUpdate(constraint, constraintIn.model_dump(exclude_unset=True))
    validateConstraint(constraint)
    session.add(constraint)
    session.commit()
    session.refresh(constraint)
    return constraint


@router.delete("/{constraint_id}", status_code=204)
def deleteConstraint(constraint_id: int, user: CurrentUser, session: DbSession) -> None:
    constraint = _ownedOr404(session, constraint_id, user.id)
    session.delete(constraint)
    session.commit()
