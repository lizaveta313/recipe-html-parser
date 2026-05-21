"""Parsing API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import SecurityValidationError
from app.parser_engine.models import ParserReportModel
from app.schemas.parse import ParseHtmlRequest, ParseUrlRequest
from app.services.html_fetch_service import HtmlFetchError
from app.services.parse_service import ParseService

router = APIRouter(prefix="/api/parse", tags=["parse"])


@router.post("/url", response_model=ParserReportModel)
async def parse_url(payload: ParseUrlRequest, db: Session = Depends(get_db)) -> ParserReportModel:
    try:
        return await ParseService(db).parse_url(payload.url)
    except SecurityValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except HtmlFetchError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.post("/html", response_model=ParserReportModel)
def parse_html(payload: ParseHtmlRequest, db: Session = Depends(get_db)) -> ParserReportModel:
    try:
        return ParseService(db).parse_raw_html(payload.html, payload.source_name)
    except SecurityValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

