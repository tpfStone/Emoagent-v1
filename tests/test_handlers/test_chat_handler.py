import pytest
from unittest.mock import AsyncMock

from httpx import ASGITransport, AsyncClient

from app.main import app
from app.dependencies import get_chat_service
from app.schemas.chat import ChatResponse


@pytest.mark.asyncio
async def test_send_message_success():
    mock_chat = AsyncMock()
    mock_chat.process_message.return_value = ChatResponse(
        assistant_message="I understand",
        emotion_label="fear",
        is_crisis=False,
        turn_index=1,
    )

    app.dependency_overrides[get_chat_service] = lambda: mock_chat
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/chat/message",
                json={
                    "session_id": "test-session",
                    "user_message": "I am feeling anxious",
                    "token": "test-token",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["assistant_message"] == "I understand"
        assert data["emotion_label"] == "fear"
        assert data["is_crisis"] is False
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_send_message_invalid_token():
    mock_chat = AsyncMock()
    mock_chat.process_message.side_effect = PermissionError("Invalid token")

    app.dependency_overrides[get_chat_service] = lambda: mock_chat
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/chat/message",
                json={
                    "session_id": "fake-session",
                    "user_message": "Hello",
                    "token": "invalid-token",
                },
            )

        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()
