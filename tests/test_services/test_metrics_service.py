import pytest
from unittest.mock import AsyncMock

from app.services.metrics_service import MetricsService


@pytest.mark.asyncio
async def test_log_turn():
    mock_turn_dao = AsyncMock()
    service = MetricsService(mock_turn_dao)

    await service.log_turn(
        session_id="test-session",
        turn_index=1,
        user_message="Hello",
        assistant_message="Hi there",
        emotion_label="joy",
        is_crisis=False,
        bert_latency_ms=50,
        llm_latency_ms=1200,
    )

    mock_turn_dao.create_turn.assert_called_once_with(
        session_id="test-session",
        turn_index=1,
        user_message="Hello",
        assistant_message="Hi there",
        emotion_label="joy",
        is_crisis=False,
        bert_latency_ms=50,
        llm_latency_ms=1200,
    )
