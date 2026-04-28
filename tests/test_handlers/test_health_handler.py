from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.dependencies import get_health_service
from app.main import app


@pytest.mark.asyncio
async def test_health_check_returns_200_when_healthy():
    mock_health_service = AsyncMock()
    mock_health_service.check_all.return_value = {
        "status": "healthy",
        "version": "0.1.0",
        "checks": {
            "database": {"status": "up", "latency_ms": 1},
            "redis": {"status": "up", "latency_ms": 1},
            "llm": {"status": "up", "provider": "mock"},
        },
    }

    app.dependency_overrides[get_health_service] = lambda: mock_health_service
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_health_check_returns_503_when_unhealthy():
    mock_health_service = AsyncMock()
    mock_health_service.check_all.return_value = {
        "status": "unhealthy",
        "version": "0.1.0",
        "checks": {
            "database": {"status": "down", "error": "database unavailable"},
            "redis": {"status": "up", "latency_ms": 1},
            "llm": {"status": "up", "provider": "mock"},
        },
    }

    app.dependency_overrides[get_health_service] = lambda: mock_health_service
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")

        assert response.status_code == 503
        body = response.json()
        assert body["status"] == "unhealthy"
        assert body["checks"]["database"]["status"] == "down"
    finally:
        app.dependency_overrides.clear()
