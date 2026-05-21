from fastapi.testclient import TestClient


def mkDt(dateStr: str) -> str:
    return dateStr + "T00:00:00"


def test_empty_availability_seeds_defaults_and_schedules(client: TestClient):
    """With no windows configured, Chronos assumes weekdays 8am–10pm and places work."""
    client.post("/api/tasks", json={"name": "Orphan", "estimated_duration_minutes": 60})
    response = client.post(
        "/api/schedule",
        json={"start_date": mkDt("2030-01-07"), "end_date": mkDt("2030-01-10")}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["blocks"]) >= 1
    assert "Assumed weekdays" in data["summary"] or data["unscheduled"] == []
    avail = client.get("/api/availability")
    assert avail.status_code == 200
    assert len(avail.json()) >= 5


def test_deadline_impossible_diagnostic(client: TestClient):
    client.post(
        "/api/availability",
        json={"day_of_week": 0, "start_minutes": 540, "end_minutes": 660}
    )
    client.post(
        "/api/tasks",
        json={
            "name": "Impossible",
            "estimated_duration_minutes": 60,
            "deadline": "2030-01-07T08:30:00"
        }
    )
    response = client.post(
        "/api/schedule",
        json={"start_date": mkDt("2030-01-07"), "end_date": mkDt("2030-01-09")}
    )
    assert response.status_code == 200
    data = response.json()
    reasons = [u["reason"] for u in data["unscheduled"]]
    assert "deadline_impossible" in reasons or "no_capacity" in reasons
    names = [b["task_name"] for b in data["blocks"]]
    assert "Impossible" not in names


def test_preference_is_soft_not_hard_gate(client: TestClient):
    """Morning preference should still schedule when only afternoon slots exist."""
    client.post(
        "/api/availability",
        json={"day_of_week": 0, "start_minutes": 780, "end_minutes": 1020}  # 13:00-17:00
    )
    client.post(
        "/api/tasks",
        json={
            "name": "Pref Soft",
            "estimated_duration_minutes": 60,
            "preferred_time_of_day": "morning"
        }
    )
    response = client.post(
        "/api/schedule",
        json={"start_date": mkDt("2030-01-07"), "end_date": mkDt("2030-01-09")}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["blocks"]) == 1
    assert data["blocks"][0]["task_name"] == "Pref Soft"


def test_replace_existing_false_skips_regenerate(client: TestClient):
    client.post(
        "/api/availability",
        json={"day_of_week": 0, "start_minutes": 540, "end_minutes": 1020}
    )
    client.post("/api/tasks", json={"name": "Keep", "estimated_duration_minutes": 30})
    first = client.post(
        "/api/schedule",
        json={"start_date": mkDt("2030-01-07"), "end_date": mkDt("2030-01-09"), "replace_existing": True}
    )
    assert first.status_code == 200
    firstBlocks = first.json()["blocks"]
    assert len(firstBlocks) == 1
    blockId = firstBlocks[0]["id"]

    second = client.post(
        "/api/schedule",
        json={"start_date": mkDt("2030-01-07"), "end_date": mkDt("2030-01-09"), "replace_existing": False}
    )
    assert second.status_code == 200
    secondBlocks = second.json()["blocks"]
    assert len(secondBlocks) == 1
    assert secondBlocks[0]["id"] == blockId
    assert "replace_existing=false" in second.json()["summary"]


def test_earliest_start_blocks_diagnostic(client: TestClient):
    client.post(
        "/api/availability",
        json={"day_of_week": 0, "start_minutes": 540, "end_minutes": 600}  # Mon 9-10 only
    )
    client.post(
        "/api/tasks",
        json={
            "name": "Too Late Start",
            "estimated_duration_minutes": 60,
            "earliest_start": "2030-01-07T15:00:00"
        }
    )
    response = client.post(
        "/api/schedule",
        json={"start_date": mkDt("2030-01-07"), "end_date": mkDt("2030-01-08")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["blocks"] == []
    assert data["unscheduled"]
    assert data["unscheduled"][0]["reason"] in ("earliest_start_blocks", "no_capacity", "deadline_impossible")
