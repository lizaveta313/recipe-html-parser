from app.parser_engine.dom_parser import DomParser
from app.parser_engine.html_analyzer import HtmlAnalyzer
from app.parser_engine.recipe_extractor import RecipeExtractor
from app.parser_engine.tokenizer import HtmlTokenizer


def run_analysis(html: str):
    tokenizer = HtmlTokenizer()
    tokens = tokenizer.tokenize(html)
    dom_root, dom_issues = DomParser().parse(tokens)
    recipe, trace = RecipeExtractor().extract(html)
    return HtmlAnalyzer().analyze(html, tokens, dom_root, dom_issues, recipe, trace)


def test_finds_missing_title() -> None:
    _, errors, _, _ = run_analysis("<html><body><ul><li>Мука 200 г</li></ul></body></html>")
    assert any(issue.code == "MISSING_TITLE" for issue in errors)


def test_finds_missing_ingredients(fixture_html) -> None:
    _, errors, _, _ = run_analysis(fixture_html("eda_recipe_without_ingredients.html"))
    assert any(issue.code == "MISSING_INGREDIENTS" for issue in errors)


def test_finds_missing_steps() -> None:
    html = "<html><body><h1>Рецепт</h1><h2>Ингредиенты</h2><ul><li>Мука 200 г</li></ul></body></html>"
    _, errors, _, _ = run_analysis(html)
    assert any(issue.code == "MISSING_STEPS" for issue in errors)


def test_finds_img_without_alt() -> None:
    html = '<html><body><h1>Рецепт</h1><img src="/x.jpg"></body></html>'
    _, errors, _, _ = run_analysis(html)
    assert any(issue.code == "IMAGE_ALT_MISSING" for issue in errors)


def test_finds_empty_href() -> None:
    html = '<html><body><h1>Рецепт</h1><a href="">empty</a></body></html>'
    _, errors, _, _ = run_analysis(html)
    assert any(issue.code == "EMPTY_LINK_HREF" for issue in errors)


def test_finds_duplicate_id() -> None:
    html = '<html><body><div id="x"></div><section id="x"></section></body></html>'
    _, errors, _, _ = run_analysis(html)
    assert any(issue.code == "DUPLICATE_ID" for issue in errors)


def test_calculates_metrics(fixture_html) -> None:
    metrics, _, _, _ = run_analysis(fixture_html("eda_recipe_valid.html"))
    assert metrics.total_tags > 20
    assert metrics.unique_tags >= 10
    assert metrics.max_dom_depth >= 5
    assert metrics.tokens_count > 30


def test_calculates_scores(fixture_html) -> None:
    _, _, _, scores = run_analysis(fixture_html("eda_recipe_valid.html"))
    assert scores.recipe_completeness_score == 100
    assert scores.parser_confidence_score >= 80
