import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.db import getSession
from app.main import app


@pytest.fixture
def testEngine():
    """In-memory SQLite engine for isolated tests."""
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(eng)
    return eng


@pytest.fixture
def client(testEngine):
    """Authenticated test client with DB session override."""

    def overrideGetSession():
        with Session(testEngine) as session:
            yield session

    app.dependency_overrides[getSession] = overrideGetSession
    with TestClient(app) as c:
        reg = c.post(
            "/api/auth/register",
            json={"email": "tester@chronos.app", "password": "test-pass-123", "name": "Tester"}
        )
        assert reg.status_code == 201, reg.text
        login = c.post(
            "/api/auth/login",
            json={"email": "tester@chronos.app", "password": "test-pass-123"}
        )
        assert login.status_code == 200, login.text
        token = login.json()["access_token"]
        c.headers.update({"Authorization": f"Bearer {token}"})
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def authHeaders(client: TestClient) -> dict:
    """Return Authorization headers already set on client (for explicit use)."""
    return {"Authorization": client.headers["Authorization"]}
