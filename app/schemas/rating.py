from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class RatingRequest(BaseModel):
    session_id: str
    rating_type: Literal["before", "after"]
    score: int = Field(..., ge=1, le=10)
    token: str


class RatingResponse(BaseModel):
    id: int
    session_id: str
    rating_type: str
    score: int
    created_at: datetime
