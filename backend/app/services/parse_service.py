"""Application service that runs parser engine and stores reports."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.security import validate_eda_recipe_url, validate_html_payload
from app.parser_engine.dom_parser import DomParser
from app.parser_engine.html_analyzer import HtmlAnalyzer
from app.parser_engine.models import ParserReportModel, SourceType
from app.parser_engine.recipe_extractor import RecipeExtractor
from app.parser_engine.tokenizer import HtmlTokenizer
from app.repositories.report_repository import ReportRepository
from app.services.html_fetch_service import HtmlFetchService

logger = logging.getLogger(__name__)


class ParseService:
    def __init__(self, db: Session) -> None:
        self.repository = ReportRepository(db)
        self.fetch_service = HtmlFetchService()
        self.tokenizer = HtmlTokenizer()
        self.dom_parser = DomParser()
        self.extractor = RecipeExtractor()
        self.analyzer = HtmlAnalyzer()

    async def parse_url(self, url: str) -> ParserReportModel:
        safe_url = validate_eda_recipe_url(url)
        html = await self.fetch_service.fetch(safe_url)
        return self._parse_and_save(
            html=html,
            source_type=SourceType.URL,
            source_value=safe_url,
            original_url=safe_url,
        )

    def parse_raw_html(self, html: str, source_name: str) -> ParserReportModel:
        validate_html_payload(html)
        return self._parse_and_save(
            html=html,
            source_type=SourceType.RAW_HTML,
            source_value=source_name or "manual test",
            original_url=None,
        )

    def _parse_and_save(
        self,
        html: str,
        source_type: SourceType,
        source_value: str,
        original_url: str | None,
    ) -> ParserReportModel:
        logger.info("Starting parser engine for %s", source_value)
        tokens = self.tokenizer.tokenize(html)
        dom_root, dom_issues = self.dom_parser.parse(tokens)
        recipe, trace = self.extractor.extract(html, original_url=original_url)
        metrics, errors, warnings, scores = self.analyzer.analyze(
            html=html,
            tokens=tokens,
            dom_root=dom_root,
            dom_issues=dom_issues,
            recipe=recipe,
            trace=trace,
        )
        report = ParserReportModel(
            id=str(uuid4()),
            source_type=source_type,
            source_value=source_value,
            created_at=datetime.now(timezone.utc),
            recipe=recipe,
            html_analysis=metrics,
            errors=errors,
            warnings=warnings,
            scores=scores,
            dom_tree_preview=dom_root.to_dict(max_depth=4),
            tokens_preview=[token.model_dump(mode="json") for token in tokens[:40]],
            extraction_trace=trace,
        )
        self.repository.create(report)
        logger.info("Parser report %s saved", report.id)
        return report

