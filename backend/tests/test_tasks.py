"""Tests for task API endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_create_task(client: TestClient):
    """Creating a task returns 201 and the task data."""
    response = client.post(
        "/api/tasks",
        json={
            "name": "Study for exam",
            "estimated_duration_minutes": 60,
            "priority": 1,
            "splittable": True,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Study for exam"
    assert data["estimated_duration_minutes"] == 60
    assert data["splittable"] is True
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_list_tasks_empty(client: TestClient):
    """Listing tasks when empty returns []."""
    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_after_create(client: TestClient):
    """Listing tasks returns created tasks."""
    client.post(
        "/api/tasks",
        json={"name": "Task 1", "estimated_duration_minutes": 30},
    )
    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Task 1"


def test_list_tasks_ordering(client: TestClient):
    """List tasks returns newest first."""
    client.post("/api/tasks", json={"name": "First", "estimated_duration_minutes": 10})
    client.post("/api/tasks", json={"name": "Second", "estimated_duration_minutes": 20})
    client.post("/api/tasks", json={"name": "Third", "estimated_duration_minutes": 30})
    response = client.get("/api/tasks")
    assert response.status_code == 200
    names = []
    for t in response.json():
        names.append(t["name"])
    assert names == ["Third", "Second", "First"]


def test_get_task_success(client: TestClient):
    """Get task by ID returns task when it exists."""
    create_resp = client.post(
        "/api/tasks",
        json={"name": "Find me", "estimated_duration_minutes": 45},
    )
    task_id = create_resp.json()["id"]
    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Find me"
    assert response.json()["id"] == task_id


def test_get_task_not_found(client: TestClient):
    """Get task returns 404 when task does not exist."""
    response = client.get("/api/tasks/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_update_task_success(client: TestClient):
    """Update task modifies and returns updated task."""
    create_resp = client.post(
        "/api/tasks",
        json={"name": "Original", "estimated_duration_minutes": 30, "priority": 0},
    )
    task_id = create_resp.json()["id"]
    response = client.put(
        f"/api/tasks/{task_id}",
        json={"name": "Updated", "estimated_duration_minutes": 60, "priority": 2},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated"
    assert data["estimated_duration_minutes"] == 60
    assert data["priority"] == 2


def test_update_task_partial(client: TestClient):
    """Update task with only some fields leaves others unchanged."""
    create_resp = client.post(
        "/api/tasks",
        json={"name": "Original", "estimated_duration_minutes": 45, "splittable": False},
    )
    task_id = create_resp.json()["id"]
    response = client.put(f"/api/tasks/{task_id}", json={"name": "Renamed"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Renamed"
    assert data["estimated_duration_minutes"] == 45
    assert data["splittable"] is False


def test_update_task_not_found(client: TestClient):
    """Update task returns 404 when task does not exist."""
    response = client.put(
        "/api/tasks/99999",
        json={"name": "Does not matter", "estimated_duration_minutes": 10},
    )
    assert response.status_code == 404


def test_delete_task_success(client: TestClient):
    """Delete task removes it and returns 204."""
    create_resp = client.post(
        "/api/tasks",
        json={"name": "To delete", "estimated_duration_minutes": 15},
    )
    task_id = create_resp.json()["id"]
    response = client.delete(f"/api/tasks/{task_id}")
    assert response.status_code == 204
    get_response = client.get(f"/api/tasks/{task_id}")
    assert get_response.status_code == 404


def test_delete_task_not_found(client: TestClient):
    """Delete task returns 404 when task does not exist."""
    response = client.delete("/api/tasks/99999")
    assert response.status_code == 404


def test_task_persistence(client: TestClient):
    """Tasks persist across multiple requests."""
    create_resp = client.post(
        "/api/tasks",
        json={"name": "Persistent", "estimated_duration_minutes": 90},
    )
    task_id = create_resp.json()["id"]
    list_resp = client.get("/api/tasks")
    found = False
    for t in list_resp.json():
        if t["id"] == task_id:
            found = True
            break
    assert found
