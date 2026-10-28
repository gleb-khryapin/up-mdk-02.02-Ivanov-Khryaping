"""Создание, изменение и проверка данных задач."""
import pytest


def test_create_task_defaults_to_backlog(client, board, lead_headers):
    response = client.post(
        f"/api/boards/{board['id']}/tasks", json={"title": "Новая задача"}, headers=lead_headers
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "backlog"
    assert body["priority"] == "medium"
    assert body["position"] == 0


@pytest.mark.parametrize(
    "payload",
    [
        {"title": "ab"},
        {"title": ""},
        {"title": "Корректная задача", "estimate_hours": -5},
        {"title": "Корректная задача", "status": "unknown_status"},
        {"title": "Корректная задача", "priority": "urgent"},
    ],
)
def test_invalid_payload_is_rejected(client, board, lead_headers, payload):
    response = client.post(f"/api/boards/{board['id']}/tasks", json=payload, headers=lead_headers)
    assert response.status_code == 422


def test_positions_increase_within_column(client, board, lead_headers):
    positions = []
    for number in range(3):
        task = client.post(
            f"/api/boards/{board['id']}/tasks",
            json={"title": f"Задача номер {number}"},
            headers=lead_headers,
        ).json()
        positions.append(task["position"])
    assert positions == [0, 1, 2]


def test_update_changes_only_sent_fields(client, board, lead_headers):
    task = client.post(
        f"/api/boards/{board['id']}/tasks",
        json={"title": "Исходное название", "description": "описание"},
        headers=lead_headers,
    ).json()

    updated = client.patch(
        f"/api/boards/{board['id']}/tasks/{task['id']}",
        json={"title": "Новое название"},
        headers=lead_headers,
    ).json()

    assert updated["title"] == "Новое название"
    assert updated["description"] == "описание"


def test_missing_task_returns_404(client, board, lead_headers):
    response = client.patch(
        f"/api/boards/{board['id']}/tasks/9999", json={"title": "Нет такой"}, headers=lead_headers
    )
    assert response.status_code == 404


def test_missing_board_returns_404(client, lead_headers):
    assert client.get("/api/boards/4242", headers=lead_headers).status_code == 404
