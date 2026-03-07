from app.dao.session_dao import SessionDAO


class AuthService:
    def __init__(self, session_dao: SessionDAO):
        self.session_dao = session_dao

    async def create_anonymous_session(self) -> dict[str, str]:
        session = await self.session_dao.create_session()
        return {
            "token": session.token,
            "session_id": str(session.session_id),
        }

    async def validate_token(self, session_id: str, token: str) -> bool:
        return await self.session_dao.validate_token(session_id, token)
