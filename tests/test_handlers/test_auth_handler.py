import pytest
from unittest.mock import AsyncMock

from httpx import ASGITransport, AsyncClient

from app.main import app
from app.dependencies import get_auth_service


@pytest.mark.asyncio
async def test_create_anonymous_session():
    mock_auth = AsyncMock()
    mock_auth.create_anonymous_session.return_value = {
        "token": "test-token-uuid",
        "session_id": "test-session-uuid",
    }

    app.dependency_overrides[get_auth_service] = lambda: mock_auth
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/auth/anonymous")

        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "session_id" in data
    finally:
        app.dependency_overrides.clear()
