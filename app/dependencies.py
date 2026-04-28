from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.dao.crisis_dao import CrisisDAO
from app.dao.rating_dao import RatingDAO
from app.dao.session_dao import SessionDAO
from app.dao.turn_dao import TurnDAO
from app.database import get_db
from app.services.auth_service import AuthService
from app.services.chat_service import ChatService
from app.services.crisis_service import CrisisService
from app.services.deepseek_llm_service import DeepSeekLLMService
from app.services.emotion_service import EmotionService
from app.services.health_service import HealthService
from app.services.memory_service import MemoryService
from app.services.metrics_service import MetricsService
from app.services.mock_llm_service import LLMServiceProtocol, MockLLMService
from app.services.report_service import ReportService


@lru_cache
def get_settings() -> Settings:
    return Settings()


# ---- Singletons (app-lifetime) ----

_llm_service: LLMServiceProtocol | None = None
_emotion_service: EmotionService | None = None
_memory_service: MemoryService | None = None


def get_llm_service(settings: Settings = Depends(get_settings)) -> LLMServiceProtocol:
    global _llm_service
    if _llm_service is not None:
        return _llm_service

    provider = settings.LLM_PROVIDER.lower()
    if provider == "deepseek":
        _llm_service = DeepSeekLLMService(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
            model=settings.DEEPSEEK_MODEL,
        )
    else:
        _llm_service = MockLLMService()
    return _llm_service


def get_emotion_service(
    settings: Settings = Depends(get_settings),
) -> EmotionService | None:
    global _emotion_service
    if not settings.ENABLE_EMOTION_DETECTION:
        return None
    if _emotion_service is None:
        _emotion_service = EmotionService(settings)
    return _emotion_service


def get_memory_service(settings: Settings = Depends(get_settings)) -> MemoryService:
    global _memory_service
    if _memory_service is None:
        _memory_service = MemoryService(settings)
    return _memory_service


# ---- Per-request factories ----


def get_session_dao(db: AsyncSession = Depends(get_db)) -> SessionDAO:
    return SessionDAO(db)


def get_turn_dao(db: AsyncSession = Depends(get_db)) -> TurnDAO:
    return TurnDAO(db)


def get_crisis_dao(db: AsyncSession = Depends(get_db)) -> CrisisDAO:
    return CrisisDAO(db)


def get_rating_dao(db: AsyncSession = Depends(get_db)) -> RatingDAO:
    return RatingDAO(db)


def get_auth_service(session_dao: SessionDAO = Depends(get_session_dao)) -> AuthService:
    return AuthService(session_dao)


def get_crisis_service(
    crisis_dao: CrisisDAO = Depends(get_crisis_dao),
) -> CrisisService:
    return CrisisService(crisis_dao)


def get_metrics_service(turn_dao: TurnDAO = Depends(get_turn_dao)) -> MetricsService:
    return MetricsService(turn_dao)


def get_report_service(
    turn_dao: TurnDAO = Depends(get_turn_dao),
    rating_dao: RatingDAO = Depends(get_rating_dao),
) -> ReportService:
    return ReportService(turn_dao, rating_dao)


def get_chat_service(
    session_dao: SessionDAO = Depends(get_session_dao),
    crisis_service: CrisisService = Depends(get_crisis_service),
    emotion_service: EmotionService | None = Depends(get_emotion_service),
    memory_service: MemoryService = Depends(get_memory_service),
    llm_service: LLMServiceProtocol = Depends(get_llm_service),
    metrics_service: MetricsService = Depends(get_metrics_service),
    settings: Settings = Depends(get_settings),
) -> ChatService:
    return ChatService(
        auth_service=session_dao,
        crisis_service=crisis_service,
        emotion_service=emotion_service,
        memory_service=memory_service,
        llm_service=llm_service,
        metrics_service=metrics_service,
        settings=settings,
    )


def get_health_service(
    db: AsyncSession = Depends(get_db),
    memory_service: MemoryService = Depends(get_memory_service),
    llm_service: LLMServiceProtocol = Depends(get_llm_service),
    settings: Settings = Depends(get_settings),
) -> HealthService:
    return HealthService(
        db=db,
        redis_client=memory_service.redis,
        llm_service=llm_service,
        settings=settings,
    )
