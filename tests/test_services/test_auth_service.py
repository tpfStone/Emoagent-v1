import pytest

from app.dao.session_dao import SessionDAO
from app.services.auth_service import AuthService


@pytest.mark.asyncio
async def test_create_anonymous_session(db_session):
    dao = SessionDAO(db_session)
    service = AuthService(dao)

    result = await service.create_anonymous_session()

    assert "token" in result
    assert "session_id" in result
    assert len(result["token"]) == 36
    assert len(result["session_id"]) == 36


@pytest.mark.asyncio
async def test_validate_token(db_session):
    dao = SessionDAO(db_session)
    service = AuthService(dao)

    result = await service.create_anonymous_session()
    valid = await service.validate_token(result["session_id"], result["token"])
    assert valid is True

    invalid = await service.validate_token(result["session_id"], "wrong-token")
    assert invalid is False
