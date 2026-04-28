from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.dependencies import get_report_service, get_session_dao
from app.main import app
from app.schemas.report import TimeRange, WeeklyReportResponse


@pytest.mark.asyncio
async def test_get_weekly_report_success():
    mock_session_dao = AsyncMock()
    mock_session_dao.validate_token.return_value = True

    mock_report_service = AsyncMock()
    mock_report_service.get_weekly_report.return_value = WeeklyReportResponse(
        session_id="test-session",
        time_range=TimeRange(start="2026-02-27T00:00:00Z", end="2026-03-06T00:00:00Z"),
        session_count=1,
        total_turns=10,
        avg_turns_per_session=10.0,
        emotion_distribution={"joy": 5, "sadness": 3, "fear": 2},
        crisis_count=0,
        rating_before_avg=4.0,
        rating_after_avg=7.5,
        rating_missing_rate=0.0,
        bert_avg_latency_ms=50,
        llm_avg_latency_ms=1500,
    )

    app.dependency_overrides[get_session_dao] = lambda: mock_session_dao
    app.dependency_overrides[get_report_service] = lambda: mock_report_service
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/api/reports/weekly",
                params={"session_id": "test-session", "token": "test-token"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["total_turns"] == 10
        assert data["crisis_count"] == 0
        assert data["emotion_distribution"]["joy"] == 5
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_weekly_report_invalid_token():
    mock_session_dao = AsyncMock()
    mock_session_dao.validate_token.return_value = False

    mock_report_service = AsyncMock()

    app.dependency_overrides[get_session_dao] = lambda: mock_session_dao
    app.dependency_overrides[get_report_service] = lambda: mock_report_service
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/api/reports/weekly",
                params={"session_id": "test-session", "token": "bad-token"},
            )

        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()
