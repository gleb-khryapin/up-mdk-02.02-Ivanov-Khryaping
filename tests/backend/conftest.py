"""Общие фикстуры: отдельная база для каждого теста и готовые токены."""
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

BACKEND = Path(__file__).resolve().parents[2] / "src" / "backend"
sys.path.insert(0, str(BACKEND))
os.environ.setdefault("SECRET_KEY", "test-secret")

from app.core.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def db_session():
    """База в оперативной памяти: тесты не трогают рабочий файл и не зависят друг от друга."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _register(client, email, name, password, role):
    response = client.post(
        "/api/auth/register",
        json={"email": email, "full_name": name, "password": password, "role": role},
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture()
def lead(client):
    return _register(client, "lead@teamboard.ru", "Тимлид", "lead12345", "lead")


@pytest.fixture()
def developer(client):
    return _register(client, "dev@teamboard.ru", "Разработчик", "dev12345", "developer")


@pytest.fixture()
def lead_headers(lead):
    return {"Authorization": "Bearer " + lead["access_token"]}


@pytest.fixture()
def dev_headers(developer):
    return {"Authorization": "Bearer " + developer["access_token"]}


@pytest.fixture()
def board(client, lead_headers):
    response = client.post("/api/boards", json={"title": "Учебная доска"}, headers=lead_headers)
    assert response.status_code == 201, response.text
    return response.json()
