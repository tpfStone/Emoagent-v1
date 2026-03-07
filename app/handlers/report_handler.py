from fastapi import APIRouter, Depends, HTTPException, Query

from app.dao.session_dao import SessionDAO
from app.dependencies import get_report_service, get_session_dao
from app.schemas.report import WeeklyReportResponse
from app.services.report_service import ReportService

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/weekly", response_model=WeeklyReportResponse)
async def get_weekly_report(
    session_id: str = Query(...),
    token: str = Query(""),
    report_service: ReportService = Depends(get_report_service),
    session_dao: SessionDAO = Depends(get_session_dao),
) -> WeeklyReportResponse:
    if token:
        valid = await session_dao.validate_token(session_id, token)
        if not valid:
            raise HTTPException(status_code=401, detail="Invalid token")

    try:
        return await report_service.get_weekly_report(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
