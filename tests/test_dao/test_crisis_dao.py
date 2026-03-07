import pytest

from app.dao.crisis_dao import CrisisDAO
from app.models.models import CrisisRule


@pytest.mark.asyncio
async def test_get_enabled_rules(db_session):
    rule1 = CrisisRule(
        keyword="(suicide|kill myself)",
        response_template="Please call crisis hotline",
        priority=100,
        enabled=True,
    )
    rule2 = CrisisRule(
        keyword="(self-harm)",
        response_template="Reach out for help",
        priority=90,
        enabled=True,
    )
    rule3 = CrisisRule(
        keyword="(disabled-rule)",
        response_template="Should not appear",
        priority=80,
        enabled=False,
    )
    db_session.add_all([rule1, rule2, rule3])
    await db_session.commit()

    dao = CrisisDAO(db_session)
    rules = await dao.get_enabled_rules()

    assert len(rules) == 2
    assert rules[0].priority >= rules[1].priority
