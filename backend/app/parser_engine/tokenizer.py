"""Educational HTML tokenizer.

The tokenizer intentionally implements the lexical stage itself instead of
delegating it to BeautifulSoup/lxml. It is tolerant by design: malformed HTML is
still converted into tokens so the next stage can report structural problems.
"""

from __future__ import annotations

import re

from app.parser_engine.models import HtmlToken, TokenPosition, TokenType


class HtmlTokenizer:
    VOID_TAGS = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }
    ATTR_RE = re.compile(
        r"""([:\w-]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>`]+)))?""",
        re.UNICODE,
    )
    TAG_NAME_RE = re.compile(r"^/?\s*([A-Za-z][A-Za-z0-9:-]*)")

    def tokenize(self, html: str) -> list[HtmlToken]:
        if html is None:
            html = ""

        tokens: list[HtmlToken] = []
        index = 0
        line = 1
        column = 1
        length = len(html)

        while index < length:
            char = html[index]
            if char != "<":
                next_tag = html.find("<", index)
                if next_tag == -1:
                    next_tag = length
                text = html[index:next_tag]
                if text.strip():
                    tokens.append(
                        HtmlToken(
                            type=TokenType.TEXT,
                            value=text,
                            position=TokenPosition(line=line, column=column),
                        )
                    )
                line, column = self._advance_position(text, line, column)
                index = next_tag
                continue

            token_line, token_column = line, column

            if html.startswith("<!--", index):
                end = html.find("-->", index + 4)
                if end == -1:
                    raw = html[index + 4 :]
                    full = html[index:]
                else:
                    raw = html[index + 4 : end]
                    full = html[index : end + 3]
                tokens.append(
                    HtmlToken(
                        type=TokenType.COMMENT,
                        value=raw,
                        position=TokenPosition(line=token_line, column=token_column),
                    )
                )
                line, column = self._advance_position(full, line, column)
                index += len(full)
                continue

            if html[index : index + 9].lower().startswith("<!doctype"):
                end = html.find(">", index + 2)
                end = length - 1 if end == -1 else end
                raw = html[index + 2 : end].strip()
                full = html[index : min(end + 1, length)]
                tokens.append(
                    HtmlToken(
                        type=TokenType.DOCTYPE,
                        value=raw,
                        position=TokenPosition(line=token_line, column=token_column),
                    )
                )
                line, column = self._advance_position(full, line, column)
                index += len(full)
                continue

            end = html.find(">", index + 1)
            if end == -1:
                fragment = html[index + 1 :]
                parsed = self._parse_tag_fragment(fragment)
                if parsed:
                    tag_name, attrs, is_close, is_self_closing = parsed
                    token_type = TokenType.CLOSE_TAG if is_close else TokenType.OPEN_TAG
                    if is_self_closing or tag_name in self.VOID_TAGS:
                        token_type = TokenType.SELF_CLOSING_TAG
                    tokens.append(
                        HtmlToken(
                            type=token_type,
                            value=tag_name,
                            attributes=attrs,
                            position=TokenPosition(line=token_line, column=token_column),
                        )
                    )
                elif fragment.strip():
                    tokens.append(
                        HtmlToken(
                            type=TokenType.TEXT,
                            value=html[index:],
                            position=TokenPosition(line=token_line, column=token_column),
                        )
                    )
                break

            inner = html[index + 1 : end]
            full = html[index : end + 1]
            parsed = self._parse_tag_fragment(inner)
            if parsed:
                tag_name, attrs, is_close, is_self_closing = parsed
                if is_close:
                    token_type = TokenType.CLOSE_TAG
                    attrs = {}
                elif is_self_closing or tag_name in self.VOID_TAGS:
                    token_type = TokenType.SELF_CLOSING_TAG
                else:
                    token_type = TokenType.OPEN_TAG
                tokens.append(
                    HtmlToken(
                        type=token_type,
                        value=tag_name,
                        attributes=attrs,
                        position=TokenPosition(line=token_line, column=token_column),
                    )
                )
            elif inner.strip():
                tokens.append(
                    HtmlToken(
                        type=TokenType.TEXT,
                        value=full,
                        position=TokenPosition(line=token_line, column=token_column),
                    )
                )

            line, column = self._advance_position(full, line, column)
            index = end + 1

        return tokens

    def _parse_tag_fragment(self, fragment: str) -> tuple[str, dict[str, str], bool, bool] | None:
        fragment = fragment.strip()
        if not fragment:
            return None
        if fragment.startswith("!"):
            return None

        is_close = fragment.startswith("/")
        is_self_closing = fragment.endswith("/")
        match = self.TAG_NAME_RE.match(fragment)
        if not match:
            return None

        tag_name = match.group(1).lower()
        attrs_part = fragment[match.end() :].strip()
        if is_self_closing:
            attrs_part = attrs_part[:-1].strip()

        attrs: dict[str, str] = {}
        if not is_close and attrs_part:
            for attr_match in self.ATTR_RE.finditer(attrs_part):
                name = attr_match.group(1).lower()
                if name == tag_name:
                    continue
                value = next(
                    (group for group in attr_match.groups()[1:] if group is not None),
                    "true",
                )
                attrs[name] = value

        return tag_name, attrs, is_close, is_self_closing

    @staticmethod
    def _advance_position(text: str, line: int, column: int) -> tuple[int, int]:
        for char in text:
            if char == "\n":
                line += 1
                column = 1
            else:
                column += 1
        return line, column
