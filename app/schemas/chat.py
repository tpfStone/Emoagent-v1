from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str
    user_message: str = Field(..., min_length=1)
    token: str


class ChatResponse(BaseModel):
    assistant_message: str
    emotion_label: str | None
    is_crisis: bool
    turn_index: int
