"""Разграничение прав между тимлидом и разработчиком."""


def test_developer_cannot_create_board(client, dev_headers):
    response = client.post("/api/boards", json={"title": "Своя доска"}, headers=dev_headers)
    assert response.status_code == 403


def test_lead_creates_board_with_five_columns(client, lead_headers):
    board = client.post("/api/boards", json={"title": "Доска команды"}, headers=lead_headers).json()
    detail = client.get(f"/api/boards/{board['id']}", headers=lead_headers).json()
    statuses = [c["status"] for c in detail["columns"]]
    assert statuses == ["backlog", "todo", "in_progress", "review", "done"]


def test_developer_cannot_assign_task_to_other_user(client, board, dev_headers, lead):
    response = client.post(
        f"/api/boards/{board['id']}/tasks",
        json={"title": "Задача для тимлида", "assignee_id": lead["user"]["id"]},
        headers=dev_headers,
    )
    assert response.status_code == 403


def test_developer_can_create_task_for_himself(client, board, dev_headers, developer):
    response = client.post(
        f"/api/boards/{board['id']}/tasks",
        json={"title": "Моя задача", "assignee_id": developer["user"]["id"]},
        headers=dev_headers,
    )
    assert response.status_code == 201
    assert response.json()["assignee_id"] == developer["user"]["id"]


def test_developer_cannot_edit_foreign_task(client, board, lead_headers, dev_headers, lead):
    task = client.post(
        f"/api/boards/{board['id']}/tasks",
        json={"title": "Задача тимлида", "assignee_id": lead["user"]["id"]},
        headers=lead_headers,
    ).json()

    response = client.patch(
        f"/api/boards/{board['id']}/tasks/{task['id']}",
        json={"title": "Переименовал чужую"},
        headers=dev_headers,
    )
    assert response.status_code == 403


def test_developer_cannot_delete_task(client, board, lead_headers, dev_headers):
    task = client.post(
        f"/api/boards/{board['id']}/tasks", json={"title": "Удаляемая задача"}, headers=lead_headers
    ).json()

    assert client.delete(
        f"/api/boards/{board['id']}/tasks/{task['id']}", headers=dev_headers
    ).status_code == 403
    assert client.delete(
        f"/api/boards/{board['id']}/tasks/{task['id']}", headers=lead_headers
    ).status_code == 204
