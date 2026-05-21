"""Report API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.parser_engine.models import ParserReportModel
from app.schemas.report import DeleteReportResponse, ReportListItem
from app.services.report_service import ReportService

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("", response_model=list[ReportListItem])
def list_reports(db: Session = Depends(get_db)) -> list[ReportListItem]:
    return ReportService(db).list_reports()


@router.get("/{report_id}", response_model=ParserReportModel)
def get_report(report_id: str, db: Session = Depends(get_db)) -> dict:
    report = ReportService(db).get_report_json(report_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
    return report


@router.delete("/{report_id}", response_model=DeleteReportResponse)
def delete_report(report_id: str, db: Session = Depends(get_db)) -> DeleteReportResponse:
    deleted = ReportService(db).delete_report(report_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
    return DeleteReportResponse(deleted=True)

