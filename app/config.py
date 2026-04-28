from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://emoagent_user:password@localhost:5432/emoagent"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # LLM
    LLM_PROVIDER: str = "mock"
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    QIANWEN_API_KEY: str = ""
    LLM_TIMEOUT: float = 10.0
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 1000

    # BERT
    BERT_MODEL_PATH: str = "./models/bert-emotion"
    BERT_MODEL_NAME: str = "nateraw/bert-base-uncased-emotion"
    BERT_DEVICE: str = "cpu"
    ENABLE_EMOTION_DETECTION: bool = True

    # App
    ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "dev-secret-key"
    HOST: str = "0.0.0.0"
    PORT: int = 8200

    # CORS
    CORS_ORIGINS: str = (
        "http://localhost:3000,http://localhost:5173,http://localhost:5174"
    )

    # Memory
    MEMORY_TTL: int = 86400
    MEMORY_MAX_TURNS: int = 6

    # Crisis
    CRISIS_RULES_CACHE_TTL: int = 3600
    CRISIS_DETECTION_ENABLED: bool = True

    # DB Pool
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30

    # Feature flags
    ENABLE_API_DOCS: bool = True

    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PATH: str = "/metrics"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    @property
    def async_database_url(self) -> str:
        """将 postgresql:// 转换为 postgresql+asyncpg:// 供异步引擎使用"""
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()
        ]
