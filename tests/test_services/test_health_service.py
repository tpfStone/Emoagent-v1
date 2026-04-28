from unittest.mock import AsyncMock, Mock

import pytest

from app.config import Settings
from app.services.health_service import HealthService


def make_service(
    *,
    db_execute_side_effect=None,
    redis_ping_side_effect=None,
    llm_health_result=True,
    llm_health_side_effect=None,
) -> HealthService:
    db = AsyncMock()
    db_result = Mock()
    db_result.scalar.return_value = 1
    db.execute.return_value = db_result
    if db_execute_side_effect is not None:
        db.execute.side_effect = db_execute_side_effect

    redis_client = AsyncMock()
    redis_client.ping.return_value = True
    if redis_ping_side_effect is not None:
        redis_client.ping.side_effect = redis_ping_side_effect

    llm_service = AsyncMock()
    llm_service.health_check.return_value = llm_health_result
    if llm_health_side_effect is not None:
        llm_service.health_check.side_effect = llm_health_side_effect

    return HealthService(
        db=db,
        redis_client=redis_client,
        llm_service=llm_service,
        settings=Settings(LLM_PROVIDER="mock"),
    )


@pytest.mark.asyncio
async def test_check_database_up():
    service = make_service()

    result = await service.check_database()

    assert result["status"] == "up"
    assert "latency_ms" in result


@pytest.mark.asyncio
async def test_check_database_down():
    service = make_service(db_execute_side_effect=RuntimeError("database unavailable"))

    result = await service.check_database()

    assert result["status"] == "down"
    assert "database unavailable" in result["error"]


@pytest.mark.asyncio
async def test_check_redis_up():
    service = make_service()

    result = await service.check_redis()

    assert result["status"] == "up"
    assert "latency_ms" in result


@pytest.mark.asyncio
async def test_check_redis_down():
    service = make_service(redis_ping_side_effect=RuntimeError("redis unavailable"))

    result = await service.check_redis()

    assert result["status"] == "down"
    assert "redis unavailable" in result["error"]


@pytest.mark.asyncio
async def test_check_llm_up():
    service = make_service(llm_health_result=True)

    result = await service.check_llm()

    assert result == {"status": "up", "provider": "mock"}


@pytest.mark.asyncio
async def test_check_llm_degraded():
    service = make_service(llm_health_result=False)

    result = await service.check_llm()

    assert result == {"status": "degraded", "provider": "mock"}


@pytest.mark.asyncio
async def test_check_llm_down():
    service = make_service(llm_health_side_effect=RuntimeError("llm unavailable"))

    result = await service.check_llm()

    assert result["status"] == "down"
    assert result["provider"] == "mock"
    assert "llm unavailable" in result["error"]


@pytest.mark.asyncio
async def test_check_all_treats_degraded_llm_as_healthy():
    service = make_service(llm_health_result=False)

    result = await service.check_all()

    assert result["status"] == "healthy"
    assert result["checks"]["database"]["status"] == "up"
    assert result["checks"]["redis"]["status"] == "up"
    assert result["checks"]["llm"]["status"] == "degraded"


@pytest.mark.asyncio
async def test_check_all_unhealthy_when_database_down():
    service = make_service(db_execute_side_effect=RuntimeError("database unavailable"))

    result = await service.check_all()

    assert result["status"] == "unhealthy"
    assert result["checks"]["database"]["status"] == "down"


@pytest.mark.asyncio
async def test_check_all_unhealthy_when_redis_down():
    service = make_service(redis_ping_side_effect=RuntimeError("redis unavailable"))

    result = await service.check_all()

    assert result["status"] == "unhealthy"
    assert result["checks"]["redis"]["status"] == "down"
