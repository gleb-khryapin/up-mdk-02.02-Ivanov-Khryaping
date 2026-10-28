# Установка и запуск

## Что нужно установить

| Программа | Версия | Зачем |
|---|---|---|
| Python | 3.11 - 3.13 | серверная часть |
| Node.js | 20 или новее | сборка интерфейса |
| Git | любая | работа с репозиторием |

Python 3.14 и новее пока не подходит: для него нет готовых сборок
библиотеки pydantic, и установка пытается собирать её из исходников.

## Первый запуск

### 1. Серверная часть

```bash
cd src/backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux и macOS

pip install -r requirements.txt
copy .env.example .env          # Windows
# cp .env.example .env          # Linux и macOS

python seed.py                  # демонстрационные данные
python -m uvicorn app.main:app --reload --port 8000
```

Сервер поднимется на `http://127.0.0.1:8000`.
Документация API открывается по адресу `http://127.0.0.1:8000/docs`.

### 2. Интерфейс

В отдельном окне терминала, из корня проекта:

```bash
npm install
npm run dev
```

Приложение откроется по адресу `http://localhost:5173`.

## Учётные записи для входа

| Роль | Почта | Пароль |
|---|---|---|
| Тимлид | lead@teamboard.ru | lead12345 |
| Разработчик | dev@teamboard.ru | dev12345 |

## Запуск тестов

```bash
# тесты серверной части (30 проверок)
src\backend\.venv\Scripts\python -m pytest

# тесты интерфейса (7 проверок)
npm test
```

## Переход на MySQL

Приложение работает через SQLAlchemy, поэтому смена базы не требует
правки кода. Достаточно установить драйвер и заменить строку подключения
в файле `src/backend/.env`:

```bash
pip install pymysql
```

```
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/teamboard
```

При первом запуске таблицы создадутся автоматически.
