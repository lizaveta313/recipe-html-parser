"""Build an internal DOM tree from educational tokenizer tokens."""

from __future__ import annotations

from app.parser_engine.models import DomNode, HtmlToken, IssueSeverity, ParserIssue, TokenType


class DomParser:
    """A small tolerant DOM parser that records structural HTML problems."""

    def parse(self, tokens: list[HtmlToken]) -> tuple[DomNode, list[ParserIssue]]:
        root = DomNode(tag="document", depth=0)
        stack: list[DomNode] = [root]
        issues: list[ParserIssue] = []

        for token in tokens:
            token_type = TokenType(token.type)

            if token_type == TokenType.DOCTYPE:
                stack[-1].add_child(
                    DomNode(tag="#doctype", text=token.value, position=token.position, self_closing=True)
                )
                continue

            if token_type == TokenType.COMMENT:
                stack[-1].add_child(
                    DomNode(tag="#comment", text=token.value, position=token.position, self_closing=True)
                )
                continue

            if token_type == TokenType.TEXT:
                text = token.value.strip()
                if text:
                    stack[-1].add_child(DomNode(tag="#text", text=text, position=token.position))
                continue

            if token_type == TokenType.SELF_CLOSING_TAG:
                stack[-1].add_child(
                    DomNode(
                        tag=token.value,
                        attributes=token.attributes,
                        position=token.position,
                        self_closing=True,
                    )
                )
                continue

            if token_type == TokenType.OPEN_TAG:
                node = DomNode(tag=token.value, attributes=token.attributes, position=token.position)
                stack[-1].add_child(node)
                stack.append(node)
                continue

            if token_type == TokenType.CLOSE_TAG:
                self._handle_close_tag(token, stack, issues)

        for unclosed in reversed(stack[1:]):
            issues.append(
                ParserIssue(
                    severity=IssueSeverity.ERROR,
                    code="UNCLOSED_TAG",
                    message=f"Tag <{unclosed.tag}> was opened but not closed.",
                    position=unclosed.position,
                )
            )

        return root, issues

    def _handle_close_tag(
        self,
        token: HtmlToken,
        stack: list[DomNode],
        issues: list[ParserIssue],
    ) -> None:
        if len(stack) == 1:
            issues.append(
                ParserIssue(
                    severity=IssueSeverity.ERROR,
                    code="EXTRA_CLOSING_TAG",
                    message=f"Closing tag </{token.value}> has no matching opening tag.",
                    position=token.position,
                )
            )
            return

        if stack[-1].tag == token.value:
            stack.pop()
            return

        matching_index = next(
            (index for index in range(len(stack) - 2, 0, -1) if stack[index].tag == token.value),
            None,
        )
        if matching_index is None:
            issues.append(
                ParserIssue(
                    severity=IssueSeverity.ERROR,
                    code="EXTRA_CLOSING_TAG",
                    message=f"Closing tag </{token.value}> has no matching opening tag.",
                    position=token.position,
                )
            )
            return

        expected = stack[-1].tag
        issues.append(
            ParserIssue(
                severity=IssueSeverity.ERROR,
                code="MISMATCHED_NESTING",
                message=f"Closing tag </{token.value}> appeared while <{expected}> was still open.",
                position=token.position,
            )
        )

        while len(stack) - 1 >= matching_index:
            stack.pop()

