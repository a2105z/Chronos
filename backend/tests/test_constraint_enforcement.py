"""Unit tests for constraint reinforcement and invariant validation."""

from datetime import datetime

import pytest

from app.models.constraint import Constraint
from app.services.scheduler.constraints import (
    getMaxContinuousWorkMinutes,
    validateMaxContinuousWork,
    validateNoOverlap,
    validateNoProtectedOverlap,
    validateWithinAvailability,
)


def test_getMaxContinuousWorkMinutes_empty():
    """Returns None when no constraints."""
    result = getMaxContinuousWorkMinutes([])
    assert result is None



def test_getMaxContinuousWorkMinutes_single():
    """Returns value for single max_continuous_work constraint."""
    c = Constraint(constraint_type="max_continuous_work", value=60)
    result = getMaxContinuousWorkMinutes([c])
    assert result == 60



def test_getMaxContinuousWorkMinutes_multiple_takes_strictest():
    """When multiple max_continuous_work exist, returns smallest (strictest)."""
    c1 = Constraint(constraint_type="max_continuous_work", value=90)
    c2 = Constraint(constraint_type="max_continuous_work", value=45)
    result = getMaxContinuousWorkMinutes([c1, c2])
    assert result == 45



def test_getMaxContinuousWorkMinutes_ignores_protected_block():
    """Ignores protected_block constraints."""
    c = Constraint(
        constraint_type="protected_block",
        day_of_week=0,
        start_minutes=720,
        end_minutes=780,
    )
    result = getMaxContinuousWorkMinutes([c])
    assert result is None



def test_validateNoOverlap_pass():
    """Does not raise when blocks do not overlap."""
    blocks = [
        {"start_time": "2025-01-06T09:00:00", "end_time": "2025-01-06T10:00:00"},
        {"start_time": "2025-01-06T10:00:00", "end_time": "2025-01-06T11:00:00"},
    ]
    validateNoOverlap(blocks)



def test_validateNoOverlap_fail():
    """Raises when blocks overlap."""
    blocks = [
        {"start_time": "2025-01-06T09:00:00", "end_time": "2025-01-06T10:30:00"},
        {"start_time": "2025-01-06T10:00:00", "end_time": "2025-01-06T11:00:00"},
    ]
    with pytest.raises(AssertionError, match="overlap"):
        validateNoOverlap(blocks)



def test_validateMaxContinuousWork_pass():
    """Does not raise when all blocks within limit."""
    blocks = [
        {"duration_minutes": 30},
        {"duration_minutes": 45},
    ]
    validateMaxContinuousWork(blocks, 60)



def test_validateMaxContinuousWork_fail():
    """Raises when block exceeds limit."""
    blocks = [
        {"duration_minutes": 30},
        {"duration_minutes": 90},
    ]
    with pytest.raises(AssertionError, match="exceeds max_continuous_work"):
        validateMaxContinuousWork(blocks, 60)



def test_validateNoProtectedOverlap_pass():
    """Does not raise when blocks avoid protected time."""
    blocks = [
        {"start_time": "2025-01-06T09:00:00", "end_time": "2025-01-06T12:00:00"},
    ]
    protected = [
        {"constraint_type": "protected_block", "day_of_week": 0, "start_minutes": 720, "end_minutes": 780},
    ]
    validateNoProtectedOverlap(blocks, protected)



def test_validateNoProtectedOverlap_fail():
    """Raises when block overlaps protected time."""
    blocks = [
        {"start_time": "2025-01-06T11:30:00", "end_time": "2025-01-06T12:30:00"},
    ]
    protected = [
        {"constraint_type": "protected_block", "day_of_week": 0, "start_minutes": 720, "end_minutes": 780},
    ]
    with pytest.raises(AssertionError, match="overlaps protected"):
        validateNoProtectedOverlap(blocks, protected)



def test_validateWithinAvailability_pass():
    """Does not raise when block within window."""
    blocks = [
        {"start_time": "2025-01-06T09:00:00", "end_time": "2025-01-06T10:00:00"},
    ]
    windows = [{"day_of_week": 0, "start_minutes": 540, "end_minutes": 1020}]
    validateWithinAvailability(blocks, windows)



def test_validateWithinAvailability_fail():
    """Raises when block outside window."""
    blocks = [
        {"start_time": "2025-01-06T08:00:00", "end_time": "2025-01-06T09:00:00"},
    ]
    windows = [{"day_of_week": 0, "start_minutes": 540, "end_minutes": 1020}]
    with pytest.raises(AssertionError, match="not within"):
        validateWithinAvailability(blocks, windows)
