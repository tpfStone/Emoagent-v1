import asyncio
import os
import uuid

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from unittest.mock import AsyncMock

# Keep tests isolated from a developer's local .env file. app.database creates
# Settings at import time, so these values must be present before importing Base.
os.environ["DATABASE_URL"] = "postgresql://test_user:test_password@localhost:5432/emoagent_test"
os.environ["DEBUG"] = "false"
os.environ["ENV"] = "testing"
os.environ["LOG_LEVEL"] = "INFO"
os.environ["LLM_PROVIDER"] = "mock"

from app.database import Base


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session

    await engine.dispose()


@pytest.fixture
def mock_llm_service():
    mock = AsyncMock()
    mock.generate_response.return_value = "Test reply from mock LLM"
    mock.health_check.return_value = True
    return mock


@pytest.fixture
def sample_session_id():
    return str(uuid.uuid4())


@pytest.fixture
def sample_token():
    return str(uuid.uuid4())
