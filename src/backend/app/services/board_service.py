"""Операции с колонками и порядком карточек."""
from sqlalchemy.orm import Session

from app.models.board import Column, Task, TaskStatus

DEFAULT_COLUMNS = [
    (TaskStatus.BACKLOG, "Бэклог", None),
    (TaskStatus.TODO, "К выполнению", None),
    (TaskStatus.IN_PROGRESS, "В работе", 3),
    (TaskStatus.REVIEW, "На проверке", None),
    (TaskStatus.DONE, "Готово", None),
]


def create_default_columns(db: Session, board_id: int) -> None:
    """Колонки создаются сразу вместе с доской согласно заданию практики."""
    for position, (status, title, wip) in enumerate(DEFAULT_COLUMNS):
        db.add(Column(board_id=board_id, status=status, title=title, position=position, wip_limit=wip))


def next_position(db: Session, board_id: int, status: TaskStatus) -> int:
    return db.query(Task).filter(Task.board_id == board_id, Task.status == status).count()


def reorder_column(
    db: Session,
    board_id: int,
    status: TaskStatus,
    moved_task_id: int | None = None,
    target_position: int = 0,
) -> None:
    """Пересчитывает позиции карточек в колонке, чтобы они шли подряд без пропусков."""
    tasks = (
        db.query(Task)
        .filter(Task.board_id == board_id, Task.status == status)
        .order_by(Task.position, Task.id)
        .all()
    )

    if moved_task_id is not None:
        moved = next((t for t in tasks if t.id == moved_task_id), None)
        if moved is not None:
            tasks.remove(moved)
            target_position = max(0, min(target_position, len(tasks)))
            tasks.insert(target_position, moved)

    for index, task in enumerate(tasks):
        task.position = index
