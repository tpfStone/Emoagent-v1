import pytest
from unittest.mock import AsyncMock

from app.services.report_service import ReportService


@pytest.mark.asyncio
async def test_get_weekly_report():
    mock_turn_dao = AsyncMock()
    mock_turn_dao.get_turns_in_range.return_value = [1, 2, 3]
    mock_turn_dao.get_emotion_distribution.return_value = {"joy": 2, "sadness": 1}
    mock_turn_dao.count_crisis_turns.return_value = 0
    mock_turn_dao.get_avg_latencies.return_value = {"bert": 45, "llm": 1500}

    mock_rating_dao = AsyncMock()
    mock_rating_dao.get_avg_scores.return_value = {"before": 4.0, "after": 7.0}
    mock_rating_dao.get_missing_rate.return_value = 0.1

    service = ReportService(mock_turn_dao, mock_rating_dao)
    report = await service.get_weekly_report("test-session")

    assert report.session_id == "test-session"
    assert report.total_turns == 3
    assert report.emotion_distribution == {"joy": 2, "sadness": 1}
    assert report.crisis_count == 0
    assert report.rating_before_avg == 4.0
    assert report.rating_after_avg == 7.0
    assert report.rating_missing_rate == 0.1
    assert report.bert_avg_latency_ms == 45
    assert report.llm_avg_latency_ms == 1500
