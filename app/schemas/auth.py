from pydantic import BaseModel


class AuthResponse(BaseModel):
    token: str
    session_id: str
