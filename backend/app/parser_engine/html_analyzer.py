"""HTML structure analysis and report metrics."""

from __future__ import annotations

from collections import Counter
from typing import Iterable

from bs4 import BeautifulSoup, Tag

from app.parser_engine.models import (
    DomNode,
    ExtractionTraceModel,
    HtmlMetricsModel,
    HtmlToken,
    IssueSeverity,
    ParserIssue,
    RecipeModel,
    ScoreModel,
    TokenType,
)


class HtmlAnalyzer:
    MAX_REASONABLE_DEPTH = 24

    def analyze(
        self,
        html: str,
        tokens: list[HtmlToken],
        dom_root: DomNode,
        dom_issues: list[ParserIssue],
        recipe: RecipeModel,
        trace: ExtractionTraceModel,
    ) -> tuple[HtmlMetricsModel, list[ParserIssue], list[ParserIssue], ScoreModel]:
        soup = BeautifulSoup(html or "", "lxml")
        errors = [issue for issue in dom_issues if issue.severity == IssueSeverity.ERROR]
        warnings = [issue for issue in dom_issues if issue.severity == IssueSeverity.WARNING]

        errors.extend(self._recipe_errors(recipe))
        errors.extend(self._structure_errors(soup, dom_root))
        warnings.extend(self._recipe_warnings(recipe))
        warnings.extend(self._metadata_warnings(soup))

        completeness = self._recipe_completeness_score(recipe)
        confidence = self._parser_confidence_score(recipe, trace, errors)
        tag_names = [token.value for token in tokens if token.type in (TokenType.OPEN_TAG, TokenType.SELF_CLOSING_TAG)]
        metrics = HtmlMetricsModel(
            total_tags=len(tag_names),
            unique_tags=len(set(tag_names)),
            total_links=len(soup.find_all("a")),
            total_images=len(soup.find_all("img")),
            total_text_nodes=sum(1 for token in tokens if token.type == TokenType.TEXT),
            max_dom_depth=dom_root.max_depth(),
            html_size_bytes=len((html or "").encode("utf-8")),
            tokens_count=len(tokens),
            errors_count=len(errors),
            warnings_count=len(warnings),
            recipe_completeness_score=completeness,
            parser_confidence_score=confidence,
        )
        return metrics, errors, warnings, ScoreModel(
            recipe_completeness_score=completeness,
            parser_confidence_score=confidence,
        )

    def _recipe_errors(self, recipe: RecipeModel) -> list[ParserIssue]:
        checks = [
            ("MISSING_TITLE", not recipe.title, "Recipe title was not found."),
            ("MISSING_INGREDIENTS", not recipe.ingredients, "Recipe ingredients were not found."),
            ("MISSING_STEPS", not recipe.steps, "Recipe instruction steps were not found."),
            ("MISSING_COOKING_TIME", not recipe.cooking_time, "Cooking time was not found."),
            ("MISSING_IMAGE", not recipe.image_url, "Recipe image was not found."),
        ]
        issues = [
            ParserIssue(severity=IssueSeverity.ERROR, code=code, message=message)
            for code, failed, message in checks
            if failed
        ]
        if not recipe.title and not recipe.ingredients and not recipe.steps:
            issues.append(
                ParserIssue(
                    severity=IssueSeverity.ERROR,
                    code="UNRECOGNIZED_RECIPE_STRUCTURE",
                    message="HTML structure does not look like a recipe page.",
                )
            )
        return issues

    def _structure_errors(self, soup: BeautifulSoup, dom_root: DomNode) -> list[ParserIssue]:
        issues: list[ParserIssue] = []
        for image in soup.find_all("img"):
            if not str(image.get("alt", "")).strip():
                issues.append(
                    ParserIssue(
                        severity=IssueSeverity.ERROR,
                        code="IMAGE_ALT_MISSING",
                        message="Image tag is missing a meaningful alt attribute.",
                    )
                )
                break

        for link in soup.find_all("a"):
            if not str(link.get("href", "")).strip():
                issues.append(
                    ParserIssue(
                        severity=IssueSeverity.ERROR,
                        code="EMPTY_LINK_HREF",
                        message="A link with an empty href attribute was found.",
                    )
                )
                break

        ids = [str(tag.get("id")) for tag in soup.find_all(attrs={"id": True})]
        duplicate_ids = [item for item, count in Counter(ids).items() if count > 1]
        if duplicate_ids:
            issues.append(
                ParserIssue(
                    severity=IssueSeverity.ERROR,
                    code="DUPLICATE_ID",
                    message=f"Duplicate id attributes found: {', '.join(duplicate_ids)}.",
                )
            )

        max_depth = dom_root.max_depth()
        if max_depth > self.MAX_REASONABLE_DEPTH:
            issues.append(
                ParserIssue(
                    severity=IssueSeverity.ERROR,
                    code="DOM_TOO_DEEP",
                    message=f"DOM depth {max_depth} exceeds the expected threshold {self.MAX_REASONABLE_DEPTH}.",
                )
            )
        return issues

    def _recipe_warnings(self, recipe: RecipeModel) -> list[ParserIssue]:
        warnings: list[ParserIssue] = []
        if not recipe.nutrition:
            warnings.append(ParserIssue(severity=IssueSeverity.WARNING, code="MISSING_NUTRITION", message="Nutrition data was not found."))
        if not recipe.author:
            warnings.append(ParserIssue(severity=IssueSeverity.WARNING, code="MISSING_AUTHOR", message="Recipe author was not found."))
        if not recipe.category:
            warnings.append(ParserIssue(severity=IssueSeverity.WARNING, code="MISSING_CATEGORY", message="Recipe category was not found."))
        if recipe.steps and len(recipe.steps) < 2:
            warnings.append(ParserIssue(severity=IssueSeverity.WARNING, code="FEW_STEPS", message="Recipe has very few instruction steps."))
        for step in recipe.steps:
            if len(step.text) < 20:
                warnings.append(
                    ParserIssue(
                        severity=IssueSeverity.WARNING,
                        code="SHORT_STEP_DESCRIPTION",
                        message=f"Step {step.step_number} has a very short description.",
                    )
                )
                break
        for ingredient in recipe.ingredients:
            if not ingredient.amount and not ingredient.unit:
                warnings.append(
                    ParserIssue(
                        severity=IssueSeverity.WARNING,
                        code="INGREDIENT_PARSE_FAILED",
                        message=f"Ingredient could not be split into amount and unit: {ingredient.raw_text}.",
                    )
                )
                break
        return warnings

    def _metadata_warnings(self, soup: BeautifulSoup) -> list[ParserIssue]:
        warnings: list[ParserIssue] = []
        canonical = soup.select_one('link[rel="canonical"]')
        if not canonical or not canonical.get("href"):
            warnings.append(ParserIssue(severity=IssueSeverity.WARNING, code="MISSING_CANONICAL", message="Canonical link was not found."))
        meta_description = soup.select_one('meta[name="description"]')
        if not meta_description or not meta_description.get("content"):
            warnings.append(ParserIssue(severity=IssueSeverity.WARNING, code="MISSING_META_DESCRIPTION", message="Meta description was not found."))
        return warnings

    def _recipe_completeness_score(self, recipe: RecipeModel) -> int:
        score = 0
        score += 20 if recipe.title else 0
        score += 20 if recipe.ingredients else 0
        score += 20 if recipe.steps else 0
        score += 10 if recipe.cooking_time else 0
        score += 10 if recipe.image_url else 0
        score += 10 if recipe.nutrition else 0
        score += 5 if recipe.author else 0
        score += 5 if recipe.servings else 0
        return min(score, 100)

    def _parser_confidence_score(
        self,
        recipe: RecipeModel,
        trace: ExtractionTraceModel,
        errors: Iterable[ParserIssue],
    ) -> int:
        score = 0
        score += 35 if trace.used_json_ld else 0
        score += 20 if trace.used_css_selectors else 0
        score += 5 if trace.used_fallback else 0
        score += 15 if recipe.ingredients else 0
        score += 15 if recipe.steps else 0

        critical_codes = {"MISSING_TITLE", "MISSING_INGREDIENTS", "MISSING_STEPS", "UNRECOGNIZED_RECIPE_STRUCTURE"}
        if not any(issue.code in critical_codes for issue in errors):
            score += 10
        return max(0, min(score, 100))

