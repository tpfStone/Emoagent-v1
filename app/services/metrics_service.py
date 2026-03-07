import logging

from app.dao.turn_dao import TurnDAO

logger = logging.getLogger("emoagent")


class MetricsService:
    def __init__(self, turn_dao: TurnDAO):
        self.turn_dao = turn_dao

    async def log_turn(
        self,
        session_id: str,
        turn_index: int,
        user_message: str,
        assistant_message: str,
        emotion_label: str | None,
        is_crisis: bool,
        bert_latency_ms: int | None,
        llm_latency_ms: int | None,
    ) -> None:
        await self.turn_dao.create_turn(
            session_id=session_id,
            turn_index=turn_index,
            user_message=user_message,
            assistant_message=assistant_message,
            emotion_label=emotion_label,
            is_crisis=is_crisis,
            bert_latency_ms=bert_latency_ms,
            llm_latency_ms=llm_latency_ms,
        )
        logger.info(
            "Turn logged",
            extra={
                "session_id": session_id,
                "turn_index": turn_index,
                "emotion": emotion_label,
                "is_crisis": is_crisis,
            },
        )
