# Тестирование

## Что проверяется

В проекте основной упор сделан на backend-тесты, потому что там находится parser engine.

Проверяются:

- токенизация простого и поврежденного HTML;
- чтение атрибутов тегов;
- построение DOM-дерева;
- поиск незакрытых и лишних тегов;
- извлечение рецепта из JSON-LD и HTML-разметки;
- поиск ошибок и предупреждений;
- API для анализа HTML, анализа URL и работы с отчетами.

## HTML fixtures

Файлы для тестов лежат в `backend/app/tests/fixtures/`:

- `eda_recipe_valid.html` — полный пример рецепта;
- `eda_recipe_without_image.html` — рецепт без изображения;
- `eda_recipe_without_ingredients.html` — рецепт без ингредиентов;
- `broken_html.html` — HTML с ошибками разметки.

## Запуск backend-тестов

```bash
cd backend
pytest
```

С покрытием:

```bash
pytest --cov=app --cov-report=term-missing
```

## Frontend-тесты

В frontend есть простые component tests на Vitest. Они проверяют форму анализа, карточку рецепта и страницу отчетов.

```bash
cd frontend
npm test
```
