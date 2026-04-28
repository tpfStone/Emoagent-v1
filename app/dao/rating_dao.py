import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import UserRating


class RatingDAO:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_rating(
        self,
        session_id: str,
        rating_type: str,
        score: int,
    ) -> UserRating:
        rating = UserRating(
            session_id=uuid.UUID(session_id),
            rating_type=rating_type,
            score=score,
        )
        self.db.add(rating)
        await self.db.commit()
        await self.db.refresh(rating)
        return rating

    async def get_avg_scores(
        self, session_id: str, start: datetime, end: datetime
    ) -> dict[str, float]:
        result = await self.db.execute(
            select(UserRating.rating_type, func.avg(UserRating.score))
            .where(
                UserRating.session_id == uuid.UUID(session_id),
                UserRating.created_at >= start,
                UserRating.created_at <= end,
            )
            .group_by(UserRating.rating_type)
        )
        return {row[0]: round(float(row[1]), 1) for row in result.all()}

    async def get_missing_rate(
        self, session_id: str, start: datetime, end: datetime
    ) -> float:
        """计算自评缺失率：没有 after 评分的比率"""
        before_count = await self._count_by_type(session_id, "before", start, end)
        after_count = await self._count_by_type(session_id, "after", start, end)
        if before_count == 0:
            return 0.0
        missing = max(0, before_count - after_count)
        return round(missing / before_count, 2)

    async def _count_by_type(
        self, session_id: str, rating_type: str, start: datetime, end: datetime
    ) -> int:
        result = await self.db.execute(
            select(func.count()).where(
                UserRating.session_id == uuid.UUID(session_id),
                UserRating.rating_type == rating_type,
                UserRating.created_at >= start,
                UserRating.created_at <= end,
            )
        )
        return result.scalar_one()
