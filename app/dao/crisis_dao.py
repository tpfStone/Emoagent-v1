from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import CrisisRule


class CrisisDAO:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_enabled_rules(self) -> list[CrisisRule]:
        result = await self.db.execute(
            select(CrisisRule)
            .where(CrisisRule.enabled.is_(True))
            .order_by(CrisisRule.priority.desc())
        )
        return list(result.scalars().all())
