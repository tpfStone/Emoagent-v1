from datetime import UTC, datetime, timedelta

import pytest

from app.dao.session_dao import SessionDAO
from app.dao.turn_dao import TurnDAO


@pytest.mark.asyncio
async def test_create_turn(db_session):
    session_dao = SessionDAO(db_session)
    session = await session_dao.create_session()
    sid = str(session.session_id)

    dao = TurnDAO(db_session)
    turn = await dao.create_turn(
        session_id=sid,
        turn_index=1,
        user_message="Hello",
        assistant_message="Hi there!",
        emotion_label="joy",
        is_crisis=False,
        bert_latency_ms=98,
        llm_latency_ms=350,
    )

    assert turn.id is not None
    assert turn.turn_index == 1
    assert turn.emotion_label == "joy"


@pytest.mark.asyncio
async def test_get_turns_by_session(db_session):
    session_dao = SessionDAO(db_session)
    session = await session_dao.create_session()
    sid = str(session.session_id)

    dao = TurnDAO(db_session)
    await dao.create_turn(
        session_id=sid,
        turn_index=1,
        user_message="msg1",
        assistant_message="reply1",
        emotion_label="joy",
        is_crisis=False,
        bert_latency_ms=50,
        llm_latency_ms=300,
    )
    await dao.create_turn(
        session_id=sid,
        turn_index=2,
        user_message="msg2",
        assistant_message="reply2",
        emotion_label="sadness",
        is_crisis=False,
        bert_latency_ms=60,
        llm_latency_ms=400,
    )

    turns = await dao.get_turns_by_session(sid)
    assert len(turns) == 2


@pytest.mark.asyncio
async def test_get_next_turn_index(db_session):
    session_dao = SessionDAO(db_session)
    session = await session_dao.create_session()
    sid = str(session.session_id)

    dao = TurnDAO(db_session)
    idx = await dao.get_next_turn_index(sid)
    assert idx == 1

    await dao.create_turn(
        session_id=sid,
        turn_index=1,
        user_message="msg",
        assistant_message="reply",
        emotion_label=None,
        is_crisis=False,
        bert_latency_ms=None,
        llm_latency_ms=None,
    )
    idx = await dao.get_next_turn_index(sid)
    assert idx == 2


async def _seed_turns(db_session):
    """Helper to create a session with several turns for range queries."""
    session_dao = SessionDAO(db_session)
    session = await session_dao.create_session()
    sid = str(session.session_id)
    dao = TurnDAO(db_session)

    await dao.create_turn(
        session_id=sid,
        turn_index=1,
        user_message="I'm happy",
        assistant_message="Great!",
        emotion_label="joy",
        is_crisis=False,
        bert_latency_ms=40,
        llm_latency_ms=1000,
    )
    await dao.create_turn(
        session_id=sid,
        turn_index=2,
        user_message="I'm scared",
        assistant_message="It's okay",
        emotion_label="fear",
        is_crisis=False,
        bert_latency_ms=50,
        llm_latency_ms=1200,
    )
    await dao.create_turn(
        session_id=sid,
        turn_index=3,
        user_message="I want to die",
        assistant_message="Crisis help",
        emotion_label="sadness",
        is_crisis=True,
        bert_latency_ms=60,
        llm_latency_ms=800,
    )
    return sid, dao


@pytest.mark.asyncio
async def test_get_turns_in_range(db_session):
    sid, dao = await _seed_turns(db_session)
    start = datetime.now(UTC) - timedelta(hours=1)
    end = datetime.now(UTC) + timedelta(hours=1)

    turns = await dao.get_turns_in_range(sid, start, end)
    assert len(turns) == 3


@pytest.mark.asyncio
async def test_get_emotion_distribution(db_session):
    sid, dao = await _seed_turns(db_session)
    start = datetime.now(UTC) - timedelta(hours=1)
    end = datetime.now(UTC) + timedelta(hours=1)

    dist = await dao.get_emotion_distribution(sid, start, end)
    assert dist["joy"] == 1
    assert dist["fear"] == 1
    assert dist["sadness"] == 1


@pytest.mark.asyncio
async def test_count_crisis_turns(db_session):
    sid, dao = await _seed_turns(db_session)
    start = datetime.now(UTC) - timedelta(hours=1)
    end = datetime.now(UTC) + timedelta(hours=1)

    count = await dao.count_crisis_turns(sid, start, end)
    assert count == 1


@pytest.mark.asyncio
async def test_get_avg_latencies(db_session):
    sid, dao = await _seed_turns(db_session)
    start = datetime.now(UTC) - timedelta(hours=1)
    end = datetime.now(UTC) + timedelta(hours=1)

    latencies = await dao.get_avg_latencies(sid, start, end)
    assert latencies["bert"] == 50
    assert latencies["llm"] == 1000
