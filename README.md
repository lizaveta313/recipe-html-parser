# Recipe HTML Parser

Учебное веб-приложение для анализа HTML-страниц с рецептами сайта `eda.rambler.ru`.

Проект принимает URL рецепта или готовый HTML-код, извлекает основные данные рецепта и показывает отчет по найденным данным и ошибкам в разметке.

## Что реализовано

- tokenizer для разбиения HTML на токены;
- простой DOM parser;
- извлечение данных рецепта;
- поиск ошибок и предупреждений в HTML;
- сохранение отчетов в базу данных;
- веб-интерфейс для анализа и просмотра истории отчетов;
- backend- и frontend-тесты.

## Стек

Backend:

- Python;
- FastAPI;
- SQLAlchemy;
- pytest.

Frontend:

- Next.js;
- TypeScript;
- React;
- Vitest.

Database:

- SQLite для локального запуска;
- PostgreSQL при запуске через Docker.

## Структура проекта

```text
recipe-html-parser/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── parser_engine/
│   │   ├── repositories/
│   │   ├── services/
│   │   └── tests/
│   ├── scripts/
│   └── requirements.txt
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── tests/
├── docs/
└── docker-compose.yml
```

## Запуск через Docker

Из корня проекта:

```bash
docker compose up --build
```

После запуска:

- frontend: http://localhost:3000
- backend: http://localhost:8000
- Swagger: http://localhost:8000/docs

В Docker поднимается PostgreSQL. Таблица отчетов создается при старте backend.

## Локальный запуск

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

По умолчанию backend локально использует SQLite:

```env
DATABASE_URL=sqlite:///./recipe_parser.db
```

## Как пользоваться

1. Открыть http://localhost:3000.
2. Выбрать режим URL или HTML.
3. Вставить ссылку на рецепт `eda.rambler.ru/recepty` или HTML-код.
4. Нажать `Analyze`.
5. Посмотреть извлеченные данные, ошибки и предупреждения.
6. Открыть историю отчетов на странице `/reports`.

## API

- `GET /api/health`
- `POST /api/parse/url`
- `POST /api/parse/html`
- `GET /api/reports`
- `GET /api/reports/{id}`
- `DELETE /api/reports/{id}`

## Тестирование

Backend:

```bash
cd backend
.venv\Scripts\python.exe -m pytest
```

Frontend:

```bash
cd frontend
npm.cmd test
```

Последний локальный прогон:

| Часть проекта | Команда | Результат |
| --- | --- | --- |
| Backend | `.venv\Scripts\python.exe -m pytest` | 43 passed |
| Frontend | `npm.cmd test` | 8 passed |

## Дополнительные материалы

- [Описание проекта](docs/project-description.md)
- [Архитектура](docs/architecture.md)
- [Тестирование](docs/testing.md)
- [Отчет по производительности](docs/performance-report.md)

## Ограничения

Проект настроен под страницы рецептов `eda.rambler.ru`. Это не универсальный HTML5 parser для любых сайтов.

Основная учебная часть находится в `backend/app/parser_engine/`: токенизация, построение простого DOM-дерева и анализ ошибок. Для практического извлечения данных рецепта также используются HTML-селекторы и структурированные данные страницы.
