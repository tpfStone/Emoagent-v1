import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Turn


class TurnDAO:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_turn(
        self,
        session_id: str,
        turn_index: int,
        user_message: str,
        assistant_message: str,
        emotion_label: str | None,
        is_crisis: bool,
        bert_latency_ms: int | None,
        llm_latency_ms: int | None,
    ) -> Turn:
        turn = Turn(
            session_id=uuid.UUID(session_id),
            turn_index=turn_index,
            user_message=user_message,
            assistant_message=assistant_message,
            emotion_label=emotion_label,
            is_crisis=is_crisis,
            bert_latency_ms=bert_latency_ms,
            llm_latency_ms=llm_latency_ms,
        )
        self.db.add(turn)
        await self.db.commit()
        await self.db.refresh(turn)
        return turn

    async def get_turns_by_session(self, session_id: str, limit: int | None = None) -> list[Turn]:
        query = (
            select(Turn)
            .where(Turn.session_id == uuid.UUID(session_id))
            .order_by(Turn.turn_index.desc())
        )
        if limit:
            query = query.limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_next_turn_index(self, session_id: str) -> int:
        result = await self.db.execute(
            select(func.coalesce(func.max(Turn.turn_index), 0))
            .where(Turn.session_id == uuid.UUID(session_id))
        )
        return result.scalar_one() + 1

    async def get_turns_in_range(
        self, session_id: str, start: datetime, end: datetime
    ) -> list[Turn]:
        result = await self.db.execute(
            select(Turn)
            .where(
                Turn.session_id == uuid.UUID(session_id),
                Turn.created_at >= start,
                Turn.created_at <= end,
            )
            .order_by(Turn.turn_index)
        )
        return list(result.scalars().all())

    async def get_emotion_distribution(
        self, session_id: str, start: datetime, end: datetime
    ) -> dict[str, int]:
        result = await self.db.execute(
            select(Turn.emotion_label, func.count())
            .where(
                Turn.session_id == uuid.UUID(session_id),
                Turn.created_at >= start,
                Turn.created_at <= end,
                Turn.emotion_label.isnot(None),
            )
            .group_by(Turn.emotion_label)
        )
        return {row[0]: row[1] for row in result.all()}

    async def count_crisis_turns(
        self, session_id: str, start: datetime, end: datetime
    ) -> int:
        result = await self.db.execute(
            select(func.count())
            .where(
                Turn.session_id == uuid.UUID(session_id),
                Turn.created_at >= start,
                Turn.created_at <= end,
                Turn.is_crisis.is_(True),
            )
        )
        return result.scalar_one()

    async def get_avg_latencies(
        self, session_id: str, start: datetime, end: datetime
    ) -> dict[str, int]:
        result = await self.db.execute(
            select(
                func.coalesce(func.avg(Turn.bert_latency_ms), 0),
                func.coalesce(func.avg(Turn.llm_latency_ms), 0),
            ).where(
                Turn.session_id == uuid.UUID(session_id),
                Turn.created_at >= start,
                Turn.created_at <= end,
            )
        )
        row = result.one()
        return {"bert": int(row[0]), "llm": int(row[1])}
