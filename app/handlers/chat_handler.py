import logging

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_chat_service
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

logger = logging.getLogger("emoagent")

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    try:
        return await chat_service.process_message(
            session_id=request.session_id,
            user_message=request.user_message,
            token=request.token,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.exception("Unhandled error in send_message")
        raise HTTPException(status_code=500, detail=str(e))
