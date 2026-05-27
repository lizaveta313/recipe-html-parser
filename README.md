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
.venv\Scripts\python.exe -m pytest
```

Фактический результат последнего прогона:

| Часть проекта | Команда | Сколько проверок | Результат |
| --- | --- | ---: | --- |
| Backend | `.venv\Scripts\python.exe -m pytest` | 43 теста | 43 passed |
| Frontend | `npm.cmd test` | 8 тестов в 3 файлах | 8 passed |


### Команды запуска

```bash
cd backend
python scripts/benchmark_parser.py
```

После запуска создаются файлы:

- `backend/reports/benchmark_results.csv`
- `backend/reports/benchmark_report.md`
- `docs/performance-report.md`

### Итоги автоматических проверок

| Проверка | Что запускается | Выход | Статус |
| --- | --- | --- | --- |
| Backend tests | unit, integration и performance smoke tests | `collected 43 items`, `43 passed in 2.35s` | Пройдено |
| Frontend tests | Vitest component tests | `Test Files 3 passed`, `Tests 8 passed` | Пройдено |
| Benchmark | 10 HTML-фикстур из `backend/app/tests/fixtures/performance/` | `Benchmark finished for 10 cases`, `OK: 10`, `ERROR: 0` | Пройдено |

### Ручные проверки API

Ручные сценарии запускались через API-слой приложения на тестовой SQLite-базе. Ошибочные входные данные считаются пройденными, если API возвращает ожидаемый код ошибки и понятное сообщение.

| Сценарий | HTTP | Ключевой выход программы | Статус |
| --- | ---: | --- | --- |
| `GET /api/health` | 200 | `{"status":"ok","service":"recipe-html-parser"}` | Пройдено |
| `POST /api/parse/html`, валидный рецепт | 200 | название: `Паста с томатами и базиликом`; ингредиенты: 5; шаги: 3; ошибки: 0; предупреждения: 0 | Пройдено |
| `POST /api/parse/html`, поврежденный HTML | 200 | название: `Сломанный рецепт`; ошибки: 4; предупреждения: 6; первая ошибка: `MISMATCHED_NESTING` | Пройдено |
| `POST /api/parse/html`, пустой HTML | 422 | `Invalid request data`, причина: `string_too_short` | Пройдено |
| `POST /api/parse/url`, чужой домен | 400 | `Only https://eda.rambler.ru/recepty/... pages are allowed.` | Пройдено |
| `GET /api/reports` после ручного парсинга | 200 | `reports_count: 2` | Пройдено |

### Таблица benchmark

| Файл | Размер HTML, KB | Время, ms | Память, KB | Токены | Ингредиенты | Шаги | Ошибки | Статус |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `broken_html.html` | 0.85 | 72.34 | 368.63 | 42 | 7 | 3 | 7 | OK |
| `incomplete_recipe.html` | 0.63 | 19.61 | 95.10 | 32 | 3 | 0 | 3 | OK |
| `large_recipe.html` | 10.09 | 65.10 | 798.08 | 378 | 40 | 25 | 1 | OK |
| `medium_recipe.html` | 4.30 | 24.24 | 307.19 | 134 | 12 | 9 | 0 | OK |
| `multiple_recipes.html` | 2.71 | 20.61 | 139.61 | 74 | 4 | 3 | 0 | OK |
| `noisy_html.html` | 3.56 | 36.76 | 331.48 | 173 | 6 | 4 | 0 | OK |
| `recipe_without_image.html` | 1.63 | 30.42 | 120.69 | 49 | 5 | 3 | 1 | OK |
| `recipe_without_ingredients.html` | 1.39 | 22.71 | 89.80 | 33 | 0 | 3 | 1 | OK |
| `recipe_without_steps.html` | 1.19 | 29.41 | 100.53 | 39 | 5 | 0 | 1 | OK |
| `small_recipe.html` | 1.64 | 14.18 | 107.93 | 44 | 3 | 3 | 0 | OK |

С покрытием backend можно запустить отдельно:

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
npm.cmd test
```

## Итог

В результате был разработан parser для HTML-страниц рецептов. В проекте реализованы извлечение данных, анализ ошибок, сохранение отчетов, просмотр истории и автоматические тесты backend-части.
