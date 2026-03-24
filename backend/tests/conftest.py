import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

from app.main import app
from app.db import getSession


@pytest.fixture
def testEngine():
    """In-memory SQLite engine for isolated tests."""
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(eng)
    return eng



@pytest.fixture
def client(testEngine):
    """Test client with DB session override."""
    def overrideGetSession():
        with Session(testEngine) as session:
            yield session

    app.dependency_overrides[getSession] = overrideGetSession
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
