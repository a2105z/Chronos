from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal

from app.models.task import Task

AllocationStyle = Literal["balanced", "deadline_focus", "deep_work"]


@dataclass(frozen=True)
class AllocationScoreWeights:
    """Tunable weights for balancing urgency, priority, and block quality."""

    priority_weight: float = 1.5
    deadline_weight: float = 3.0
    duration_weight: float = 1.0
    preference_weight: float = 1.0
    continuity_weight: float = 0.8
    lateness_penalty_weight: float = 6.0


DEFAULT_WEIGHTS = AllocationScoreWeights()
DEADLINE_FOCUS_WEIGHTS = AllocationScoreWeights(priority_weight=1.4, deadline_weight=4.2, duration_weight=0.9, preference_weight=0.8, continuity_weight=0.4, lateness_penalty_weight=8.0)
DEEP_WORK_WEIGHTS = AllocationScoreWeights(priority_weight=1.2, deadline_weight=2.0, duration_weight=1.6, preference_weight=1.2, continuity_weight=1.7, lateness_penalty_weight=6.0)


def _to_utc_naive(value: datetime) -> datetime:
    """Normalize timezone-aware datetimes to UTC-naive for safe math."""
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)


def _minutes_until(reference: datetime, point: datetime) -> float:
    """Return signed minutes from reference to point (negative means in past)."""
    return (_to_utc_naive(point) - _to_utc_naive(reference)).total_seconds() / 60.0


def _is_soon_deadline(task: Task, now: datetime, horizon_minutes: int = 72 * 60) -> bool:
    """Return True when task has a near-term deadline."""
    if task.deadline is None:
        return False
    minutes = _minutes_until(now, task.deadline)
    return 0 <= minutes <= horizon_minutes


def _is_deep_work_task(task: Task) -> bool:
    """Heuristic for tasks that benefit from longer contiguous focus."""
    return task.estimated_duration_minutes >= 90 and not task.splittable


def choose_allocation_style(tasks: list[Task], now: datetime | None = None) -> AllocationStyle:
    """Pick a weight profile from workload shape: deadline_focus, deep_work, or balanced."""
    if not tasks:
        return "balanced"

    reference = now or datetime.utcnow()
    task_count = len(tasks)

    soon_deadline_count = 0
    deep_work_count = 0
    for task in tasks:
        if _is_soon_deadline(task, reference):
            soon_deadline_count += 1
        if _is_deep_work_task(task):
            deep_work_count += 1

    soon_deadline_ratio = soon_deadline_count / task_count
    deep_work_ratio = deep_work_count / task_count

    if soon_deadline_ratio >= 0.35:
        return "deadline_focus"
    if deep_work_ratio >= 0.40:
        return "deep_work"
    return "balanced"


def weights_for_style(style: AllocationStyle) -> AllocationScoreWeights:
    """Return concrete weights for the selected style."""
    if style == "deadline_focus":
        return DEADLINE_FOCUS_WEIGHTS
    if style == "deep_work":
        return DEEP_WORK_WEIGHTS
    return DEFAULT_WEIGHTS


def _time_preference_score(task: Task, slot_start: datetime) -> float:
    """Return preference alignment in [0, 1]."""
    preferred = task.preferred_time_of_day
    if preferred is None or preferred == "anytime":
        return 1.0

    hour = slot_start.hour
    if preferred == "morning":
        if 6 <= hour < 12:
            return 1.0
        return 0.0
    if preferred == "afternoon":
        if 12 <= hour < 18:
            return 1.0
        return 0.0
    if preferred == "evening":
        if 18 <= hour < 24:
            return 1.0
        return 0.0
    return 0.5


def _priority_score(task: Task) -> float:
    """Map integer priority to a bounded, smooth score."""
    bounded = min(task.priority, 10)
    return float(bounded) / 10.0


def _deadline_score(task: Task, slot_end: datetime) -> float:
    """Reward larger remaining slack before deadline; penalize lateness."""
    if task.deadline is None:
        return 0.5

    slack_minutes = (_to_utc_naive(task.deadline) - _to_utc_naive(slot_end)).total_seconds() / 60.0
    if slack_minutes < 0:
        return max(-1.0, slack_minutes / 120.0)

    clamped = min(slack_minutes, 24.0 * 60.0)
    return clamped / (24.0 * 60.0)


def _continuity_score(previous_end: datetime | None, slot_start: datetime) -> float:
    """Prefer extending an existing run of the same task when possible."""
    if previous_end is None:
        return 0.0
    gap_minutes = (slot_start - previous_end).total_seconds() / 60.0
    if gap_minutes < 0:
        return -1.0
    if gap_minutes == 0:
        return 1.0
    if gap_minutes <= 15:
        return 0.5
    if gap_minutes <= 60:
        return 0.1
    return 0.0


def score_splittable_candidate(
    task: Task,
    slot_start: datetime,
    slot_end: datetime,
    allocated_minutes: int,
    remaining_before_pick: int,
    previous_end_for_task: datetime | None,
    weights: AllocationScoreWeights = DEFAULT_WEIGHTS
) -> float:
    """Compute scalar utility for choosing one splittable chunk."""
    duration_fraction = 0.0
    if remaining_before_pick > 0:
        duration_fraction = float(allocated_minutes) / float(remaining_before_pick)

    preference = _time_preference_score(task, slot_start)
    priority = _priority_score(task)
    deadline = _deadline_score(task, slot_end)
    continuity = _continuity_score(previous_end_for_task, slot_start)

    score = 0.0
    score += weights.duration_weight * duration_fraction
    score += weights.preference_weight * preference
    score += weights.priority_weight * priority
    score += weights.deadline_weight * max(deadline, 0.0)
    score += weights.continuity_weight * continuity

    if deadline < 0:
        score += weights.lateness_penalty_weight * deadline

    return score


def score_fixed_candidate(
    task: Task,
    candidate_start: datetime,
    candidate_end: datetime,
    weights: AllocationScoreWeights = DEFAULT_WEIGHTS
) -> float:
    """Compute scalar utility for placing one contiguous non-splittable block."""
    preference = _time_preference_score(task, candidate_start)
    priority = _priority_score(task)
    deadline = _deadline_score(task, candidate_end)

    score = 0.0
    score += weights.preference_weight * preference
    score += weights.priority_weight * priority
    score += weights.deadline_weight * max(deadline, 0.0)

    if deadline < 0:
        score += weights.lateness_penalty_weight * deadline

    return score
