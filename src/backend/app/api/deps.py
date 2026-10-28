"""Зависимости FastAPI: текущий пользователь и проверка роли."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import Role, User

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Требуется авторизация")

    payload = decode_access_token(credentials.credentials)
    if payload is None or "sub" not in payload:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Недействительный токен")

    user = db.query(User).filter(User.email == payload["sub"]).first()
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Пользователь не найден")
    return user


def require_lead(user: User = Depends(get_current_user)) -> User:
    """Действия, доступные только тимлиду: создание доски и удаление задач."""
    if not user.is_lead:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Действие доступно только тимлиду")
    return user


def can_edit_task(user: User, task) -> bool:
    """Тимлид правит любые задачи, разработчик - только назначенные на него."""
    return user.is_lead or task.assignee_id == user.id or task.author_id == user.id


__all__ = ["get_current_user", "require_lead", "can_edit_task", "Role"]
