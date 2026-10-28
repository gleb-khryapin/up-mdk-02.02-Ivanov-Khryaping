"""Точка входа серверной части TeamBoard."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, boards
from app.core.config import settings
from app.core.database import Base, engine
from app.models import Board, Column, Task, User  # noqa: F401  - нужны для создания таблиц


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="TeamBoard API",
    description="Kanban-доска для студенческой команды. Учебный проект по МДК 02.02.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(boards.router, prefix="/api")


@app.get("/api/health", tags=["Служебные"])
def health() -> dict[str, str]:
    """Проверка, что сервер отвечает."""
    return {"status": "ok"}
