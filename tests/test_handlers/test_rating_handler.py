import pytest
from unittest.mock import AsyncMock

from httpx import ASGITransport, AsyncClient

from app.main import app
from app.dependencies import get_rating_dao, get_session_dao


@pytest.mark.asyncio
async def test_submit_rating_success():
    mock_session_dao = AsyncMock()
    mock_session_dao.validate_token.return_value = True

    mock_rating_dao = AsyncMock()
    mock_rating_dao.create_rating.return_value = AsyncMock(
        id=1,
        session_id="test-session-uuid",
        rating_type="before",
        score=7,
        created_at="2026-03-06T00:00:00",
    )

    app.dependency_overrides[get_session_dao] = lambda: mock_session_dao
    app.dependency_overrides[get_rating_dao] = lambda: mock_rating_dao
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/ratings",
                json={
                    "session_id": "test-session",
                    "rating_type": "before",
                    "score": 7,
                    "token": "test-token",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["score"] == 7
        assert data["rating_type"] == "before"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_submit_rating_invalid_token():
    mock_session_dao = AsyncMock()
    mock_session_dao.validate_token.return_value = False

    mock_rating_dao = AsyncMock()

    app.dependency_overrides[get_session_dao] = lambda: mock_session_dao
    app.dependency_overrides[get_rating_dao] = lambda: mock_rating_dao
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/ratings",
                json={
                    "session_id": "test-session",
                    "rating_type": "before",
                    "score": 5,
                    "token": "bad-token",
                },
            )

        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()
