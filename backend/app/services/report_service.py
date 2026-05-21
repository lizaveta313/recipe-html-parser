"""Report query service."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.report_repository import ReportRepository
from app.schemas.report import ReportListItem


class ReportService:
    def __init__(self, db: Session) -> None:
        self.repository = ReportRepository(db)

    def list_reports(self) -> list[ReportListItem]:
        return [
            ReportListItem(
                id=record.id,
                source_type=record.source_type,
                source_value=record.source_value,
                recipe_title=record.recipe_title,
                recipe_author=record.recipe_author,
                cooking_time=record.cooking_time,
                ingredients_count=record.ingredients_count,
                steps_count=record.steps_count,
                completeness_score=record.completeness_score,
                confidence_score=record.confidence_score,
                errors_count=record.errors_count,
                warnings_count=record.warnings_count,
                created_at=record.created_at,
            )
            for record in self.repository.list()
        ]

    def get_report_json(self, report_id: str) -> dict | None:
        record = self.repository.get(report_id)
        return record.report_json if record else None

    def delete_report(self, report_id: str) -> bool:
        return self.repository.delete(report_id)

