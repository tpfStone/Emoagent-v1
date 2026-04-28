from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.crisis_service import CrisisService


def _make_rule(keyword: str, response: str, priority: int = 100):
    rule = MagicMock()
    rule.keyword = keyword
    rule.response_template = response
    rule.priority = priority
    if hasattr(rule, "category"):
        del rule.category
    return rule


@pytest.mark.asyncio
async def test_check_crisis_matches():
    mock_dao = AsyncMock()
    mock_dao.get_enabled_rules.return_value = [
        _make_rule(
            r"(suicide|kill myself|end my life)",
            "Please call the crisis hotline",
            100,
        ),
    ]

    service = CrisisService(mock_dao)
    result = await service.check_crisis("I want to end my life")

    assert result.is_crisis is True
    assert "crisis hotline" in result.response
    assert result.matched_keyword == r"(suicide|kill myself|end my life)"


@pytest.mark.asyncio
async def test_check_crisis_no_match():
    mock_dao = AsyncMock()
    mock_dao.get_enabled_rules.return_value = [
        _make_rule(r"(suicide|kill myself)", "Crisis response", 100),
    ]

    service = CrisisService(mock_dao)
    result = await service.check_crisis("I had a great day today")

    assert result.is_crisis is False
    assert result.response is None


@pytest.mark.asyncio
async def test_check_crisis_invalid_regex():
    mock_dao = AsyncMock()
    mock_dao.get_enabled_rules.return_value = [
        _make_rule("[invalid regex(", "Bad rule", 100),
        _make_rule(r"(suicide)", "Valid rule", 90),
    ]

    service = CrisisService(mock_dao)
    result = await service.check_crisis("suicide")

    assert result.is_crisis is True
