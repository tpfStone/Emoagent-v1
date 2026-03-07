import uuid
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Session


class SessionDAO:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(self) -> Session:
        token = str(uuid.uuid4())
        session_id = uuid.uuid4()
        session = Session(session_id=session_id, token=token)
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get_by_token(self, token: str) -> Session | None:
        result = await self.db.execute(select(Session).where(Session.token == token))
        return result.scalar_one_or_none()

    async def get_by_session_id(self, session_id: str) -> Session | None:
        result = await self.db.execute(
            select(Session).where(Session.session_id == uuid.UUID(session_id))
        )
        return result.scalar_one_or_none()

    async def update_last_active(self, session_id: str) -> None:
        await self.db.execute(
            update(Session)
            .where(Session.session_id == uuid.UUID(session_id))
            .values(last_active_at=datetime.now(UTC))
        )
        await self.db.commit()

    async def validate_token(self, session_id: str, token: str) -> bool:
        result = await self.db.execute(
            select(Session).where(
                Session.session_id == uuid.UUID(session_id),
                Session.token == token,
            )
        )
        return result.scalar_one_or_none() is not None
