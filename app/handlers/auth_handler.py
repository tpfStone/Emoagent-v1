from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_auth_service
from app.schemas.auth import AuthResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/anonymous", response_model=AuthResponse)
async def create_anonymous_session(
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    try:
        result = await auth_service.create_anonymous_session()
        return AuthResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
