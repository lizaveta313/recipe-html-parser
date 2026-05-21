from app.parser_engine.recipe_extractor import RecipeExtractor


def test_extracts_main_recipe_fields(fixture_html) -> None:
    recipe, trace = RecipeExtractor().extract(
        fixture_html("eda_recipe_valid.html"),
        original_url="https://eda.rambler.ru/recepty/pasta/pasta-s-tomatami-i-bazilikom-12345",
    )
    assert recipe.title == "Паста с томатами и базиликом"
    assert recipe.author == "Редакция Еда"
    assert recipe.cooking_time == "35 мин"
    assert recipe.servings == "4 порции"
    assert recipe.image_url == "https://eda.rambler.ru/images/recipe/pasta.jpg"
    assert recipe.rating == "4.8"
    assert recipe.original_url == "https://eda.rambler.ru/recepty/pasta/pasta-s-tomatami-i-bazilikom-12345"
    assert trace.used_json_ld is True


def test_extracts_ingredients_steps_and_nutrition(fixture_html) -> None:
    recipe, _ = RecipeExtractor().extract(fixture_html("eda_recipe_valid.html"))
    assert len(recipe.ingredients) == 5
    assert recipe.ingredients[0].name == "Спагетти"
    assert recipe.ingredients[0].amount == "400"
    assert recipe.ingredients[0].unit == "г"
    assert len(recipe.steps) == 3
    assert recipe.steps[0].step_number == 1
    assert recipe.nutrition is not None
    assert recipe.nutrition.calories == 420
    assert recipe.nutrition.proteins == 12


def test_handles_page_without_image(fixture_html) -> None:
    recipe, _ = RecipeExtractor().extract(fixture_html("eda_recipe_without_image.html"))
    assert recipe.title == "Овощной суп"
    assert recipe.image_url is None


def test_handles_page_without_ingredients(fixture_html) -> None:
    recipe, _ = RecipeExtractor().extract(fixture_html("eda_recipe_without_ingredients.html"))
    assert recipe.title == "Чай с мятой"
    assert recipe.ingredients == []


def test_fallback_without_json_ld() -> None:
    html = """
    <html><body>
      <h1>Сырники</h1>
      <p>Нежные сырники для быстрого завтрака из творога и муки.</p>
      <h2>Ингредиенты</h2>
      <ul><li>Творог 300 г</li><li>Мука 3 ст. л.</li></ul>
      <h2>Инструкция приготовления</h2>
      <ol><li>Смешайте творог с мукой.</li><li>Обжарьте сырники на сковороде.</li></ol>
      <img src="/images/syrniki.jpg" alt="Сырники">
    </body></html>
    """
    recipe, trace = RecipeExtractor().extract(html)
    assert recipe.title == "Сырники"
    assert len(recipe.ingredients) == 2
    assert len(recipe.steps) == 2
    assert recipe.image_url == "https://eda.rambler.ru/images/syrniki.jpg"
    assert trace.used_fallback is True


def test_resolves_relative_links(fixture_html) -> None:
    recipe, _ = RecipeExtractor().extract(fixture_html("eda_recipe_valid.html"))
    assert recipe.image_url.startswith("https://eda.rambler.ru/")
