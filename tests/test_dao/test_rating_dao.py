from datetime import UTC, datetime, timedelta

import pytest

from app.dao.rating_dao import RatingDAO
from app.dao.session_dao import SessionDAO


@pytest.mark.asyncio
async def test_create_rating(db_session):
    session_dao = SessionDAO(db_session)
    session = await session_dao.create_session()
    sid = str(session.session_id)

    dao = RatingDAO(db_session)
    rating = await dao.create_rating(session_id=sid, rating_type="before", score=5)

    assert rating.id is not None
    assert rating.score == 5
    assert rating.rating_type == "before"


@pytest.mark.asyncio
async def test_get_avg_scores(db_session):
    session_dao = SessionDAO(db_session)
    session = await session_dao.create_session()
    sid = str(session.session_id)

    dao = RatingDAO(db_session)
    await dao.create_rating(session_id=sid, rating_type="before", score=3)
    await dao.create_rating(session_id=sid, rating_type="after", score=7)

    start = datetime.now(UTC) - timedelta(hours=1)
    end = datetime.now(UTC) + timedelta(hours=1)
    scores = await dao.get_avg_scores(sid, start, end)

    assert "before" in scores
    assert "after" in scores
    assert scores["before"] == 3.0
    assert scores["after"] == 7.0


@pytest.mark.asyncio
async def test_get_missing_rate(db_session):
    session_dao = SessionDAO(db_session)
    session = await session_dao.create_session()
    sid = str(session.session_id)

    dao = RatingDAO(db_session)
    await dao.create_rating(session_id=sid, rating_type="before", score=5)
    await dao.create_rating(session_id=sid, rating_type="before", score=6)
    await dao.create_rating(session_id=sid, rating_type="after", score=7)

    start = datetime.now(UTC) - timedelta(hours=1)
    end = datetime.now(UTC) + timedelta(hours=1)
    rate = await dao.get_missing_rate(sid, start, end)

    assert rate == 0.5


@pytest.mark.asyncio
async def test_get_missing_rate_no_before(db_session):
    session_dao = SessionDAO(db_session)
    session = await session_dao.create_session()
    sid = str(session.session_id)

    dao = RatingDAO(db_session)
    start = datetime.now(UTC) - timedelta(hours=1)
    end = datetime.now(UTC) + timedelta(hours=1)
    rate = await dao.get_missing_rate(sid, start, end)

    assert rate == 0.0
