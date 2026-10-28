"""Доски и задачи."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import can_edit_task, get_current_user, require_lead
from app.core.database import get_db
from app.models.board import Board, Column, Task
from app.models.user import User
from app.schemas.schemas import (
    BoardCreate,
    BoardDetail,
    BoardOut,
    ColumnOut,
    TaskCreate,
    TaskMove,
    TaskOut,
    TaskUpdate,
)
from app.services.board_service import create_default_columns, next_position, reorder_column

router = APIRouter(prefix="/boards", tags=["Доски"])


def _get_board(db: Session, board_id: int) -> Board:
    board = db.get(Board, board_id)
    if board is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Доска не найдена")
    return board


def _get_task(db: Session, board_id: int, task_id: int) -> Task:
    task = db.get(Task, task_id)
    if task is None or task.board_id != board_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Задача не найдена")
    return task


@router.get("", response_model=list[BoardOut])
def list_boards(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return [BoardOut.model_validate(b) for b in db.query(Board).order_by(Board.id).all()]


@router.post("", response_model=BoardOut, status_code=status.HTTP_201_CREATED)
def create_board(data: BoardCreate, db: Session = Depends(get_db), user: User = Depends(require_lead)):
    """Создание доски. Доступно только тимлиду."""
    board = Board(title=data.title, description=data.description, owner_id=user.id)
    db.add(board)
    db.flush()
    create_default_columns(db, board.id)
    db.commit()
    db.refresh(board)
    return BoardOut.model_validate(board)


@router.get("/{board_id}", response_model=BoardDetail)
def get_board(board_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """Доска со всеми колонками и задачами - основной запрос интерфейса."""
    board = _get_board(db, board_id)
    columns = db.query(Column).filter(Column.board_id == board_id).order_by(Column.position).all()
    tasks = db.query(Task).filter(Task.board_id == board_id).order_by(Task.status, Task.position).all()
    return BoardDetail(
        id=board.id,
        title=board.title,
        description=board.description,
        owner_id=board.owner_id,
        columns=[ColumnOut.model_validate(c) for c in columns],
        tasks=[TaskOut.model_validate(t) for t in tasks],
    )


@router.post("/{board_id}/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    board_id: int,
    data: TaskCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Создать задачу. Разработчик может ставить задачи только на себя."""
    _get_board(db, board_id)

    if not user.is_lead and data.assignee_id not in (None, user.id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Назначать задачи другим может только тимлид")

    task = Task(
        board_id=board_id,
        title=data.title,
        description=data.description,
        status=data.status,
        priority=data.priority,
        assignee_id=data.assignee_id,
        branch=data.branch,
        estimate_hours=data.estimate_hours,
        author_id=user.id,
        position=next_position(db, board_id, data.status),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return TaskOut.model_validate(task)


@router.patch("/{board_id}/tasks/{task_id}", response_model=TaskOut)
def update_task(
    board_id: int,
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    task = _get_task(db, board_id, task_id)
    if not can_edit_task(user, task):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Нельзя изменять чужую задачу")

    payload = data.model_dump(exclude_unset=True)
    if "assignee_id" in payload and not user.is_lead and payload["assignee_id"] not in (None, user.id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Назначать задачи другим может только тимлид")

    for field, value in payload.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return TaskOut.model_validate(task)


@router.patch("/{board_id}/tasks/{task_id}/move", response_model=TaskOut)
def move_task(
    board_id: int,
    task_id: int,
    data: TaskMove,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Перенос карточки между колонками с учётом лимита задач в работе."""
    task = _get_task(db, board_id, task_id)
    if not can_edit_task(user, task):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Нельзя перемещать чужую задачу")

    column = db.query(Column).filter(Column.board_id == board_id, Column.status == data.status).first()
    if column is not None and column.wip_limit is not None and task.status != data.status:
        in_column = db.query(Task).filter(Task.board_id == board_id, Task.status == data.status).count()
        if in_column >= column.wip_limit:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Превышен лимит задач в колонке " + column.title + ": не больше " + str(column.wip_limit),
            )

    old_status = task.status
    task.status = data.status
    task.position = data.position
    db.flush()
    reorder_column(db, board_id, old_status)
    reorder_column(db, board_id, data.status, moved_task_id=task.id, target_position=data.position)
    db.commit()
    db.refresh(task)
    return TaskOut.model_validate(task)


@router.delete("/{board_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    board_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_lead),
):
    """Удаление задачи. Доступно только тимлиду."""
    task = _get_task(db, board_id, task_id)
    db.delete(task)
    db.commit()
