"""Проверки регистрации, входа и защиты эндпоинтов."""


def test_register_returns_token_and_user(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "new@teamboard.ru",
            "full_name": "Новый участник",
            "password": "secret123",
            "role": "developer",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == "new@teamboard.ru"
    assert "password" not in body["user"]


def test_duplicate_email_is_rejected(client, lead):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "lead@teamboard.ru",
            "full_name": "Двойник",
            "password": "secret123",
            "role": "developer",
        },
    )
    assert response.status_code == 409


def test_short_password_is_rejected(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "a@teamboard.ru", "full_name": "Тест", "password": "123", "role": "developer"},
    )
    assert response.status_code == 422


def test_login_with_correct_password(client, lead):
    response = client.post(
        "/api/auth/login", json={"email": "lead@teamboard.ru", "password": "lead12345"}
    )
    assert response.status_code == 200
    assert response.json()["user"]["role"] == "lead"


def test_login_with_wrong_password(client, lead):
    response = client.post(
        "/api/auth/login", json={"email": "lead@teamboard.ru", "password": "wrong-password"}
    )
    assert response.status_code == 401


def test_protected_endpoint_requires_token(client):
    assert client.get("/api/auth/me").status_code == 401


def test_forged_token_is_rejected(client):
    headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.fake-payload.invalid-signature"}
    assert client.get("/api/auth/me", headers=headers).status_code == 401
