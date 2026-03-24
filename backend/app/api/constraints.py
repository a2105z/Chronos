from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import getSession
from app.utils import applyPartialUpdate
from app.models.constraint import Constraint
from app.schemas.constraint import (
    ConstraintCreate,
    ConstraintRead,
    ConstraintUpdate,
    validateConstraintFields,
)


router = APIRouter(prefix="/api/constraints", tags=["constraints"])


def validateConstraint(constraint: Constraint) -> None:
    """Check that constraint fields match its type."""
    try:
        validateConstraintFields(
            constraint.constraint_type,
            constraint.day_of_week,
            constraint.start_minutes,
            constraint.end_minutes,
            constraint.value,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e



@router.get("", response_model=list[ConstraintRead])
def listConstraints(session: Session = Depends(getSession)) -> list[Constraint]:
    """List all constraints."""
    rows = session.exec(select(Constraint)).all()
    return list(rows)



@router.post("", response_model=ConstraintRead, status_code=201)
def createConstraint(constraintIn: ConstraintCreate, session: Session = Depends(getSession)) -> Constraint:
    """Create a constraint (protected_block or max_continuous_work)."""
    constraint = Constraint(**constraintIn.model_dump())
    session.add(constraint)
    session.commit()
    session.refresh(constraint)
    return constraint



@router.get("/{constraint_id}", response_model=ConstraintRead)
def getConstraint(constraint_id: int, session: Session = Depends(getSession)) -> Constraint:
    """Get a single constraint."""
    constraint = session.get(Constraint, constraint_id)
    if not constraint:
        raise HTTPException(status_code=404, detail="Constraint not found")
    return constraint



@router.put("/{constraint_id}", response_model=ConstraintRead)
def updateConstraint(constraint_id: int, constraintIn: ConstraintUpdate, session: Session = Depends(getSession)) -> Constraint:
    """Update a constraint. Validates after merge."""
    constraint = session.get(Constraint, constraint_id)
    if not constraint:
        raise HTTPException(status_code=404, detail="Constraint not found")

    applyPartialUpdate(constraint, constraintIn.model_dump(exclude_unset=True))
    validateConstraint(constraint)

    session.add(constraint)
    session.commit()
    session.refresh(constraint)
    return constraint



@router.delete("/{constraint_id}", status_code=204)
def deleteConstraint(constraint_id: int, session: Session = Depends(getSession)) -> None:
    """Delete a constraint."""
    constraint = session.get(Constraint, constraint_id)
    if not constraint:
        raise HTTPException(status_code=404, detail="Constraint not found")
    session.delete(constraint)
    session.commit()
