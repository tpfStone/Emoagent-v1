import pytest

from app.dao.session_dao import SessionDAO


@pytest.mark.asyncio
async def test_create_session(db_session):
    dao = SessionDAO(db_session)
    session = await dao.create_session()

    assert session.id is not None
    assert session.session_id is not None
    assert session.token is not None
    assert len(session.token) == 36  # UUID format


@pytest.mark.asyncio
async def test_get_by_token(db_session):
    dao = SessionDAO(db_session)
    created = await dao.create_session()

    found = await dao.get_by_token(created.token)
    assert found is not None
    assert found.session_id == created.session_id


@pytest.mark.asyncio
async def test_get_by_token_not_found(db_session):
    dao = SessionDAO(db_session)
    found = await dao.get_by_token("nonexistent-token")
    assert found is None


@pytest.mark.asyncio
async def test_validate_token(db_session):
    dao = SessionDAO(db_session)
    created = await dao.create_session()

    valid = await dao.validate_token(str(created.session_id), created.token)
    assert valid is True

    invalid = await dao.validate_token(str(created.session_id), "wrong-token")
    assert invalid is False


@pytest.mark.asyncio
async def test_get_by_session_id(db_session):
    dao = SessionDAO(db_session)
    created = await dao.create_session()

    found = await dao.get_by_session_id(str(created.session_id))
    assert found is not None
    assert found.token == created.token


@pytest.mark.asyncio
async def test_get_by_session_id_not_found(db_session):
    dao = SessionDAO(db_session)
    import uuid

    found = await dao.get_by_session_id(str(uuid.uuid4()))
    assert found is None


@pytest.mark.asyncio
async def test_update_last_active(db_session):
    dao = SessionDAO(db_session)
    created = await dao.create_session()
    original_active = created.last_active_at.replace(tzinfo=None)

    await dao.update_last_active(str(created.session_id))

    updated = await dao.get_by_session_id(str(created.session_id))
    assert updated is not None
    assert updated.last_active_at.replace(tzinfo=None) >= original_active
