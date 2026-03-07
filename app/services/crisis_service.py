import re
import logging
from dataclasses import dataclass

from app.dao.crisis_dao import CrisisDAO

logger = logging.getLogger("emoagent")


@dataclass
class CrisisResult:
    is_crisis: bool
    response: str | None = None
    matched_keyword: str | None = None


class CrisisService:
    def __init__(self, crisis_dao: CrisisDAO):
        self.crisis_dao = crisis_dao
        self._cached_rules: list | None = None

    async def check_crisis(self, user_message: str) -> CrisisResult:
        rules = await self._get_rules()
        text_lower = user_message.lower()

        for rule in rules:
            try:
                if re.search(rule.keyword, text_lower, re.IGNORECASE):
                    logger.warning(
                        "Crisis keyword matched",
                        extra={"keyword": rule.keyword, "priority": rule.priority},
                    )
                    return CrisisResult(
                        is_crisis=True,
                        response=rule.response_template,
                        matched_keyword=rule.keyword,
                    )
            except re.error:
                logger.error(f"Invalid regex in crisis rule: {rule.keyword}")
                continue

        return CrisisResult(is_crisis=False)

    async def _get_rules(self):
        if self._cached_rules is None:
            self._cached_rules = await self.crisis_dao.get_enabled_rules()
        return self._cached_rules

    def invalidate_cache(self):
        self._cached_rules = None
