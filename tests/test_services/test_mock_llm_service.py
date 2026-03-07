import pytest

from app.services.mock_llm_service import MockLLMService


@pytest.mark.asyncio
async def test_generate_response_emotion_match():
    service = MockLLMService()

    response = await service.generate_response("I feel sadness today")
    assert "tough time" in response

    response = await service.generate_response("Full of joy!")
    assert "great mood" in response


@pytest.mark.asyncio
async def test_generate_response_default():
    service = MockLLMService()
    response = await service.generate_response("Just a random message")
    assert "Thank you for sharing" in response


@pytest.mark.asyncio
async def test_health_check():
    service = MockLLMService()
    assert await service.health_check() is True
