"""
Health check service for monitoring system components
"""

import logging
import time
from typing import Any

import redis.asyncio as aioredis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.services.mock_llm_service import LLMServiceProtocol

logger = logging.getLogger("emoagent")


class HealthService:
    def __init__(
        self,
        db: AsyncSession,
        redis_client: aioredis.Redis,
        llm_service: LLMServiceProtocol,
        settings: Settings,
    ):
        self.db = db
        self.redis_client = redis_client
        self.llm_service = llm_service
        self.settings = settings

    async def check_database(self) -> dict[str, Any]:
        try:
            start = time.perf_counter()
            result = await self.db.execute(text("SELECT 1"))
            result.scalar()
            latency_ms = int((time.perf_counter() - start) * 1000)
            return {"status": "up", "latency_ms": latency_ms}
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {"status": "down", "error": str(e)}

    async def check_redis(self) -> dict[str, Any]:
        try:
            start = time.perf_counter()
            await self.redis_client.ping()
            latency_ms = int((time.perf_counter() - start) * 1000)
            return {"status": "up", "latency_ms": latency_ms}
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {"status": "down", "error": str(e)}

    async def check_llm(self) -> dict[str, Any]:
        try:
            if hasattr(self.llm_service, "health_check"):
                is_healthy = await self.llm_service.health_check()
                if is_healthy:
                    return {
                        "status": "up",
                        "provider": self.settings.LLM_PROVIDER,
                    }
                else:
                    return {
                        "status": "degraded",
                        "provider": self.settings.LLM_PROVIDER,
                    }
            else:
                return {
                    "status": "up",
                    "provider": self.settings.LLM_PROVIDER,
                    "note": "health_check not implemented",
                }
        except Exception as e:
            logger.error(f"LLM health check failed: {e}")
            return {"status": "down", "provider": self.settings.LLM_PROVIDER, "error": str(e)}

    async def check_all(self) -> dict[str, Any]:
        db_check = await self.check_database()
        redis_check = await self.check_redis()
        llm_check = await self.check_llm()

        all_up = (
            db_check["status"] == "up"
            and redis_check["status"] == "up"
            and llm_check["status"] in ["up", "degraded"]
        )

        return {
            "status": "healthy" if all_up else "unhealthy",
            "version": "0.1.0",
            "checks": {
                "database": db_check,
                "redis": redis_check,
                "llm": llm_check,
            },
        }
