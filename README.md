# Recipe HTML Parser

## Тема работы

Разработка и тестирование синтаксического анализатора для обработки HTML-страниц.

## Описание

Recipe HTML Parser — учебное веб-приложение для анализа HTML-страниц с рецептами сайта `eda.rambler.ru`. Проект принимает ссылку на рецепт или готовый HTML-код, извлекает название, ингредиенты, шаги приготовления, время, изображение и дополнительные данные.

В проекте есть отдельный parser engine:

- tokenizer;
- DOM parser;
- recipe extractor;
- HTML analyzer.

## Что умеет проект

- анализировать URL рецепта с `eda.rambler.ru/recepty`;
- анализировать вставленный HTML-код;
- извлекать данные рецепта;
- находить ошибки и предупреждения в HTML;
- сохранять отчеты;
- показывать историю отчетов;
- запускать тесты parser engine и API.

## Стек технологий

Backend:

- Python;
- FastAPI;
- SQLAlchemy;
- pytest.

Frontend:

- Next.js;
- TypeScript;
- React.

Database:

- SQLite для простого локального запуска;
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
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── tests/
│   ├── Dockerfile
│   └── package.json
├── docs/
├── docker-compose.yml
└── README.md
```

## Как запустить проект

### Вариант 1. Через Docker

Из корня проекта:

```bash
docker compose up --build
```

После запуска:

- frontend: http://localhost:3000
- backend: http://localhost:8000
- Swagger: http://localhost:8000/docs
- PostgreSQL: localhost:5432

В Docker база PostgreSQL поднимается автоматически. Таблица отчетов создается при старте backend.

### Вариант 2. Локально

Backend:

```bash
cd backend
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Установка зависимостей и запуск:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend будет доступен по адресу http://localhost:8000, Swagger — http://localhost:8000/docs, health endpoint — http://localhost:8000/api/health.

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Frontend будет доступен по адресу http://localhost:3000.

При локальном запуске backend по умолчанию использует SQLite:

```env
DATABASE_URL=sqlite:///./recipe_parser.db
```

Если нужен PostgreSQL локально, можно указать свой `DATABASE_URL` в файле `backend/.env`.

## Переменные окружения

Примеры есть в `.env.example`, `backend/.env.example` и `frontend/.env.example`.

Основные переменные:

- `DATABASE_URL` — строка подключения к базе данных;
- `FRONTEND_URL` — адрес frontend для CORS;
- `NEXT_PUBLIC_API_URL` — адрес backend для frontend;
- `AUTO_CREATE_TABLES` — автоматическое создание таблиц при старте backend.

## Как пользоваться

1. Открыть http://localhost:3000.
2. Выбрать режим URL или HTML.
3. Вставить ссылку на рецепт `eda.rambler.ru` или HTML-код.
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

Короткий пример:

```bash
curl -X POST http://localhost:8000/api/parse/html \
  -H "Content-Type: application/json" \
  -d "{\"html\":\"<html><body><h1>Рецепт</h1></body></html>\",\"source_name\":\"manual test\"}"
```

## Тестирование

Backend:

```bash
cd backend
pytest
```

С покрытием:

```bash
pytest --cov=app --cov-report=term-missing
```

Тестами проверяются:

- токенизация HTML;
- построение DOM;
- извлечение рецептов;
- анализ ошибок;
- API для анализа и отчетов.

Если нужно проверить frontend:

```bash
cd frontend
npm test
```

## Итог

В результате был разработан parser для HTML-страниц рецептов. В проекте реализованы извлечение данных, анализ ошибок, сохранение отчетов, просмотр истории и автоматические тесты backend-части.
