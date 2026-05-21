from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from app.services.ai.llm import parseWithOptionalLlm
from app.services.ai.parser import PlanIntent, parseDeterministic


def planFromNaturalLanguage(
    prompt: str,
    reference: Optional[datetime] = None,
    useLlm: bool = True
) -> PlanIntent:
    """Interpret NL into PlanIntent. Deterministic always; LLM optional."""
    if useLlm:
        return parseWithOptionalLlm(prompt, reference=reference)
    return parseDeterministic(prompt, reference=reference)


def buildAssistantMessage(intent: PlanIntent, created: dict[str, Any], scheduleSummary: str) -> str:
    parts: list[str] = []
    parts.append(f"Interpreted with {intent.parser} parser.")
    if intent.tasks:
        names = ", ".join(t.name for t in intent.tasks)
        parts.append(f"Tasks: {names}.")
    if intent.availability:
        parts.append(f"Added {len(created.get('availability') or [])} availability window(s).")
    if intent.constraints:
        parts.append(f"Added {len(created.get('constraints') or [])} constraint(s).")
    if intent.notes:
        parts.append(" ".join(intent.notes))
    parts.append(scheduleSummary)
    return " ".join(parts)


def ruleBasedSuggestions(
    taskCount: int,
    availabilityCount: int,
    unscheduledCount: int,
    longTaskNames: list[str]
) -> list[str]:
    suggestions: list[str] = []
    if availabilityCount == 0:
        suggestions.append("Add weekday availability (e.g. 9am–5pm) so the engine can place blocks.")
    if unscheduledCount > 0:
        suggestions.append("Review unscheduled diagnostics — relax deadlines or split long tasks.")
    for name in longTaskNames[:3]:
        suggestions.append(f"Mark “{name}” as splittable or shorten it to fit max continuous work limits.")
    if taskCount == 0:
        suggestions.append("Describe work in plain English on Plan, e.g. “Schedule 2 hours of resume polish tomorrow morning”.")
    if not suggestions:
        suggestions.append("Your week looks healthy — regenerate after adding new tasks.")
    return suggestions
