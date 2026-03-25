import logging
import time
from functools import lru_cache
from pathlib import Path

from app.config import Settings
from app.dao.session_dao import SessionDAO
from app.schemas.chat import ChatResponse
from app.services.crisis_service import CrisisService
from app.services.emotion_service import EmotionService
from app.services.memory_service import MemoryService
from app.services.metrics_service import MetricsService
from app.services.mock_llm_service import LLMServiceProtocol
from app.services.prompt_builder import build_emotion_prompt
from app.services.response_parser import extract_ai_response
from app.utils.metrics import messages_total, api_latency

logger = logging.getLogger("emoagent")

FALLBACK_PATH = Path(__file__).resolve().parents[2] / "config" / "llm_fallback_responses.md"


class ChatService:
    def __init__(
        self,
        auth_service: SessionDAO,
        crisis_service: CrisisService,
        emotion_service: EmotionService | None,
        memory_service: MemoryService,
        llm_service: LLMServiceProtocol,
        metrics_service: MetricsService,
        settings: Settings,
    ):
        self.auth_service = auth_service
        self.crisis_service = crisis_service
        self.emotion_service = emotion_service
        self.memory_service = memory_service
        self.llm_service = llm_service
        self.metrics_service = metrics_service
        self.settings = settings

    async def process_message(
        self, session_id: str, user_message: str, token: str
    ) -> ChatResponse:
        start_time = time.perf_counter()
        
        # 1. 验证 token
        valid = await self.auth_service.validate_token(session_id, token)
        if not valid:
            raise PermissionError("Invalid token")

        # 更新活跃时间
        await self.auth_service.update_last_active(session_id)

        # 从数据库获取下一个 turn_index（避免与 Redis 计数不一致导致唯一约束冲突）
        turn_index = await self.metrics_service.turn_dao.get_next_turn_index(session_id)
        
        messages_total.inc()

        # 2. 危机检测
        if self.settings.CRISIS_DETECTION_ENABLED:
            crisis_result = await self.crisis_service.check_crisis(user_message)
            if crisis_result.is_crisis:
                await self.metrics_service.log_turn(
                    session_id=session_id,
                    turn_index=turn_index,
                    user_message=user_message,
                    assistant_message=crisis_result.response or "",
                    emotion_label=None,
                    is_crisis=True,
                    bert_latency_ms=None,
                    llm_latency_ms=None,
                )
                return ChatResponse(
                    assistant_message=crisis_result.response or "",
                    emotion_label=None,
                    is_crisis=True,
                    turn_index=turn_index,
                )

        # 3. 情绪识别
        emotion_label: str | None = None
        bert_latency_ms: int | None = None
        if self.emotion_service and self.settings.ENABLE_EMOTION_DETECTION:
            try:
                emotion_label, bert_latency_ms = await self.emotion_service.classify_emotion(user_message)
            except Exception as e:
                logger.error(f"Emotion classification failed: {e}")

        # 4. 获取短期记忆
        memory = await self.memory_service.get_recent_turns(session_id)

        # 5. 构建 prompt
        prompt = build_emotion_prompt(
            user_message=user_message,
            emotion=emotion_label or "neutral",
            memory=memory,
        )

        # 6. 调用 LLM
        llm_start = time.perf_counter()
        try:
            raw_response = await self.llm_service.generate_response(
                prompt=prompt,
                timeout=self.settings.LLM_TIMEOUT,
                temperature=self.settings.LLM_TEMPERATURE,
                max_tokens=self.settings.LLM_MAX_TOKENS,
            )
            assistant_message = extract_ai_response(raw_response)
        except (TimeoutError, RuntimeError) as e:
            logger.warning(f"LLM call failed, using fallback: {e}")
            assistant_message = self._get_fallback_response(emotion_label or "neutral")
        llm_latency_ms = int((time.perf_counter() - llm_start) * 1000)

        # 7. 更新记忆
        await self.memory_service.add_turn(
            session_id=session_id,
            turn_index=turn_index,
            user_message=user_message,
            assistant_message=assistant_message,
            emotion=emotion_label,
        )

        # 8. 落库
        await self.metrics_service.log_turn(
            session_id=session_id,
            turn_index=turn_index,
            user_message=user_message,
            assistant_message=assistant_message,
            emotion_label=emotion_label,
            is_crisis=False,
            bert_latency_ms=bert_latency_ms,
            llm_latency_ms=llm_latency_ms,
        )

        # 记录API延迟
        elapsed = time.perf_counter() - start_time
        api_latency.labels(endpoint='/chat/message').observe(elapsed)

        return ChatResponse(
            assistant_message=assistant_message,
            emotion_label=emotion_label,
            is_crisis=False,
            turn_index=turn_index,
        )

    def _get_fallback_response(self, emotion: str) -> str:
        fallback_map = self._load_fallback_map()
        return fallback_map.get(
            emotion.lower(),
            fallback_map.get("default", "Thank you for sharing. I'm here for you."),
        )

    @staticmethod
    @lru_cache(maxsize=1)
    def _load_fallback_map() -> dict[str, str]:
        """解析 config/llm_fallback_responses.md"""
        if not FALLBACK_PATH.exists():
            return {}
        content = FALLBACK_PATH.read_text(encoding="utf-8")
        result: dict[str, str] = {}
        current_emotion: str | None = None
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("## "):
                # 提取 "## 1. Sadness" -> "sadness"
                parts = stripped[3:].strip().split(".", 1)
                if len(parts) == 2:
                    current_emotion = parts[1].strip().lower()
                else:
                    current_emotion = parts[0].strip().lower()
            elif current_emotion and stripped.startswith("> "):
                result[current_emotion] = stripped[2:].strip().strip('"')
                current_emotion = None
        return result
