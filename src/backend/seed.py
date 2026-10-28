"""Наполнение базы демонстрационными данными.

Запуск: python seed.py
Создаёт двух пользователей, доску и несколько задач, чтобы доску
можно было сразу открыть и показать.
"""
from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models.board import Board, Priority, Task, TaskStatus
from app.models.user import Role, User
from app.services.board_service import create_default_columns

DEMO_TASKS = [
    ("Настроить репозиторий и структуру проекта", TaskStatus.DONE, Priority.HIGH, "chore/init-structure"),
    ("Спроектировать схему базы данных", TaskStatus.DONE, Priority.HIGH, "feat/db-schema"),
    ("Реализовать регистрацию и вход по JWT", TaskStatus.REVIEW, Priority.HIGH, "feat/auth-jwt"),
    ("Сделать перетаскивание карточек", TaskStatus.IN_PROGRESS, Priority.MEDIUM, "feat/drag-and-drop"),
    ("Написать тесты API задач", TaskStatus.TODO, Priority.MEDIUM, "test/tasks-api"),
    ("Добавить фильтр задач по исполнителю", TaskStatus.BACKLOG, Priority.LOW, None),
    ("Экспорт доски в CSV", TaskStatus.BACKLOG, Priority.LOW, None),
]


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            print("База уже заполнена, повторное наполнение не требуется")
            return

        lead = User(
            email="lead@teamboard.ru",
            full_name="Хряпин Г. С.",
            password_hash=hash_password("lead12345"),
            role=Role.LEAD,
        )
        dev = User(
            email="dev@teamboard.ru",
            full_name="Иванов В. В.",
            password_hash=hash_password("dev12345"),
            role=Role.DEVELOPER,
        )
        db.add_all([lead, dev])
        db.flush()

        board = Board(
            title="Учебная практика УП.02",
            description="Доска команды по теме «Модуль управления задачами»",
            owner_id=lead.id,
        )
        db.add(board)
        db.flush()
        create_default_columns(db, board.id)

        counters: dict[TaskStatus, int] = {}
        for title, status, priority, branch in DEMO_TASKS:
            position = counters.get(status, 0)
            counters[status] = position + 1
            db.add(
                Task(
                    board_id=board.id,
                    title=title,
                    description="",
                    status=status,
                    priority=priority,
                    position=position,
                    author_id=lead.id,
                    assignee_id=dev.id if status != TaskStatus.BACKLOG else None,
                    branch=branch,
                )
            )

        db.commit()
        print("Готово. Учётные записи для входа:")
        print("  тимлид:      lead@teamboard.ru / lead12345")
        print("  разработчик: dev@teamboard.ru / dev12345")
    finally:
        db.close()


if __name__ == "__main__":
    main()
