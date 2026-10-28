"""Правила доски: перенос карточек, лимит задач в работе, порядок карточек."""


def _create(client, board, headers, title, status="backlog"):
    return client.post(
        f"/api/boards/{board['id']}/tasks",
        json={"title": title, "status": status},
        headers=headers,
    ).json()


def _move(client, board, headers, task_id, status, position=0):
    return client.patch(
        f"/api/boards/{board['id']}/tasks/{task_id}/move",
        json={"status": status, "position": position},
        headers=headers,
    )


def test_move_changes_status(client, board, lead_headers):
    task = _create(client, board, lead_headers, "Задача к переносу")
    response = _move(client, board, lead_headers, task["id"], "todo")
    assert response.status_code == 200
    assert response.json()["status"] == "todo"


def test_wip_limit_blocks_fourth_task(client, board, lead_headers):
    """В колонке «В работе» лимит 3 задачи - четвёртая не должна проходить."""
    for number in range(3):
        task = _create(client, board, lead_headers, f"Задача {number}")
        assert _move(client, board, lead_headers, task["id"], "in_progress").status_code == 200

    extra = _create(client, board, lead_headers, "Лишняя задача")
    response = _move(client, board, lead_headers, extra["id"], "in_progress")
    assert response.status_code == 409
    assert "лимит" in response.json()["detail"].lower()


def test_task_stays_in_old_column_after_limit_error(client, board, lead_headers):
    for number in range(3):
        task = _create(client, board, lead_headers, f"Занимает место {number}")
        _move(client, board, lead_headers, task["id"], "in_progress")

    extra = _create(client, board, lead_headers, "Не пройдёт")
    _move(client, board, lead_headers, extra["id"], "in_progress")

    detail = client.get(f"/api/boards/{board['id']}", headers=lead_headers).json()
    stored = next(t for t in detail["tasks"] if t["id"] == extra["id"])
    assert stored["status"] == "backlog"


def test_positions_are_recalculated_after_move(client, board, lead_headers):
    tasks = [_create(client, board, lead_headers, f"Карточка {n}") for n in range(3)]
    _move(client, board, lead_headers, tasks[0]["id"], "todo")

    detail = client.get(f"/api/boards/{board['id']}", headers=lead_headers).json()
    backlog = sorted(
        [t for t in detail["tasks"] if t["status"] == "backlog"], key=lambda t: t["position"]
    )
    assert [t["position"] for t in backlog] == [0, 1]


def test_move_to_specific_position(client, board, lead_headers):
    first = _create(client, board, lead_headers, "Первая", status="todo")
    second = _create(client, board, lead_headers, "Вторая", status="todo")
    _move(client, board, lead_headers, second["id"], "todo", position=0)

    detail = client.get(f"/api/boards/{board['id']}", headers=lead_headers).json()
    todo = sorted([t for t in detail["tasks"] if t["status"] == "todo"], key=lambda t: t["position"])
    assert [t["title"] for t in todo] == ["Вторая", "Первая"]


def test_developer_cannot_move_foreign_task(client, board, lead_headers, dev_headers, lead):
    task = client.post(
        f"/api/boards/{board['id']}/tasks",
        json={"title": "Чужая задача", "assignee_id": lead["user"]["id"]},
        headers=lead_headers,
    ).json()

    assert _move(client, board, dev_headers, task["id"], "todo").status_code == 403


def test_developer_can_move_own_task(client, board, lead_headers, dev_headers, developer):
    task = client.post(
        f"/api/boards/{board['id']}/tasks",
        json={"title": "Задача разработчика", "assignee_id": developer["user"]["id"]},
        headers=lead_headers,
    ).json()

    assert _move(client, board, dev_headers, task["id"], "in_progress").status_code == 200
