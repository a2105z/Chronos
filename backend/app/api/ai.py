
from fastapi import APIRouter
from sqlmodel import select

from app.core.deps import CurrentUser, DbSession
from app.core.timeutil import nowCst
from app.models.availability import AvailabilityWindow
from app.models.task import Task
from app.schemas.ai import (
    AiExplainRequest,
    AiPlanCreated,
    AiPlanRequest,
    AiPlanResponse,
    AiSuggestionsResponse,
    PlanIntentOut,
    PlannedAvailabilityOut,
    PlannedConstraintOut,
    PlannedTaskOut,
)
from app.schemas.schedule import ScheduleGenerateResponse
from app.services.ai.apply import applyPlanIntent
from app.services.ai.planner import (
    buildAssistantMessage,
    planFromNaturalLanguage,
    ruleBasedSuggestions,
)
from app.services.scheduler.engine import SchedulingEngine

router = APIRouter(prefix="/api/ai", tags=["ai"])


def _intentOut(intent) -> PlanIntentOut:
    return PlanIntentOut(
        raw_prompt=intent.raw_prompt,
        tasks=[
            PlannedTaskOut(
                name=t.name,
                estimated_duration_minutes=t.estimated_duration_minutes,
                priority=t.priority,
                preferred_time_of_day=t.preferred_time_of_day,
                deadline=t.deadline,
                earliest_start=t.earliest_start,
                splittable=t.splittable
            )
            for t in intent.tasks
        ],
        availability=[
            PlannedAvailabilityOut(
                day_of_week=a.day_of_week,
                start_minutes=a.start_minutes,
                end_minutes=a.end_minutes,
                weekdays_only=a.weekdays_only
            )
            for a in intent.availability
        ],
        constraints=[
            PlannedConstraintOut(
                constraint_type=c.constraint_type,
                day_of_week=c.day_of_week,
                start_minutes=c.start_minutes,
                end_minutes=c.end_minutes,
                value=c.value,
                every_weekday=c.every_weekday
            )
            for c in intent.constraints
        ],
        notes=intent.notes,
        parser=intent.parser
    )


@router.post("/plan", response_model=AiPlanResponse)
def planWeek(body: AiPlanRequest, user: CurrentUser, session: DbSession) -> AiPlanResponse:
    # Parse relative to current CST — not week start — so past days are not planned.
    parseRef = nowCst()
    intent = planFromNaturalLanguage(body.prompt, reference=parseRef, useLlm=True)

    created = AiPlanCreated(tasks=[], availability=[], constraints=[])
    schedule = None  # type: ScheduleGenerateResponse | None

    if body.apply:
        result = applyPlanIntent(
            session,
            user,
            intent,
            body.start_date,
            body.end_date,
            runSchedule=True
        )
        created = AiPlanCreated(
            tasks=list(result["tasks"]),
            availability=list(result["availability"]),
            constraints=list(result["constraints"])
        )
        schedule = result["schedule"]
    else:
        schedule = ScheduleGenerateResponse(blocks=[], unscheduled=[], summary="apply=false; nothing persisted.")

    summary = schedule.summary if schedule else "No schedule run."
    message = buildAssistantMessage(
        intent,
        {"availability": created.availability, "constraints": created.constraints, "tasks": created.tasks},
        summary
    )

    return AiPlanResponse(
        intent=_intentOut(intent),
        created=created,
        schedule=schedule,
        assistant_message=message
    )


@router.post("/explain", response_model=ScheduleGenerateResponse)
def explainSchedule(body: AiExplainRequest, user: CurrentUser, session: DbSession) -> ScheduleGenerateResponse:
    engine = SchedulingEngine(session, userId=user.id)
    return engine.explain(body.start_date, body.end_date)


@router.get("/suggestions", response_model=AiSuggestionsResponse)
def suggestions(user: CurrentUser, session: DbSession) -> AiSuggestionsResponse:
    tasks = list(session.exec(select(Task).where(Task.user_id == user.id)).all())
    avail = list(session.exec(select(AvailabilityWindow).where(AvailabilityWindow.user_id == user.id)).all())
    longNames = [t.name for t in tasks if t.estimated_duration_minutes >= 120]
    tips = ruleBasedSuggestions(
        taskCount=len(tasks),
        availabilityCount=len(avail),
        unscheduledCount=0,
        longTaskNames=longNames
    )
    return AiSuggestionsResponse(suggestions=tips)
