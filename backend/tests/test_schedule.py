"""Tests for schedule generation API and engine."""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.services.scheduler.constraints import (
    validateMaxContinuousWork,
    validateNoOverlap,
    validateNoProtectedOverlap,
    validateWithinAvailability,
)


def mkDt(dateStr: str) -> str:
    """Return ISO datetime string for schedule API."""
    result = dateStr + "T00:00:00"
    return result


def test_generate_schedule_empty_no_tasks(client: TestClient):
    """Generate returns empty when no tasks."""
    client.post(
        "/api/availability",
        json={"day_of_week": 0, "start_minutes": 540, "end_minutes": 1020},
    )
    response = client.post(
        "/api/schedule",
        json={"start_date": mkDt("2025-01-06"), "end_date": mkDt("2025-01-12")},
    )
    assert response.status_code == 200
    assert response.json() == []



def test_generate_schedule_empty_no_availability(client: TestClient):
    """Generate returns empty when no availability windows."""
    client.post(
        "/api/tasks",
        json={"name": "Task A", "estimated_duration_minutes": 60},
    )
    response = client.post(
        "/api/schedule",
        json={"start_date": mkDt("2025-01-06"), "end_date": mkDt("2025-01-12")},
    )
    assert response.status_code == 200
    assert response.json() == []



def test_generate_schedule_single_task(client: TestClient):
    """Generate places one task in availability."""
    client.post(
        "/api/tasks",
        json={"name": "Study", "estimated_duration_minutes": 60},
    )
    client.post(
        "/api/availability",
        json={"day_of_week": 0, "start_minutes": 540, "end_minutes": 1020},
    )
    response = client.post(
        "/api/schedule",
        json={"start_date": mkDt("2025-01-06"), "end_date": mkDt("2025-01-10")},
    )
    assert response.status_code == 200
    blocks = response.json()
    assert len(blocks) == 1
    assert blocks[0]["task_name"] == "Study"
    assert blocks[0]["duration_minutes"] == 60
    assert "start_time" in blocks[0]
    assert "end_time" in blocks[0]



def test_generate_schedule_no_overlap(client: TestClient):
    """Generated blocks never overlap. Uses invariant validator."""
    client.post(
        "/api/tasks",
        json={"name": "A", "estimated_duration_minutes": 60},
    )
    client.post(
        "/api/tasks",
        json={"name": "B", "estimated_duration_minutes": 60},
    )
    client.post(
        "/api/availability",
        json={"day_of_week": 0, "start_minutes": 540, "end_minutes": 1020},
    )
    response = client.post(
        "/api/schedule",
        json={"start_date": mkDt("2025-01-06"), "end_date": mkDt("2025-01-10")},
    )
    assert response.status_code == 200
    blocks = response.json()
    assert len(blocks) >= 2
    validateNoOverlap(blocks)



def test_generate_schedule_within_availability(client: TestClient):
    """Blocks fall within availability windows (Mon 9-17). Uses invariant validator."""
    windows = [{"day_of_week": 0, "start_minutes": 540, "end_minutes": 1020}]
    client.post(
        "/api/tasks",
        json={"name": "Work", "estimated_duration_minutes": 120},
    )
    client.post(
        "/api/availability",
        json=windows[0],
    )
    response = client.post(
        "/api/schedule",
        json={"start_date": mkDt("2025-01-06"), "end_date": mkDt("2025-01-08")},
    )
    assert response.status_code == 200
    blocks = response.json()
    assert len(blocks) == 1
    validateWithinAvailability(blocks, windows)



def test_generate_schedule_respects_protected_block(client: TestClient):
    """Blocks do not overlap protected time (lunch 12-13). Uses invariant validator."""
    protected = [
        {
            "constraint_type": "protected_block",
            "day_of_week": 0,
            "start_minutes": 720,
            "end_minutes": 780,
        }
    ]
    client.post(
        "/api/tasks",
        json={"name": "Morning", "estimated_duration_minutes": 240},
    )
    client.post(
        "/api/availability",
        json={"day_of_week": 0, "start_minutes": 540, "end_minutes": 1020},
    )
    client.post(
        "/api/constraints",
        json=protected[0],
    )
    response = client.post(
        "/api/schedule",
        json={"start_date": mkDt("2025-01-06"), "end_date": mkDt("2025-01-08")},
    )
    assert response.status_code == 200
    blocks = response.json()
    validateNoProtectedOverlap(blocks, protected)



def test_generate_schedule_splittable_task(client: TestClient):
    """Splittable task can span multiple blocks."""
    client.post(
        "/api/tasks",
        json={"name": "Splittable", "estimated_duration_minutes": 90, "splittable": True},
    )
    client.post(
        "/api/availability",
        json={"day_of_week": 0, "start_minutes": 540, "end_minutes": 600},
    )
    client.post(
        "/api/availability",
        json={"day_of_week": 0, "start_minutes": 660, "end_minutes": 720},
    )
    response = client.post(
        "/api/schedule",
        json={"start_date": mkDt("2025-01-06"), "end_date": mkDt("2025-01-08")},
    )
    assert response.status_code == 200
    blocks = []
    for b in response.json():
        if b["task_name"] == "Splittable":
            blocks.append(b)
    assert len(blocks) >= 2
    total_mins = 0
    for b in blocks:
        total_mins += b["duration_minutes"]
    assert total_mins == 90



def test_generate_schedule_export_ics(client: TestClient):
    """Export returns valid .ics file."""
    client.post(
        "/api/tasks",
        json={"name": "Export Test", "estimated_duration_minutes": 30},
    )
    client.post(
        "/api/availability",
        json={"day_of_week": 0, "start_minutes": 540, "end_minutes": 1020},
    )
    response = client.post(
        "/api/schedule/export",
        json={"start_date": mkDt("2025-01-06"), "end_date": mkDt("2025-01-10")},
    )
    assert response.status_code == 200
    assert "text/calendar" in response.headers.get("content-type", "")
    content = response.content
    assert b"BEGIN:VCALENDAR" in content
    assert b"END:VCALENDAR" in content



def test_invariants_max_continuous_work_splittable(client: TestClient):
    """Splittable task respects max_continuous_work. No block exceeds limit."""
    client.post(
        "/api/tasks",
        json={"name": "Long Task", "estimated_duration_minutes": 120, "splittable": True},
    )
    client.post(
        "/api/availability",
        json={"day_of_week": 0, "start_minutes": 540, "end_minutes": 1020},
    )
    client.post(
        "/api/constraints",
        json={"constraint_type": "max_continuous_work", "value": 60},
    )
    response = client.post(
        "/api/schedule",
        json={"start_date": mkDt("2025-01-06"), "end_date": mkDt("2025-01-08")},
    )
    assert response.status_code == 200
    blocks = response.json()
    validateMaxContinuousWork(blocks, 60)
    totalMins = 0
    for b in blocks:
        if b["task_name"] == "Long Task":
            totalMins += b["duration_minutes"]
    assert totalMins == 120



def test_invariants_max_continuous_work_non_splittable(client: TestClient):
    """Non-splittable task exceeding max_continuous_work is split to satisfy constraint."""
    client.post(
        "/api/tasks",
        json={"name": "Long Fixed", "estimated_duration_minutes": 90, "splittable": False},
    )
    client.post(
        "/api/availability",
        json={"day_of_week": 0, "start_minutes": 540, "end_minutes": 1020},
    )
    client.post(
        "/api/constraints",
        json={"constraint_type": "max_continuous_work", "value": 60},
    )
    response = client.post(
        "/api/schedule",
        json={"start_date": mkDt("2025-01-06"), "end_date": mkDt("2025-01-08")},
    )
    assert response.status_code == 200
    blocks = response.json()
    validateMaxContinuousWork(blocks, 60)
    validateNoOverlap(blocks)
    longFixedBlocks = [b for b in blocks if b["task_name"] == "Long Fixed"]
    assert len(longFixedBlocks) >= 2
    totalMins = sum(b["duration_minutes"] for b in longFixedBlocks)
    assert totalMins == 90



def test_invariants_all_constraints_combined(client: TestClient):
    """Schedule satisfies all invariants: no overlap, availability, protected block, max continuous work."""
    windows = [{"day_of_week": 0, "start_minutes": 540, "end_minutes": 1020}]
    protected = [
        {
            "constraint_type": "protected_block",
            "day_of_week": 0,
            "start_minutes": 720,
            "end_minutes": 780,
        }
    ]
    client.post(
        "/api/tasks",
        json={"name": "Task A", "estimated_duration_minutes": 45},
    )
    client.post(
        "/api/tasks",
        json={"name": "Task B", "estimated_duration_minutes": 60, "splittable": True},
    )
    client.post(
        "/api/availability",
        json=windows[0],
    )
    client.post(
        "/api/constraints",
        json=protected[0],
    )
    client.post(
        "/api/constraints",
        json={"constraint_type": "max_continuous_work", "value": 60},
    )
    response = client.post(
        "/api/schedule",
        json={"start_date": mkDt("2025-01-06"), "end_date": mkDt("2025-01-10")},
    )
    assert response.status_code == 200
    blocks = response.json()
    validateNoOverlap(blocks)
    validateWithinAvailability(blocks, windows)
    validateNoProtectedOverlap(blocks, protected)
    validateMaxContinuousWork(blocks, 60)
