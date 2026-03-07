import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.config import Settings
from app.services.chat_service import ChatService
from app.services.crisis_service import CrisisResult


def _make_chat_service(
    mock_llm=None,
    crisis_is_crisis=False,
    emotion_label="joy",
):
    mock_session_dao = AsyncMock()
    mock_session_dao.validate_token.return_value = True
    mock_session_dao.update_last_active.return_value = None

    mock_crisis = AsyncMock()
    mock_crisis.check_crisis.return_value = CrisisResult(
        is_crisis=crisis_is_crisis,
        response="Crisis response" if crisis_is_crisis else None,
    )

    mock_emotion = AsyncMock()
    mock_emotion.classify_emotion.return_value = (emotion_label, 50)

    mock_memory = AsyncMock()
    mock_memory.get_recent_turns.return_value = []
    mock_memory.add_turn.return_value = None

    if mock_llm is None:
        mock_llm = AsyncMock()
        mock_llm.generate_response.return_value = "I understand how you feel"

    mock_metrics = AsyncMock()
    mock_metrics.log_turn.return_value = None
    mock_metrics.turn_dao.get_next_turn_index.return_value = 1

    settings = Settings(
        DATABASE_URL="sqlite+aiosqlite:///:memory:",
        REDIS_URL="redis://localhost:6379/0",
        LLM_PROVIDER="mock",
    )

    return ChatService(
        auth_service=mock_session_dao,
        crisis_service=mock_crisis,
        emotion_service=mock_emotion,
        memory_service=mock_memory,
        llm_service=mock_llm,
        metrics_service=mock_metrics,
        settings=settings,
    )


@pytest.mark.asyncio
async def test_process_message_normal_flow():
    service = _make_chat_service(emotion_label="fear")

    response = await service.process_message(
        session_id="test-session",
        user_message="I am feeling anxious",
        token="test-token",
    )

    assert response.assistant_message == "I understand how you feel"
    assert response.emotion_label == "fear"
    assert response.is_crisis is False


@pytest.mark.asyncio
async def test_process_message_crisis_flow():
    service = _make_chat_service(crisis_is_crisis=True)

    response = await service.process_message(
        session_id="test-session",
        user_message="I want to end my life",
        token="test-token",
    )

    assert response.is_crisis is True
    assert response.assistant_message == "Crisis response"
    assert response.emotion_label is None


@pytest.mark.asyncio
async def test_process_message_invalid_token():
    service = _make_chat_service()
    service.auth_service.validate_token.return_value = False

    with pytest.raises(PermissionError):
        await service.process_message(
            session_id="test-session",
            user_message="Hello",
            token="invalid-token",
        )


@pytest.mark.asyncio
async def test_process_message_llm_timeout_fallback():
    mock_llm = AsyncMock()
    mock_llm.generate_response.side_effect = TimeoutError("timeout")

    service = _make_chat_service(mock_llm=mock_llm, emotion_label="sadness")

    response = await service.process_message(
        session_id="test-session",
        user_message="I feel sad",
        token="test-token",
    )

    assert response.is_crisis is False
    assert len(response.assistant_message) > 0
