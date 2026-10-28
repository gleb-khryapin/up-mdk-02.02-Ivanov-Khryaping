"""Схемы запросов и ответов. Pydantic проверяет данные до попадания в бизнес-логику."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.board import Priority, TaskStatus
from app.models.user import Role


# --- пользователи ---
class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)
    password: str = Field(min_length=6, max_length=128)
    role: Role = Role.DEVELOPER


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    role: Role


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# --- задачи ---
class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str = ""
    status: TaskStatus = TaskStatus.BACKLOG
    priority: Priority = Priority.MEDIUM
    assignee_id: int | None = None
    branch: str | None = Field(default=None, max_length=255)
    estimate_hours: float | None = Field(default=None, ge=0, le=1000)


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=255)
    description: str | None = None
    status: TaskStatus | None = None
    priority: Priority | None = None
    assignee_id: int | None = None
    branch: str | None = None
    estimate_hours: float | None = Field(default=None, ge=0, le=1000)
    position: int | None = None


class TaskMove(BaseModel):
    """Перенос карточки в другую колонку."""

    status: TaskStatus
    position: int = 0


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    board_id: int
    title: str
    description: str
    status: TaskStatus
    priority: Priority
    position: int
    author_id: int
    assignee_id: int | None
    branch: str | None
    estimate_hours: float | None
    created_at: datetime
    updated_at: datetime
    assignee: UserOut | None = None


# --- доски ---
class BoardCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str = ""


class BoardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    owner_id: int


class ColumnOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: TaskStatus
    title: str
    position: int
    wip_limit: int | None


class BoardDetail(BoardOut):
    columns: list[ColumnOut]
    tasks: list[TaskOut]
