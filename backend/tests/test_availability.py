import pytest
from fastapi.testclient import TestClient


def test_create_availability(client: TestClient):
    response = client.post(
        "/api/availability",
        json={
            "day_of_week": 0,
            "start_minutes": 540,
            "end_minutes": 1020,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["day_of_week"] == 0
    assert data["start_minutes"] == 540
    assert data["end_minutes"] == 1020
    assert "id" in data


def test_create_availability_invalid_range(client: TestClient):
    response = client.post(
        "/api/availability",
        json={
            "day_of_week": 0,
            "start_minutes": 1020,
            "end_minutes": 540,
        },
    )
    assert response.status_code == 422


def test_create_availability_equal_times(client: TestClient):
    response = client.post(
        "/api/availability",
        json={
            "day_of_week": 1,
            "start_minutes": 600,
            "end_minutes": 600,
        },
    )
    assert response.status_code == 422


def test_list_availability_ordering(client: TestClient):
    client.post(
        "/api/availability",
        json={"day_of_week": 2, "start_minutes": 600, "end_minutes": 720},
    )
    client.post(
        "/api/availability",
        json={"day_of_week": 0, "start_minutes": 540, "end_minutes": 1020},
    )
    client.post(
        "/api/availability",
        json={"day_of_week": 2, "start_minutes": 480, "end_minutes": 600},
    )
    response = client.get("/api/availability")
    assert response.status_code == 200
    windows = response.json()
    assert len(windows) == 3
    assert windows[0]["day_of_week"] == 0
    assert windows[1]["day_of_week"] == 2
    assert windows[1]["start_minutes"] == 480
    assert windows[2]["start_minutes"] == 600


def test_get_availability(client: TestClient):
    create_resp = client.post(
        "/api/availability",
        json={"day_of_week": 3, "start_minutes": 540, "end_minutes": 1020},
    )
    window_id = create_resp.json()["id"]
    response = client.get(f"/api/availability/{window_id}")
    assert response.status_code == 200
    assert response.json()["day_of_week"] == 3


def test_get_availability_not_found(client: TestClient):
    response = client.get("/api/availability/99999")
    assert response.status_code == 404


def test_update_availability(client: TestClient):
    create_resp = client.post(
        "/api/availability",
        json={"day_of_week": 4, "start_minutes": 540, "end_minutes": 720},
    )
    window_id = create_resp.json()["id"]
    response = client.put(
        f"/api/availability/{window_id}",
        json={"end_minutes": 900},
    )
    assert response.status_code == 200
    assert response.json()["end_minutes"] == 900


def test_update_availability_invalid(client: TestClient):
    create_resp = client.post(
        "/api/availability",
        json={"day_of_week": 5, "start_minutes": 540, "end_minutes": 720},
    )
    window_id = create_resp.json()["id"]
    response = client.put(
        f"/api/availability/{window_id}",
        json={"start_minutes": 800, "end_minutes": 600},
    )
    assert response.status_code == 422


def test_delete_availability(client: TestClient):
    create_resp = client.post(
        "/api/availability",
        json={"day_of_week": 6, "start_minutes": 600, "end_minutes": 720},
    )
    window_id = create_resp.json()["id"]
    response = client.delete(f"/api/availability/{window_id}")
    assert response.status_code == 204
    get_resp = client.get(f"/api/availability/{window_id}")
    assert get_resp.status_code == 404
