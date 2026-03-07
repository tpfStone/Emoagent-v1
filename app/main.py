from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings
from app.handlers import auth_handler, chat_handler, rating_handler, report_handler
from app.utils.logging import setup_logger

settings = Settings()
logger = setup_logger(settings.LOG_LEVEL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "EmoAgent starting",
        extra={"env": settings.ENV, "llm_provider": settings.LLM_PROVIDER},
    )
    yield
    logger.info("EmoAgent shutting down")


app = FastAPI(
    title="EmoAgent - 情绪对话系统",
    version="0.1.0",
    docs_url="/docs" if settings.ENABLE_API_DOCS else None,
    redoc_url="/redoc" if settings.ENABLE_API_DOCS else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(auth_handler.router)
app.include_router(chat_handler.router)
app.include_router(rating_handler.router)
app.include_router(report_handler.router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0", "llm_provider": settings.LLM_PROVIDER}
