from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import getSession
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskRead
from app.utils import applyPartialUpdate


router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskRead])
def listTasks(session: Session = Depends(getSession)) -> list[Task]:
    """List all tasks, newest first."""
    stmt = select(Task)
    stmt = stmt.order_by(Task.created_at.desc(), Task.id.desc())
    rows = session.exec(stmt).all()
    return list(rows)



@router.post("", response_model=TaskRead, status_code=201)
def createTask(taskIn: TaskCreate, session: Session = Depends(getSession)) -> Task:
    """Create a new task."""
    task = Task(**taskIn.model_dump())
    session.add(task)
    session.commit()
    session.refresh(task)
    return task



@router.get("/{task_id}", response_model=TaskRead)
def getTask(task_id: int, session: Session = Depends(getSession)) -> Task:
    """Get a task by id."""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task



@router.put("/{task_id}", response_model=TaskRead)
def updateTask(task_id: int, taskIn: TaskUpdate, session: Session = Depends(getSession)) -> Task:
    """Update a task. Partial updates supported."""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    applyPartialUpdate(task, taskIn.model_dump(exclude_unset=True))
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)
    return task



@router.delete("/{task_id}", status_code=204)
def deleteTask(task_id: int, session: Session = Depends(getSession)) -> None:
    """Delete a task."""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
