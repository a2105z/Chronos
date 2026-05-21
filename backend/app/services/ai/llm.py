from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Optional

from app.core.config import getSettings
from app.services.ai.parser import (
    PlanIntent,
    PlannedAvailability,
    PlannedConstraint,
    PlannedTask,
    parseDeterministic,
)


def refineWithLlm(prompt: str, base: PlanIntent, reference: Optional[datetime] = None) -> PlanIntent:
    """Optionally refine a deterministic parse via OpenAI JSON mode."""
    settings = getSettings()
    if not settings.OPENAI_API_KEY:
        return base

    try:
        from openai import OpenAI
    except ImportError:
        return base

    ref = reference or datetime.utcnow()
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    system = (
        "You refine internship scheduling intents into JSON. "
        "Return only JSON with keys: tasks, availability, constraints, notes. "
        "tasks items: name, estimated_duration_minutes, priority, preferred_time_of_day, "
        "deadline (ISO or null), earliest_start (ISO or null), splittable. "
        "If the user asks for N spots/blocks/sessions each of duration D "
        "(e.g. 'find me 3 spots, each 2 hours'), emit N separate tasks of D minutes "
        "(splittable=false), named clearly (Focus 1/N …). "
        "availability items: day_of_week (0=Mon..6 or -1 weekdays), start_minutes, end_minutes, weekdays_only. "
        "constraints items: constraint_type, day_of_week, start_minutes, end_minutes, value, every_weekday. "
        f"Reference datetime (CST): {ref.isoformat()}"
    )
    userMsg = (
        f"Original prompt: {prompt}\n"
        f"Deterministic parse: {json.dumps(_intentToDict(base), default=str)}\n"
        "Improve if needed; keep faithful to the user prompt."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": userMsg}
            ],
            temperature=0.2
        )
        content = response.choices[0].message.content or "{}"
        data = json.loads(content)
        refined = _dictToIntent(prompt, data)
        refined.parser = "openai"
        refined.notes.append("Refined with OpenAI.")
        return refined
    except Exception:
        base.notes.append("OpenAI refine failed; using deterministic parse.")
        return base


def _intentToDict(intent: PlanIntent) -> dict[str, Any]:
    return {
        "tasks": [
            {
                "name": t.name,
                "estimated_duration_minutes": t.estimated_duration_minutes,
                "priority": t.priority,
                "preferred_time_of_day": t.preferred_time_of_day,
                "deadline": t.deadline.isoformat() if t.deadline else None,
                "earliest_start": t.earliest_start.isoformat() if t.earliest_start else None,
                "splittable": t.splittable
            }
            for t in intent.tasks
        ],
        "availability": [
            {
                "day_of_week": a.day_of_week,
                "start_minutes": a.start_minutes,
                "end_minutes": a.end_minutes,
                "weekdays_only": a.weekdays_only
            }
            for a in intent.availability
        ],
        "constraints": [
            {
                "constraint_type": c.constraint_type,
                "day_of_week": c.day_of_week,
                "start_minutes": c.start_minutes,
                "end_minutes": c.end_minutes,
                "value": c.value,
                "every_weekday": c.every_weekday
            }
            for c in intent.constraints
        ],
        "notes": intent.notes
    }


def _parseIso(value: Any) -> Optional[datetime]:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return None


def _dictToIntent(prompt: str, data: dict[str, Any]) -> PlanIntent:
    intent = PlanIntent(raw_prompt=prompt)
    for t in data.get("tasks") or []:
        intent.tasks.append(
            PlannedTask(
                name=str(t.get("name") or "Untitled task"),
                estimated_duration_minutes=int(t.get("estimated_duration_minutes") or 60),
                priority=int(t.get("priority") or 0),
                preferred_time_of_day=t.get("preferred_time_of_day"),
                deadline=_parseIso(t.get("deadline")),
                earliest_start=_parseIso(t.get("earliest_start")),
                splittable=bool(t.get("splittable"))
            )
        )
    for a in data.get("availability") or []:
        intent.availability.append(
            PlannedAvailability(
                day_of_week=int(a.get("day_of_week", 0)),
                start_minutes=int(a.get("start_minutes") or 0),
                end_minutes=int(a.get("end_minutes") or 0),
                weekdays_only=bool(a.get("weekdays_only"))
            )
        )
    for c in data.get("constraints") or []:
        intent.constraints.append(
            PlannedConstraint(
                constraint_type=str(c.get("constraint_type") or "protected_block"),
                day_of_week=c.get("day_of_week"),
                start_minutes=c.get("start_minutes"),
                end_minutes=c.get("end_minutes"),
                value=c.get("value"),
                every_weekday=bool(c.get("every_weekday"))
            )
        )
    for note in data.get("notes") or []:
        intent.notes.append(str(note))
    return intent


def parseWithOptionalLlm(prompt: str, reference: Optional[datetime] = None) -> PlanIntent:
    base = parseDeterministic(prompt, reference=reference)
    return refineWithLlm(prompt, base, reference=reference)
