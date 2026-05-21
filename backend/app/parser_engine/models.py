"""Shared models for the educational parser engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class TokenType(str, Enum):
    DOCTYPE = "DOCTYPE"
    OPEN_TAG = "OPEN_TAG"
    CLOSE_TAG = "CLOSE_TAG"
    SELF_CLOSING_TAG = "SELF_CLOSING_TAG"
    TEXT = "TEXT"
    COMMENT = "COMMENT"


class IssueSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"


class SourceType(str, Enum):
    URL = "url"
    RAW_HTML = "raw_html"


class TokenPosition(BaseModel):
    line: int = 1
    column: int = 1


class HtmlToken(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    type: TokenType
    value: str
    attributes: dict[str, str] = Field(default_factory=dict)
    position: TokenPosition = Field(default_factory=TokenPosition)


class ParserIssue(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    severity: IssueSeverity
    code: str
    message: str
    position: Optional[TokenPosition] = None


@dataclass
class DomNode:
    tag: str
    attributes: dict[str, str] = field(default_factory=dict)
    text: str = ""
    children: list["DomNode"] = field(default_factory=list)
    parent: Optional["DomNode"] = field(default=None, repr=False)
    depth: int = 0
    position: Optional[TokenPosition] = None
    self_closing: bool = False

    def add_child(self, child: "DomNode") -> None:
        child.parent = self
        child.depth = self.depth + 1
        self.children.append(child)

    def find_all(self, tag: str) -> list["DomNode"]:
        matches: list[DomNode] = []
        if self.tag == tag:
            matches.append(self)
        for child in self.children:
            matches.extend(child.find_all(tag))
        return matches

    def max_depth(self) -> int:
        if not self.children:
            return self.depth
        return max(child.max_depth() for child in self.children)

    def to_dict(self, max_depth: int = 4, include_empty_text: bool = False) -> dict[str, Any]:
        data: dict[str, Any] = {
            "tag": self.tag,
            "attributes": self.attributes,
            "text": self.text if include_empty_text or self.text else "",
            "depth": self.depth,
            "position": self.position.model_dump() if self.position else None,
            "children": [],
        }
        if max_depth <= 0:
            data["children_count"] = len(self.children)
            return data
        data["children"] = [
            child.to_dict(max_depth=max_depth - 1, include_empty_text=include_empty_text)
            for child in self.children[:20]
        ]
        if len(self.children) > 20:
            data["truncated_children"] = len(self.children) - 20
        return data


class IngredientModel(BaseModel):
    name: str
    amount: Optional[str] = None
    unit: Optional[str] = None
    raw_text: str


class RecipeStepModel(BaseModel):
    step_number: int
    text: str
    image_url: Optional[str] = None


class NutritionModel(BaseModel):
    calories: Optional[float] = None
    proteins: Optional[float] = None
    fats: Optional[float] = None
    carbohydrates: Optional[float] = None


class RecipeModel(BaseModel):
    title: Optional[str] = None
    original_url: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    servings: Optional[str] = None
    cooking_time: Optional[str] = None
    image_url: Optional[str] = None
    rating: Optional[str] = None
    description: Optional[str] = None
    ingredients: list[IngredientModel] = Field(default_factory=list)
    steps: list[RecipeStepModel] = Field(default_factory=list)
    nutrition: Optional[NutritionModel] = None
    tags: list[str] = Field(default_factory=list)
    equipment: list[str] = Field(default_factory=list)
    comments_count: Optional[int] = None
    source_site: str = "eda.rambler.ru"


class HtmlMetricsModel(BaseModel):
    total_tags: int = 0
    unique_tags: int = 0
    total_links: int = 0
    total_images: int = 0
    total_text_nodes: int = 0
    max_dom_depth: int = 0
    html_size_bytes: int = 0
    tokens_count: int = 0
    errors_count: int = 0
    warnings_count: int = 0
    recipe_completeness_score: int = 0
    parser_confidence_score: int = 0


class ScoreModel(BaseModel):
    recipe_completeness_score: int
    parser_confidence_score: int


class ExtractionTraceModel(BaseModel):
    used_json_ld: bool = False
    used_css_selectors: bool = False
    used_fallback: bool = False
    matched_selectors: list[str] = Field(default_factory=list)


class ParserReportModel(BaseModel):
    id: str
    source_type: SourceType
    source_value: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    recipe: RecipeModel
    html_analysis: HtmlMetricsModel
    errors: list[ParserIssue] = Field(default_factory=list)
    warnings: list[ParserIssue] = Field(default_factory=list)
    scores: ScoreModel
    dom_tree_preview: dict[str, Any]
    tokens_preview: list[dict[str, Any]]
    extraction_trace: ExtractionTraceModel = Field(default_factory=ExtractionTraceModel)

