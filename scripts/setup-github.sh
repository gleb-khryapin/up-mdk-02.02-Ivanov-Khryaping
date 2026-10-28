#!/usr/bin/env bash
# Создаёт метки, задачи (issues) и переносит их на канбан-доску проекта.
#
# Перед запуском:
#   1) установить GitHub CLI:  winget install GitHub.cli
#   2) войти в аккаунт:        gh auth login
#   3) создать проект на GitHub: вкладка Projects -> New project -> Board
#
# Запуск:  bash scripts/setup-github.sh <номер_проекта>
# Номер проекта виден в адресе доски: github.com/users/<логин>/projects/<номер>

set -e

OWNER="gleb-khryapin"
REPO="gleb-khryapin/up-mdk-02.02-Ivanov-Khryaping"
PROJECT_NUMBER="${1:-}"

# GitHub CLI может быть установлен, но отсутствовать в PATH текущего окна
if ! command -v gh >/dev/null 2>&1; then
  for candidate in "/c/Program Files/GitHub CLI/gh.exe" "/c/Program Files (x86)/GitHub CLI/gh.exe"; do
    if [ -x "$candidate" ]; then
      PATH="$PATH:$(dirname "$candidate")"
      break
    fi
  done
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI не найден. Установите: winget install GitHub.cli"
  echo "Если он уже установлен, перезапустите терминал."
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "Вы не вошли в GitHub. Выполните команду: gh auth login"
  exit 1
fi

echo "== Создание меток =="
create_label () {
  gh label create "$1" --repo "$REPO" --color "$2" --description "$3" --force >/dev/null 2>&1 \
    && echo "  метка $1"
}

create_label "backend"     "1d76db" "Серверная часть"
create_label "frontend"    "5319e7" "Интерфейс"
create_label "tests"       "0e8a16" "Тестирование"
create_label "docs"        "d4c5f9" "Документация"
create_label "приоритет: высокий" "d93f0b" "Высокий приоритет"
create_label "приоритет: средний" "fbca04" "Средний приоритет"
create_label "приоритет: низкий"  "c2e0c6" "Низкий приоритет"

echo "== Создание задач =="
ISSUE_URLS=()

new_issue () {
  local title="$1"; local body="$2"; local labels="$3"
  local url
  url=$(gh issue create --repo "$REPO" --title "$title" --body "$body" --label "$labels")
  ISSUE_URLS+=("$url")
  echo "  $title"
}

# --- первый цикл разработки ---
new_issue "Структура проекта, README и .gitignore" \
"Развернуть базовую структуру: папки src, tests, docs. Добавить описание проекта и список игнорируемых файлов.

Ветка: chore/project-structure
Оценка: 1 ч
Статус: выполнено" \
"docs,приоритет: высокий"

new_issue "Модели данных и схема базы" \
"Описать таблицы: пользователь, доска, колонка, задача. Настроить подключение через SQLAlchemy.

Ветка: feat/db-models
Оценка: 3 ч
Статус: выполнено" \
"backend,приоритет: высокий"

new_issue "Регистрация и вход по JWT" \
"Реализовать регистрацию, вход, выпуск токена и проверку роли пользователя. Пароли хранить в виде хеша bcrypt.

Ветка: feat/auth-jwt
Оценка: 4 ч
Статус: выполнено" \
"backend,приоритет: высокий"

new_issue "API досок и задач с разграничением прав" \
"Эндпоинты создания доски, задач, переноса карточек и удаления. Проверка прав: разработчик не создаёт доски, не назначает задачи другим и не удаляет карточки.

Ветка: feat/tasks-api
Оценка: 5 ч
Статус: выполнено" \
"backend,приоритет: высокий"

new_issue "Интерфейс доски с перетаскиванием карточек" \
"Пять колонок, карточки с приоритетом и исполнителем, перенос мышью, фильтр своих задач.

Ветка: feat/board-ui
Оценка: 6 ч
Статус: выполнено" \
"frontend,приоритет: высокий"

new_issue "Автотесты API и интерфейса" \
"30 проверок серверной части и 7 проверок компонентов интерфейса.

Ветка: test/autotests
Оценка: 4 ч
Статус: выполнено" \
"tests,приоритет: высокий"

# --- бэклог на развитие ---
new_issue "Комментарии к задачам" \
"Обсуждение прямо в карточке: добавление, просмотр и удаление комментариев." \
"backend,frontend,приоритет: средний"

new_issue "История изменений задачи" \
"Фиксировать, кто и когда менял статус, исполнителя и приоритет." \
"backend,приоритет: низкий"

new_issue "Фильтр по исполнителю и приоритету" \
"Расширить текущий фильтр: выбор участника и уровня приоритета." \
"frontend,приоритет: средний"

new_issue "Экспорт доски в CSV" \
"Выгрузка списка задач для отчёта по практике." \
"backend,приоритет: низкий"

new_issue "Поддержка нескольких досок" \
"Сейчас команда работает с одной доской, нужен выбор доски." \
"backend,frontend,приоритет: низкий"

new_issue "Уведомления о назначении задачи" \
"Сообщение участнику, когда на него назначили задачу." \
"backend,приоритет: низкий"

if [ -z "$PROJECT_NUMBER" ]; then
  echo
  echo "Задачи созданы. Номер проекта не указан, карточки на доску не перенесены."
  echo "Доски аккаунта:"
  gh project list --owner "$OWNER" 2>/dev/null || echo "  (создайте доску: Projects -> New project -> Board)"
  echo
  echo "Затем выполните: bash scripts/setup-github.sh <номер_проекта>"
  exit 0
fi

echo "== Перенос задач на доску $PROJECT_NUMBER =="
for url in "${ISSUE_URLS[@]}"; do
  gh project item-add "$PROJECT_NUMBER" --owner "$OWNER" --url "$url" >/dev/null
  echo "  добавлено: $url"
done

echo
echo "Готово. Откройте доску и распределите карточки по колонкам."
