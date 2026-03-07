import json
import logging

import redis.asyncio as aioredis

from app.config import Settings

logger = logging.getLogger("emoagent")


class MemoryService:
    def __init__(self, settings: Settings):
        self.redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        self.max_turns = settings.MEMORY_MAX_TURNS
        self.ttl = settings.MEMORY_TTL

    def _key(self, session_id: str) -> str:
        return f"memory:{session_id}"

    async def get_recent_turns(self, session_id: str) -> list[dict]:
        key = self._key(session_id)
        data = await self.redis.get(key)
        if data is None:
            return []
        try:
            turns = json.loads(data)
            return turns[-self.max_turns :]
        except (json.JSONDecodeError, TypeError):
            logger.warning(f"Invalid memory data for {session_id}")
            return []

    async def add_turn(
        self,
        session_id: str,
        turn_index: int,
        user_message: str,
        assistant_message: str,
        emotion: str | None,
    ) -> None:
        key = self._key(session_id)
        turns = await self.get_recent_turns(session_id)

        turns.append(
            {
                "turn": turn_index,
                "user": user_message,
                "assistant": assistant_message,
                "emotion": emotion,
            }
        )

        # 只保留最近 max_turns 轮
        turns = turns[-self.max_turns :]
        await self.redis.set(key, json.dumps(turns), ex=self.ttl)

    async def clear(self, session_id: str) -> None:
        await self.redis.delete(self._key(session_id))
