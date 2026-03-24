import pytest
from fastapi.testclient import TestClient


def test_create_protected_block(client: TestClient):
    response = client.post(
        "/api/constraints",
        json={
            "constraint_type": "protected_block",
            "day_of_week": 0,
            "start_minutes": 720,
            "end_minutes": 780,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["constraint_type"] == "protected_block"
    assert data["day_of_week"] == 0
    assert data["start_minutes"] == 720
    assert data["end_minutes"] == 780


def test_create_protected_block_missing_fields(client: TestClient):
    response = client.post(
        "/api/constraints",
        json={
            "constraint_type": "protected_block",
            "day_of_week": 0,
        },
    )
    assert response.status_code == 422


def test_create_protected_block_invalid_range(client: TestClient):
    response = client.post(
        "/api/constraints",
        json={
            "constraint_type": "protected_block",
            "day_of_week": 1,
            "start_minutes": 780,
            "end_minutes": 720,
        },
    )
    assert response.status_code == 422


def test_create_max_continuous_work(client: TestClient):
    response = client.post(
        "/api/constraints",
        json={
            "constraint_type": "max_continuous_work",
            "value": 120,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["constraint_type"] == "max_continuous_work"
    assert data["value"] == 120


def test_create_max_continuous_work_missing_value(client: TestClient):
    response = client.post(
        "/api/constraints",
        json={"constraint_type": "max_continuous_work"},
    )
    assert response.status_code == 422


def test_create_max_continuous_work_zero_value(client: TestClient):
    response = client.post(
        "/api/constraints",
        json={"constraint_type": "max_continuous_work", "value": 0},
    )
    assert response.status_code == 422


def test_create_invalid_constraint_type(client: TestClient):
    response = client.post(
        "/api/constraints",
        json={
            "constraint_type": "invalid_type",
            "value": 60,
        },
    )
    assert response.status_code == 422


def test_list_constraints(client: TestClient):
    client.post(
        "/api/constraints",
        json={
            "constraint_type": "protected_block",
            "day_of_week": 2,
            "start_minutes": 720,
            "end_minutes": 780,
        },
    )
    response = client.get("/api/constraints")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_constraint(client: TestClient):
    create_resp = client.post(
        "/api/constraints",
        json={
            "constraint_type": "max_continuous_work",
            "value": 90,
        },
    )
    constraint_id = create_resp.json()["id"]
    response = client.get(f"/api/constraints/{constraint_id}")
    assert response.status_code == 200
    assert response.json()["value"] == 90


def test_get_constraint_not_found(client: TestClient):
    response = client.get("/api/constraints/99999")
    assert response.status_code == 404


def test_update_constraint(client: TestClient):
    create_resp = client.post(
        "/api/constraints",
        json={"constraint_type": "max_continuous_work", "value": 60},
    )
    constraint_id = create_resp.json()["id"]
    response = client.put(
        f"/api/constraints/{constraint_id}",
        json={"value": 120},
    )
    assert response.status_code == 200
    assert response.json()["value"] == 120


def test_delete_constraint(client: TestClient):
    create_resp = client.post(
        "/api/constraints",
        json={"constraint_type": "max_continuous_work", "value": 45},
    )
    constraint_id = create_resp.json()["id"]
    response = client.delete(f"/api/constraints/{constraint_id}")
    assert response.status_code == 204
    get_resp = client.get(f"/api/constraints/{constraint_id}")
    assert get_resp.status_code == 404
