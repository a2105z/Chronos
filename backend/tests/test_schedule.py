"""Tests for schedule generation API and engine."""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from icalendar import Calendar

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
        json={"start_date": mkDt("2030-01-07"), "end_date": mkDt("2030-01-13")},
    )
    assert response.status_code == 200
    assert response.json() == []



def test_generate_schedule_fallback_availability_when_none_configured(client: TestClient):
    """With no availability rows, engine uses full-week fallback and can still place tasks."""
    client.post(
        "/api/tasks",
        json={"name": "Task A", "estimated_duration_minutes": 60},
    )
    response = client.post(
        "/api/schedule",
        json={"start_date": mkDt("2030-01-07"), "end_date": mkDt("2030-01-13")},
    )
    assert response.status_code == 200
    blocks = response.json()
    assert len(blocks) >= 1
    assert blocks[0]["task_name"] == "Task A"



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
        json={"start_date": mkDt("2030-01-07"), "end_date": mkDt("2030-01-11")},
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
        json={"start_date": mkDt("2030-01-07"), "end_date": mkDt("2030-01-11")},
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
        json={"start_date": mkDt("2030-01-07"), "end_date": mkDt("2030-01-09")},
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
        json={"start_date": mkDt("2030-01-07"), "end_date": mkDt("2030-01-09")},
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
        json={"start_date": mkDt("2030-01-07"), "end_date": mkDt("2030-01-09")},
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
    """Export returns valid .ics file with standard headers."""
    client.post(
        "/api/tasks",
        json={"name": "Export Test", "estimated_duration_minutes": 30},
    )
    client.post(
        "/api/availability",
        json={"day_of_week": 0, "start_minutes": 540, "end_minutes": 1020},
    )
    client.post(
        "/api/schedule",
        json={"start_date": mkDt("2030-01-07"), "end_date": mkDt("2030-01-11")},
    )
    response = client.post(
        "/api/schedule/export",
        json={"start_date": mkDt("2030-01-07"), "end_date": mkDt("2030-01-11")},
    )
    assert response.status_code == 200
    assert "text/calendar" in response.headers.get("content-type", "")
    disposition = response.headers.get("content-disposition", "")
    assert "attachment;" in disposition
    assert "chronos_schedule.ics" in disposition
    content = response.content
    assert b"BEGIN:VCALENDAR" in content
    assert b"END:VCALENDAR" in content


def test_export_ics_round_trip_has_events(client: TestClient):
    """Export can be parsed by icalendar and contains expected event fields."""
    client.post(
        "/api/tasks",
        json={"name": "Calendar Interop", "estimated_duration_minutes": 45},
    )
    client.post(
        "/api/availability",
        json={"day_of_week": 0, "start_minutes": 540, "end_minutes": 1020},
    )
    client.post(
        "/api/schedule",
        json={"start_date": mkDt("2030-01-07"), "end_date": mkDt("2030-01-11")},
    )

    response = client.post(
        "/api/schedule/export",
        json={"start_date": mkDt("2030-01-07"), "end_date": mkDt("2030-01-11")},
    )
    assert response.status_code == 200

    parsed = Calendar.from_ical(response.content)
    events = [component for component in parsed.walk() if component.name == "VEVENT"]
    assert len(events) >= 1
    first = events[0]
    assert "SUMMARY" in first
    assert "DTSTART" in first
    assert "DTEND" in first
    assert "UID" in first
    assert "DTSTAMP" in first


def test_export_ics_uses_crlf_line_endings(client: TestClient):
    """RFC5545-style CRLF line endings help compatibility across calendar clients."""
    client.post(
        "/api/tasks",
        json={"name": "Line Endings", "estimated_duration_minutes": 30},
    )
    client.post(
        "/api/availability",
        json={"day_of_week": 0, "start_minutes": 540, "end_minutes": 1020},
    )
    client.post(
        "/api/schedule",
        json={"start_date": mkDt("2030-01-07"), "end_date": mkDt("2030-01-11")},
    )

    response = client.post(
        "/api/schedule/export",
        json={"start_date": mkDt("2030-01-07"), "end_date": mkDt("2030-01-11")},
    )
    assert response.status_code == 200
    content = response.content
    assert b"\r\n" in content


def test_generate_schedule_respects_earliest_start(client: TestClient):
    """Task should not be scheduled before earliest_start."""
    client.post(
        "/api/tasks",
        json={
            "name": "Earliest Window",
            "estimated_duration_minutes": 60,
            "earliest_start": "2030-01-07T13:00:00",
        },
    )
    client.post(
        "/api/availability",
        json={"day_of_week": 0, "start_minutes": 540, "end_minutes": 1020},
    )

    response = client.post(
        "/api/schedule",
        json={"start_date": mkDt("2030-01-07"), "end_date": mkDt("2030-01-09")},
    )
    assert response.status_code == 200
    blocks = [b for b in response.json() if b["task_name"] == "Earliest Window"]
    assert len(blocks) == 1
    assert blocks[0]["start_time"] >= "2030-01-07T13:00:00"


def test_generate_schedule_skips_task_when_deadline_missed(client: TestClient):
    """Task is not scheduled when every possible slot ends after its deadline."""
    client.post(
        "/api/tasks",
        json={
            "name": "Impossible Deadline",
            "estimated_duration_minutes": 60,
            "deadline": "2030-01-07T08:30:00",
        },
    )
    client.post(
        "/api/tasks",
        json={"name": "Feasible Task", "estimated_duration_minutes": 60},
    )
    client.post(
        "/api/availability",
        json={"day_of_week": 0, "start_minutes": 540, "end_minutes": 660},
    )

    response = client.post(
        "/api/schedule",
        json={"start_date": mkDt("2030-01-07"), "end_date": mkDt("2030-01-09")},
    )
    assert response.status_code == 200
    names = [b["task_name"] for b in response.json()]
    assert "Impossible Deadline" not in names
    assert "Feasible Task" in names


def test_generate_schedule_respects_preferred_time_of_day(client: TestClient):
    """Morning-preference task should be placed before noon when slots exist."""
    client.post(
        "/api/tasks",
        json={
            "name": "Morning Deep Work",
            "estimated_duration_minutes": 60,
            "preferred_time_of_day": "morning",
        },
    )
    client.post(
        "/api/availability",
        json={"day_of_week": 0, "start_minutes": 480, "end_minutes": 1080},
    )

    response = client.post(
        "/api/schedule",
        json={"start_date": mkDt("2030-01-07"), "end_date": mkDt("2030-01-09")},
    )
    assert response.status_code == 200
    blocks = [b for b in response.json() if b["task_name"] == "Morning Deep Work"]
    assert len(blocks) == 1
    start = datetime.fromisoformat(blocks[0]["start_time"])
    assert 6 <= start.hour < 12



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
        json={"start_date": mkDt("2030-01-07"), "end_date": mkDt("2030-01-09")},
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
        json={"start_date": mkDt("2030-01-07"), "end_date": mkDt("2030-01-09")},
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
        json={"start_date": mkDt("2030-01-07"), "end_date": mkDt("2030-01-11")},
    )
    assert response.status_code == 200
    blocks = response.json()
    validateNoOverlap(blocks)
    validateWithinAvailability(blocks, windows)
    validateNoProtectedOverlap(blocks, protected)
    validateMaxContinuousWork(blocks, 60)


def test_move_block_rejected_when_overlapping(client: TestClient):
    """PATCH block with invalid time returns 422."""
    client.post("/api/tasks", json={"name": "A", "estimated_duration_minutes": 60})
    client.post("/api/tasks", json={"name": "B", "estimated_duration_minutes": 60})
    client.post("/api/availability", json={"day_of_week": 0, "start_minutes": 540, "end_minutes": 1020})
    gen = client.post(
        "/api/schedule",
        json={"start_date": mkDt("2030-01-07"), "end_date": mkDt("2030-01-09")},
    )
    blocks = gen.json()
    assert len(blocks) >= 2
    blockA = next(b for b in blocks if b["task_name"] == "A")
    blockB = next(b for b in blocks if b["task_name"] == "B")
    badStart = blockB["start_time"]
    resp = client.patch(f"/api/schedule/blocks/{blockA['id']}", json={"start_time": badStart})
    assert resp.status_code == 422


def test_delete_block_then_get_excludes_it(client: TestClient):
    """DELETE removes a persisted block."""
    client.post("/api/tasks", json={"name": "Only", "estimated_duration_minutes": 30})
    client.post("/api/availability", json={"day_of_week": 0, "start_minutes": 540, "end_minutes": 1020})
    gen = client.post(
        "/api/schedule",
        json={"start_date": mkDt("2030-01-07"), "end_date": mkDt("2030-01-09")},
    )
    blocks = gen.json()
    assert len(blocks) == 1
    bid = blocks[0]["id"]
    delResp = client.delete(f"/api/schedule/blocks/{bid}")
    assert delResp.status_code == 204
    listed = client.get(
        "/api/schedule",
        params={"start_date": mkDt("2030-01-07"), "end_date": mkDt("2030-01-09")},
    )
    assert listed.json() == []
