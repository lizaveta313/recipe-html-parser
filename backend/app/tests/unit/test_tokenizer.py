from app.parser_engine.models import TokenType
from app.parser_engine.tokenizer import HtmlTokenizer


def test_tokenizes_simple_html() -> None:
    tokens = HtmlTokenizer().tokenize("<html><body>Hello</body></html>")
    assert [token.type for token in tokens] == [
        TokenType.OPEN_TAG,
        TokenType.OPEN_TAG,
        TokenType.TEXT,
        TokenType.CLOSE_TAG,
        TokenType.CLOSE_TAG,
    ]
    assert tokens[2].value == "Hello"


def test_tokenizes_attributes() -> None:
    tokens = HtmlTokenizer().tokenize('<a class="link primary" id="x" href="/recepty">Link</a>')
    open_tag = tokens[0]
    assert open_tag.type == TokenType.OPEN_TAG
    assert open_tag.attributes["class"] == "link primary"
    assert open_tag.attributes["id"] == "x"
    assert open_tag.attributes["href"] == "/recepty"


def test_tokenizes_self_closing_img() -> None:
    tokens = HtmlTokenizer().tokenize('<img src="/x.jpg" alt="x">')
    assert tokens[0].type == TokenType.SELF_CLOSING_TAG
    assert tokens[0].value == "img"
    assert tokens[0].attributes["src"] == "/x.jpg"


def test_tokenizes_comments() -> None:
    tokens = HtmlTokenizer().tokenize("<div><!-- note --></div>")
    assert any(token.type == TokenType.COMMENT and "note" in token.value for token in tokens)


def test_tokenizes_doctype() -> None:
    tokens = HtmlTokenizer().tokenize("<!DOCTYPE html><html></html>")
    assert tokens[0].type == TokenType.DOCTYPE
    assert tokens[0].value.lower() == "doctype html"


def test_preserves_line_and_column_position() -> None:
    tokens = HtmlTokenizer().tokenize("<html>\n  <body>Text</body>")
    body = next(token for token in tokens if token.value == "body" and token.type == TokenType.OPEN_TAG)
    assert body.position.line == 2
    assert body.position.column == 3


def test_handles_broken_html_without_crashing() -> None:
    tokens = HtmlTokenizer().tokenize("<div><span")
    assert [token.value for token in tokens] == ["div", "span"]
    assert tokens[-1].type == TokenType.OPEN_TAG

