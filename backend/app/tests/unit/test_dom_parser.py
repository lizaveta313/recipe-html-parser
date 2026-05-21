from app.parser_engine.dom_parser import DomParser
from app.parser_engine.tokenizer import HtmlTokenizer


def parse(html: str):
    tokens = HtmlTokenizer().tokenize(html)
    return DomParser().parse(tokens)


def test_builds_dom_tree_for_simple_html() -> None:
    root, issues = parse("<html><body><p>Hello</p></body></html>")
    html = root.children[0]
    body = html.children[0]
    paragraph = body.children[0]
    assert html.tag == "html"
    assert body.tag == "body"
    assert paragraph.tag == "p"
    assert paragraph.children[0].text == "Hello"
    assert issues == []


def test_preserves_nested_tags() -> None:
    root, _ = parse('<div class="outer"><section><span>Text</span></section></div>')
    div = root.children[0]
    assert div.attributes["class"] == "outer"
    assert div.children[0].tag == "section"
    assert div.children[0].children[0].tag == "span"


def test_handles_text_nodes() -> None:
    root, _ = parse("<p>Hello <strong>world</strong></p>")
    paragraph = root.children[0]
    assert paragraph.children[0].tag == "#text"
    assert paragraph.children[0].text == "Hello"


def test_handles_self_closing_tags() -> None:
    root, issues = parse('<div><img src="/x.jpg"></div>')
    img = root.children[0].children[0]
    assert img.tag == "img"
    assert img.self_closing is True
    assert issues == []


def test_detects_unclosed_tag() -> None:
    _, issues = parse("<div><span>Text")
    assert any(issue.code == "UNCLOSED_TAG" for issue in issues)


def test_detects_extra_closing_tag() -> None:
    _, issues = parse("<div></div></section>")
    assert any(issue.code == "EXTRA_CLOSING_TAG" for issue in issues)


def test_detects_mismatched_nesting() -> None:
    _, issues = parse("<div><p>Text</div>")
    assert any(issue.code == "MISMATCHED_NESTING" for issue in issues)


def test_calculates_dom_depth() -> None:
    root, _ = parse("<html><body><main><article><p>Text</p></article></main></body></html>")
    assert root.max_depth() >= 5

