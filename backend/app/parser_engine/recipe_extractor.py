"""Recipe extraction strategies for eda.rambler.ru HTML pages."""

from __future__ import annotations

import json
import re
from typing import Any, Iterable
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from app.parser_engine.models import (
    ExtractionTraceModel,
    IngredientModel,
    NutritionModel,
    RecipeModel,
    RecipeStepModel,
)


class RecipeExtractor:
    BASE_URL = "https://eda.rambler.ru"
    UNITS = (
        "г",
        "кг",
        "мг",
        "мл",
        "л",
        "стакан",
        "стакана",
        "стаканов",
        "ст. л.",
        "ст.л.",
        "ч. л.",
        "ч.л.",
        "ложка",
        "ложки",
        "ложек",
        "штука",
        "штуки",
        "штук",
        "шт.",
        "пучок",
        "зубчик",
        "зубчика",
        "по вкусу",
    )

    def extract(self, html: str, original_url: str | None = None) -> tuple[RecipeModel, ExtractionTraceModel]:
        soup = BeautifulSoup(html or "", "lxml")
        recipe = RecipeModel(original_url=original_url, source_site="eda.rambler.ru")
        trace = ExtractionTraceModel()

        json_ld_recipe = self._extract_json_ld_recipe(soup)
        if json_ld_recipe:
            trace.used_json_ld = True
            self._apply_json_ld(recipe, json_ld_recipe)

        self._apply_css_selectors(recipe, soup, trace)
        self._apply_fallback(recipe, soup, trace)

        recipe.ingredients = self._dedupe_ingredients(recipe.ingredients)
        recipe.steps = self._dedupe_steps(recipe.steps)
        recipe.tags = self._dedupe_text(recipe.tags)
        recipe.equipment = self._dedupe_text(recipe.equipment)
        return recipe, trace

    def _extract_json_ld_recipe(self, soup: BeautifulSoup) -> dict[str, Any] | None:
        for script in soup.select('script[type="application/ld+json"]'):
            raw = script.string or script.get_text(strip=True)
            if not raw:
                continue
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue
            recipe = self._find_recipe_object(data)
            if recipe:
                return recipe
        return None

    def _find_recipe_object(self, data: Any) -> dict[str, Any] | None:
        if isinstance(data, list):
            for item in data:
                found = self._find_recipe_object(item)
                if found:
                    return found
        if isinstance(data, dict):
            type_value = data.get("@type") or data.get("type")
            if self._type_contains_recipe(type_value):
                return data
            graph = data.get("@graph")
            if graph:
                return self._find_recipe_object(graph)
        return None

    @staticmethod
    def _type_contains_recipe(value: Any) -> bool:
        if isinstance(value, str):
            return value.lower() == "recipe"
        if isinstance(value, list):
            return any(str(item).lower() == "recipe" for item in value)
        return False

    def _apply_json_ld(self, recipe: RecipeModel, data: dict[str, Any]) -> None:
        recipe.title = self._first_text(data.get("name") or data.get("headline")) or recipe.title
        recipe.author = self._extract_author(data.get("author")) or recipe.author
        recipe.category = self._first_text(data.get("recipeCategory")) or recipe.category
        recipe.servings = self._first_text(data.get("recipeYield")) or recipe.servings
        recipe.cooking_time = (
            self._format_duration(data.get("totalTime"))
            or self._format_duration(data.get("cookTime"))
            or self._format_duration(data.get("prepTime"))
            or recipe.cooking_time
        )
        recipe.image_url = self._extract_image(data.get("image")) or recipe.image_url
        recipe.rating = self._extract_rating(data.get("aggregateRating")) or recipe.rating
        recipe.description = self._first_text(data.get("description")) or recipe.description
        recipe.ingredients.extend(
            self._parse_ingredient(raw)
            for raw in self._as_list(data.get("recipeIngredient"))
            if self._first_text(raw)
        )
        recipe.steps.extend(self._parse_json_ld_steps(data.get("recipeInstructions")))
        recipe.nutrition = self._parse_nutrition(data.get("nutrition")) or recipe.nutrition
        recipe.tags.extend(self._parse_keywords(data.get("keywords")))
        recipe.equipment.extend(self._parse_tools(data.get("tool") or data.get("instrument")))

    def _apply_css_selectors(
        self,
        recipe: RecipeModel,
        soup: BeautifulSoup,
        trace: ExtractionTraceModel,
    ) -> None:
        recipe.title = recipe.title or self._select_text(
            soup,
            trace,
            '[itemprop="name"]',
            "h1",
            ".recipe-title",
            '[data-testid="recipe-title"]',
        )
        recipe.author = recipe.author or self._select_text(
            soup,
            trace,
            '[itemprop="author"]',
            ".author",
            ".recipe-author",
            '[rel="author"]',
        )
        recipe.category = recipe.category or self._select_text(
            soup,
            trace,
            '[itemprop="recipeCategory"]',
            ".recipe-category",
            '[data-testid="recipe-category"]',
        )
        recipe.servings = recipe.servings or self._select_text(
            soup,
            trace,
            '[itemprop="recipeYield"]',
            ".servings",
            '[data-testid="servings"]',
        )
        recipe.cooking_time = recipe.cooking_time or self._select_text(
            soup,
            trace,
            '[itemprop="totalTime"]',
            "time",
            ".cooking-time",
            '[data-testid="cooking-time"]',
        )
        recipe.description = recipe.description or self._select_attr_or_text(
            soup,
            trace,
            ('meta[name="description"]', "content"),
            ('[itemprop="description"]', None),
            (".recipe-description", None),
        )
        recipe.image_url = recipe.image_url or self._select_image(soup, trace)

        if not recipe.ingredients:
            ingredient_nodes = self._select_nodes(
                soup,
                trace,
                '[itemprop="recipeIngredient"]',
                ".ingredient",
                ".ingredients li",
                '[data-testid="ingredient"]',
            )
            recipe.ingredients.extend(self._parse_ingredient(node.get_text(" ", strip=True)) for node in ingredient_nodes)

        if not recipe.steps:
            step_nodes = self._select_nodes(
                soup,
                trace,
                '[itemprop="recipeInstructions"] [itemprop="text"]',
                ".instruction-step",
                ".step",
                ".instructions li",
                '[data-testid="instruction-step"]',
            )
            for index, node in enumerate(step_nodes, start=1):
                image = node.select_one("img")
                recipe.steps.append(
                    RecipeStepModel(
                        step_number=index,
                        text=node.get_text(" ", strip=True),
                        image_url=self._absolute_url(image.get("src")) if image and image.get("src") else None,
                    )
                )

        recipe.nutrition = recipe.nutrition or self._parse_nutrition_from_dom(soup, trace)
        recipe.tags.extend(
            node.get_text(" ", strip=True)
            for node in self._select_nodes(soup, trace, ".tags a", '[itemprop="keywords"]')
            if node.get_text(" ", strip=True)
        )
        recipe.equipment.extend(
            node.get_text(" ", strip=True)
            for node in self._select_nodes(soup, trace, ".equipment li", ".tools li", '[data-testid="equipment"]')
            if node.get_text(" ", strip=True)
        )
        recipe.comments_count = recipe.comments_count or self._extract_comments_count(soup, trace)

    def _apply_fallback(self, recipe: RecipeModel, soup: BeautifulSoup, trace: ExtractionTraceModel) -> None:
        before = recipe.model_dump()
        recipe.title = recipe.title or self._text_or_none(soup.find("h1")) or self._title_from_head(soup)
        recipe.image_url = recipe.image_url or self._first_image(soup)
        recipe.description = recipe.description or self._first_long_paragraph(soup)
        recipe.cooking_time = recipe.cooking_time or self._regex_text(
            soup,
            r"\b\d+\s*(?:минут|минуты|мин|часа|часов|ч)\b",
        )

        if not recipe.ingredients:
            recipe.ingredients.extend(self._extract_list_after_heading(soup, ("ингредиенты",)))

        if not recipe.steps:
            raw_steps = self._extract_list_after_heading(
                soup,
                ("инструкция", "приготовление", "шаги приготовления", "способ приготовления"),
                parse_ingredients=False,
            )
            recipe.steps.extend(
                RecipeStepModel(step_number=index, text=item.raw_text)
                for index, item in enumerate(raw_steps, start=1)
            )

        if not recipe.servings:
            recipe.servings = self._regex_text(soup, r"\b\d+\s*(?:порц(?:ия|ии|ий)|персон[а-я]*)\b")

        if before != recipe.model_dump():
            trace.used_fallback = True

    def _select_text(self, soup: BeautifulSoup, trace: ExtractionTraceModel, *selectors: str) -> str | None:
        for selector in selectors:
            node = soup.select_one(selector)
            text = self._text_or_none(node)
            if text:
                trace.used_css_selectors = True
                trace.matched_selectors.append(selector)
                return text
        return None

    def _select_attr_or_text(
        self,
        soup: BeautifulSoup,
        trace: ExtractionTraceModel,
        *selectors: tuple[str, str | None],
    ) -> str | None:
        for selector, attr in selectors:
            node = soup.select_one(selector)
            if not node:
                continue
            value = node.get(attr) if attr else node.get_text(" ", strip=True)
            if value:
                trace.used_css_selectors = True
                trace.matched_selectors.append(selector)
                return str(value).strip()
        return None

    def _select_nodes(self, soup: BeautifulSoup, trace: ExtractionTraceModel, *selectors: str) -> list[Tag]:
        for selector in selectors:
            nodes = [node for node in soup.select(selector) if isinstance(node, Tag)]
            if nodes:
                trace.used_css_selectors = True
                trace.matched_selectors.append(selector)
                return nodes
        return []

    def _select_image(self, soup: BeautifulSoup, trace: ExtractionTraceModel) -> str | None:
        selectors = (
            ('meta[property="og:image"]', "content"),
            ('[itemprop="image"]', "src"),
            (".recipe-image img", "src"),
            ('[data-testid="recipe-image"] img', "src"),
            ("article img", "src"),
        )
        for selector, attr in selectors:
            node = soup.select_one(selector)
            if node and node.get(attr):
                trace.used_css_selectors = True
                trace.matched_selectors.append(selector)
                return self._absolute_url(str(node.get(attr)))
        return None

    def _parse_json_ld_steps(self, instructions: Any) -> list[RecipeStepModel]:
        steps: list[RecipeStepModel] = []
        for item in self._as_list(instructions):
            if isinstance(item, str):
                text = item.strip()
                if text:
                    steps.append(RecipeStepModel(step_number=len(steps) + 1, text=text))
            elif isinstance(item, dict):
                item_type = item.get("@type")
                if str(item_type).lower() == "howtosection":
                    steps.extend(self._parse_json_ld_steps(item.get("itemListElement")))
                    continue
                text = self._first_text(item.get("text") or item.get("name"))
                if text:
                    steps.append(
                        RecipeStepModel(
                            step_number=len(steps) + 1,
                            text=text,
                            image_url=self._extract_image(item.get("image")),
                        )
                    )
        return steps

    def _parse_ingredient(self, raw: Any) -> IngredientModel:
        text = self._first_text(raw) or ""
        text = re.sub(r"\s+", " ", text).strip()
        lower = text.lower()
        if "по вкусу" in lower:
            name = re.sub(r"\bпо вкусу\b", "", text, flags=re.IGNORECASE).strip(" -,:")
            return IngredientModel(name=name or text, amount=None, unit="по вкусу", raw_text=text)

        amount = r"(?P<amount>\d+(?:[.,/]\d+)?|[¼½¾⅓⅔]+)"
        unit = r"(?P<unit>" + "|".join(re.escape(unit) for unit in self.UNITS if unit != "по вкусу") + r")"
        pattern_after_name = re.compile(rf"^(?P<name>.+?)\s+{amount}\s*{unit}\.?$", re.IGNORECASE)
        pattern_before_name = re.compile(rf"^{amount}\s*{unit}\.?\s+(?P<name>.+)$", re.IGNORECASE)

        for pattern in (pattern_after_name, pattern_before_name):
            match = pattern.match(text)
            if match:
                return IngredientModel(
                    name=match.group("name").strip(" -,:"),
                    amount=match.group("amount").replace(",", "."),
                    unit=match.group("unit"),
                    raw_text=text,
                )
        return IngredientModel(name=text, raw_text=text)

    def _parse_nutrition(self, nutrition: Any) -> NutritionModel | None:
        if not isinstance(nutrition, dict):
            return None
        return NutritionModel(
            calories=self._number_from_text(nutrition.get("calories")),
            proteins=self._number_from_text(nutrition.get("proteinContent")),
            fats=self._number_from_text(nutrition.get("fatContent")),
            carbohydrates=self._number_from_text(nutrition.get("carbohydrateContent")),
        )

    def _parse_nutrition_from_dom(self, soup: BeautifulSoup, trace: ExtractionTraceModel) -> NutritionModel | None:
        selectors = {
            "calories": ('[itemprop="calories"]', ".calories", '[data-testid="calories"]'),
            "proteins": ('[itemprop="proteinContent"]', ".proteins", '[data-testid="proteins"]'),
            "fats": ('[itemprop="fatContent"]', ".fats", '[data-testid="fats"]'),
            "carbohydrates": ('[itemprop="carbohydrateContent"]', ".carbohydrates", '[data-testid="carbohydrates"]'),
        }
        values: dict[str, float | None] = {}
        for field, field_selectors in selectors.items():
            text = self._select_text(soup, trace, *field_selectors)
            values[field] = self._number_from_text(text)
        if any(value is not None for value in values.values()):
            return NutritionModel(**values)
        return None

    def _extract_list_after_heading(
        self,
        soup: BeautifulSoup,
        heading_words: tuple[str, ...],
        parse_ingredients: bool = True,
    ) -> list[IngredientModel]:
        for heading in soup.find_all(["h2", "h3", "h4", "strong"]):
            heading_text = heading.get_text(" ", strip=True).lower()
            if not any(word in heading_text for word in heading_words):
                continue
            sibling = heading.find_next(["ul", "ol"])
            if not sibling:
                continue
            items = [item.get_text(" ", strip=True) for item in sibling.find_all("li")]
            if items:
                if parse_ingredients:
                    return [self._parse_ingredient(item) for item in items]
                return [IngredientModel(name=item, raw_text=item) for item in items]
        return []

    def _extract_comments_count(self, soup: BeautifulSoup, trace: ExtractionTraceModel) -> int | None:
        text = self._select_text(soup, trace, '[data-testid="comments-count"]', ".comments-count")
        number = self._number_from_text(text)
        return int(number) if number is not None else None

    def _parse_keywords(self, value: Any) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in re.split(r"[,;]", value) if item.strip()]
        return [text for text in (self._first_text(item) for item in self._as_list(value)) if text]

    def _parse_tools(self, value: Any) -> list[str]:
        return [text for text in (self._first_text(item) for item in self._as_list(value)) if text]

    def _extract_author(self, value: Any) -> str | None:
        if isinstance(value, dict):
            return self._first_text(value.get("name"))
        if isinstance(value, list):
            return ", ".join(filter(None, (self._extract_author(item) for item in value))) or None
        return self._first_text(value)

    def _extract_image(self, value: Any) -> str | None:
        if isinstance(value, dict):
            return self._absolute_url(self._first_text(value.get("url") or value.get("contentUrl")))
        if isinstance(value, list):
            return self._extract_image(value[0]) if value else None
        return self._absolute_url(self._first_text(value))

    def _extract_rating(self, value: Any) -> str | None:
        if isinstance(value, dict):
            return self._first_text(value.get("ratingValue"))
        return None

    def _first_image(self, soup: BeautifulSoup) -> str | None:
        image = soup.find("img")
        if isinstance(image, Tag) and image.get("src"):
            return self._absolute_url(str(image.get("src")))
        return None

    def _first_long_paragraph(self, soup: BeautifulSoup) -> str | None:
        for paragraph in soup.find_all("p"):
            text = paragraph.get_text(" ", strip=True)
            if len(text) >= 40:
                return text
        return None

    def _title_from_head(self, soup: BeautifulSoup) -> str | None:
        title = soup.find("title")
        return self._text_or_none(title)

    def _regex_text(self, soup: BeautifulSoup, pattern: str) -> str | None:
        text = soup.get_text(" ", strip=True)
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(0) if match else None

    def _absolute_url(self, url: str | None) -> str | None:
        if not url:
            return None
        return urljoin(self.BASE_URL, url)

    @staticmethod
    def _as_list(value: Any) -> list[Any]:
        if value is None:
            return []
        return value if isinstance(value, list) else [value]

    @staticmethod
    def _first_text(value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, list):
            for item in value:
                text = RecipeExtractor._first_text(item)
                if text:
                    return text
            return None
        if isinstance(value, dict):
            return RecipeExtractor._first_text(value.get("name") or value.get("text") or value.get("@id"))
        text = str(value).strip()
        return text or None

    @staticmethod
    def _text_or_none(node: Tag | None) -> str | None:
        if not node:
            return None
        text = node.get_text(" ", strip=True)
        return text or None

    @staticmethod
    def _number_from_text(value: Any) -> float | None:
        if value is None:
            return None
        match = re.search(r"\d+(?:[.,]\d+)?", str(value))
        return float(match.group(0).replace(",", ".")) if match else None

    @staticmethod
    def _format_duration(value: Any) -> str | None:
        text = RecipeExtractor._first_text(value)
        if not text:
            return None
        match = re.fullmatch(r"P(?:T)?(?:(\d+)H)?(?:(\d+)M)?", text)
        if not match:
            return text
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        parts = []
        if hours:
            parts.append(f"{hours} ч")
        if minutes:
            parts.append(f"{minutes} мин")
        return " ".join(parts) or text

    @staticmethod
    def _dedupe_text(values: Iterable[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            normalized = re.sub(r"\s+", " ", value).strip()
            key = normalized.lower()
            if normalized and key not in seen:
                seen.add(key)
                result.append(normalized)
        return result

    @staticmethod
    def _dedupe_ingredients(values: Iterable[IngredientModel]) -> list[IngredientModel]:
        seen: set[str] = set()
        result: list[IngredientModel] = []
        for item in values:
            key = item.raw_text.lower()
            if item.raw_text and key not in seen:
                seen.add(key)
                result.append(item)
        return result

    @staticmethod
    def _dedupe_steps(values: Iterable[RecipeStepModel]) -> list[RecipeStepModel]:
        seen: set[str] = set()
        result: list[RecipeStepModel] = []
        for item in values:
            key = item.text.lower()
            if item.text and key not in seen:
                seen.add(key)
                result.append(RecipeStepModel(step_number=len(result) + 1, text=item.text, image_url=item.image_url))
        return result
