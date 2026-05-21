from datetime import datetime

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.core.deps import CurrentUser, DbSession
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.services.schedule_persistence import deleteBlocksForTask
from app.utils import applyPartialUpdate

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def _ownedOr404(session: DbSession, taskId: int, userId: int) -> Task:
    task = session.get(Task, taskId)
    if not task or task.user_id != userId:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("", response_model=list[TaskRead])
def listTasks(user: CurrentUser, session: DbSession) -> list[Task]:
    """List current user's tasks, newest first."""
    stmt = (
        select(Task)
        .where(Task.user_id == user.id)
        .order_by(Task.created_at.desc(), Task.id.desc())
    )
    return list(session.exec(stmt).all())


@router.post("", response_model=TaskRead, status_code=201)
def createTask(taskIn: TaskCreate, user: CurrentUser, session: DbSession) -> Task:
    """Create a new task for the current user."""
    task = Task(**taskIn.model_dump(), user_id=user.id)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.get("/{task_id}", response_model=TaskRead)
def getTask(task_id: int, user: CurrentUser, session: DbSession) -> Task:
    return _ownedOr404(session, task_id, user.id)


@router.put("/{task_id}", response_model=TaskRead)
def updateTask(task_id: int, taskIn: TaskUpdate, user: CurrentUser, session: DbSession) -> Task:
    task = _ownedOr404(session, task_id, user.id)
    applyPartialUpdate(task, taskIn.model_dump(exclude_unset=True))
    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def deleteTask(task_id: int, user: CurrentUser, session: DbSession) -> None:
    task = _ownedOr404(session, task_id, user.id)
    deleteBlocksForTask(session, task_id)
    session.flush()
    session.delete(task)
    session.commit()
