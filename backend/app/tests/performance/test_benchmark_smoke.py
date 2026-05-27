from __future__ import annotations

from pathlib import Path

from scripts import benchmark_parser


EXPECTED_FIXTURES = {
    "small_recipe.html",
    "medium_recipe.html",
    "large_recipe.html",
    "broken_html.html",
    "recipe_without_ingredients.html",
    "recipe_without_steps.html",
    "recipe_without_image.html",
    "noisy_html.html",
    "multiple_recipes.html",
    "incomplete_recipe.html",
}


def test_benchmark_fixtures_exist() -> None:
    fixture_dir = benchmark_parser.FIXTURES_DIR
    assert fixture_dir.exists()

    actual_files = {path.name for path in fixture_dir.glob("*.html")}
    assert EXPECTED_FIXTURES.issubset(actual_files)


def test_benchmark_script_is_importable() -> None:
    assert callable(benchmark_parser.benchmark_file)
    assert callable(benchmark_parser.run_full_analysis)


def test_small_recipe_benchmark_smoke() -> None:
    small_fixture = Path(benchmark_parser.FIXTURES_DIR) / "small_recipe.html"

    result = benchmark_parser.benchmark_file(small_fixture)

    assert result["status"] == "OK"
    assert "execution_time_ms" in result
    assert "peak_memory_kb" in result
    assert result["execution_time_ms"] >= 0
    assert result["peak_memory_kb"] > 0
    assert result["ingredients_count"] == 3
    assert result["steps_count"] == 3
