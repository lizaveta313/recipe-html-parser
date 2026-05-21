"""Response schemas for report endpoints."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.parser_engine.models import ParserReportModel


class ReportListItem(BaseModel):
    id: str
    source_type: str
    source_value: str
    recipe_title: str | None
    recipe_author: str | None
    cooking_time: str | None
    ingredients_count: int
    steps_count: int
    completeness_score: int
    confidence_score: int
    errors_count: int
    warnings_count: int
    created_at: datetime


class DeleteReportResponse(BaseModel):
    deleted: bool


ReportResponse = ParserReportModel
ReportJson = dict[str, Any]

