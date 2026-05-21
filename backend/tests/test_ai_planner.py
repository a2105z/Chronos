from datetime import datetime

from app.services.ai.parser import parseDeterministic


def test_parse_deep_work_resume_tomorrow_morning():
    prompt = "Schedule 3 hours of deep work on the Chronos resume tomorrow morning, high priority"
    ref = datetime(2030, 1, 6, 10, 0, 0)
    intent = parseDeterministic(prompt, reference=ref)
    assert len(intent.tasks) == 1
    task = intent.tasks[0]
    assert task.estimated_duration_minutes == 180
    assert task.priority >= 8
    assert task.preferred_time_of_day == "morning"
    assert task.earliest_start is not None
    assert "resume" in task.name.lower() or "chronos" in task.name.lower() or "deep" in task.name.lower()


def test_parse_protect_lunch():
    intent = parseDeterministic("Protect lunch every day from 12 to 1")
    assert intent.constraints
    c = intent.constraints[0]
    assert c.constraint_type == "protected_block"
    assert c.start_minutes == 12 * 60
    assert c.end_minutes == 13 * 60
    assert c.every_weekday is True
    assert intent.tasks == []


def test_parse_weekday_availability():
    intent = parseDeterministic("I'm free weekdays 9am to 5pm")
    assert intent.availability
    a = intent.availability[0]
    assert a.start_minutes == 9 * 60
    assert a.end_minutes == 17 * 60
    assert a.weekdays_only is True
    assert intent.tasks == []


def test_parse_study_before_friday_splittable():
    ref = datetime(2030, 1, 6, 10, 0, 0)  # Monday
    intent = parseDeterministic(
        "Block 90 minutes to study algorithms before Friday, can split",
        reference=ref
    )
    assert len(intent.tasks) == 1
    task = intent.tasks[0]
    assert task.estimated_duration_minutes == 90
    assert task.splittable is True
    assert task.deadline is not None
    assert task.deadline.weekday() == 4


def test_ai_plan_endpoint_deterministic(client):
    start = "2030-01-07T00:00:00"
    end = "2030-01-14T00:00:00"
    # Seed availability first so schedule can place
    for day in range(5):
        client.post(
            "/api/availability",
            json={"day_of_week": day, "start_minutes": 540, "end_minutes": 1020}
        )
    response = client.post(
        "/api/ai/plan",
        json={
            "prompt": "Schedule 2 hours of resume polish tomorrow morning, high priority",
            "start_date": start,
            "end_date": end,
            "apply": True
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["intent"]["parser"] in ("deterministic", "openai")
    assert data["created"]["tasks"]
    createdTask = data["created"]["tasks"][0]
    assert createdTask.get("id") is not None
    assert createdTask.get("name")
    assert "assistant_message" in data
    assert data["schedule"] is not None


def test_ai_explain_endpoint(client):
    client.post(
        "/api/availability",
        json={"day_of_week": 0, "start_minutes": 540, "end_minutes": 1020}
    )
    client.post("/api/tasks", json={"name": "X", "estimated_duration_minutes": 30})
    client.post(
        "/api/schedule",
        json={"start_date": "2030-01-07T00:00:00", "end_date": "2030-01-09T00:00:00"}
    )
    response = client.post(
        "/api/ai/explain",
        json={"start_date": "2030-01-07T00:00:00", "end_date": "2030-01-09T00:00:00"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "blocks" in data
    assert "unscheduled" in data
    assert "summary" in data


def test_ai_suggestions_endpoint(client):
    response = client.get("/api/ai/suggestions")
    assert response.status_code == 200
    assert isinstance(response.json()["suggestions"], list)
    assert len(response.json()["suggestions"]) >= 1

def test_parse_exam_study_stat410():
    from datetime import datetime

    from app.services.ai.parser import parseDeterministic
    ref = datetime(2026, 8, 18, 10, 0, 0)  # Tuesday
    prompt = "I have a test for my STAT 410 class on Thursday at 5-6:30. Block out per day to study for this"
    intent = parseDeterministic(prompt, reference=ref)
    assert intent.constraints
    assert intent.constraints[0].constraint_type == "protected_block"
    assert intent.constraints[0].day_of_week == 3
    assert intent.constraints[0].start_minutes == 17 * 60
    assert intent.constraints[0].end_minutes == 18 * 60 + 30
    assert len(intent.tasks) >= 2
    assert any("STAT" in t.name.upper() or "study" in t.name.lower() for t in intent.tasks)

def test_parse_find_three_two_hour_spots():
    from datetime import datetime

    from app.services.ai.parser import parseDeterministic

    ref = datetime(2026, 8, 18, 10, 0, 0)
    intent = parseDeterministic(
        "Find me 3 spots, each 2 hours long for deep work",
        reference=ref,
    )
    assert len(intent.tasks) == 3
    assert all(t.estimated_duration_minutes == 120 for t in intent.tasks)
    assert all(t.splittable is False for t in intent.tasks)
    assert all("Deep work" in t.name for t in intent.tasks)


def test_parse_four_blocks_of_ninety_minutes():
    from datetime import datetime

    from app.services.ai.parser import parseDeterministic

    ref = datetime(2026, 8, 18, 10, 0, 0)
    intent = parseDeterministic(
        "Schedule 4 blocks of 90 minutes for studying",
        reference=ref,
    )
    assert len(intent.tasks) == 4
    assert all(t.estimated_duration_minutes == 90 for t in intent.tasks)


def test_parse_three_two_hour_sessions():
    from datetime import datetime

    from app.services.ai.parser import parseDeterministic

    ref = datetime(2026, 8, 18, 10, 0, 0)
    intent = parseDeterministic("give me 3 two-hour sessions", reference=ref)
    assert len(intent.tasks) == 3
    assert all(t.estimated_duration_minutes == 120 for t in intent.tasks)


def test_ai_plan_multi_spots_endpoint(client):
    start = "2030-01-07T00:00:00"
    end = "2030-01-14T00:00:00"
    for day in range(5):
        client.post(
            "/api/availability",
            json={"day_of_week": day, "start_minutes": 540, "end_minutes": 1020},
        )
    response = client.post(
        "/api/ai/plan",
        json={
            "prompt": "Find me 3 spots, each 2 hours long for deep work",
            "start_date": start,
            "end_date": end,
            "apply": True,
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert len(body["created"]["tasks"]) >= 3
    assert len(body["intent"]["tasks"]) == 3
    assert all(t["estimated_duration_minutes"] == 120 for t in body["intent"]["tasks"])
