"""Persistence layer for parser reports."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, String, Text, delete, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, Session, mapped_column
from sqlalchemy.types import JSON

from app.core.database import Base
from app.parser_engine.models import ParserReportModel, SourceType


class ReportRecord(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    source_type: Mapped[str] = mapped_column(String(20), nullable=False)
    source_value: Mapped[str] = mapped_column(Text, nullable=False)
    recipe_title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    recipe_author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cooking_time: Mapped[str | None] = mapped_column(String(120), nullable=True)
    ingredients_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    steps_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completeness_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    confidence_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    errors_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    warnings_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    report_json: Mapped[dict[str, Any]] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ReportRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, report: ParserReportModel) -> ReportRecord:
        record = ReportRecord(
            id=report.id,
            source_type=self._source_type_value(report.source_type),
            source_value=report.source_value,
            recipe_title=report.recipe.title,
            recipe_author=report.recipe.author,
            cooking_time=report.recipe.cooking_time,
            ingredients_count=len(report.recipe.ingredients),
            steps_count=len(report.recipe.steps),
            completeness_score=report.scores.recipe_completeness_score,
            confidence_score=report.scores.parser_confidence_score,
            errors_count=len(report.errors),
            warnings_count=len(report.warnings),
            report_json=report.model_dump(mode="json"),
            created_at=report.created_at,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list(self) -> list[ReportRecord]:
        return list(self.db.scalars(select(ReportRecord).order_by(ReportRecord.created_at.desc())).all())

    def get(self, report_id: str) -> ReportRecord | None:
        return self.db.get(ReportRecord, report_id)

    def delete(self, report_id: str) -> bool:
        result = self.db.execute(delete(ReportRecord).where(ReportRecord.id == report_id))
        self.db.commit()
        return bool(result.rowcount)

    @staticmethod
    def _source_type_value(source_type: SourceType | str) -> str:
        return source_type.value if isinstance(source_type, SourceType) else str(source_type)

