from datetime import datetime
from typing import cast

from fastapi import APIRouter, Depends, HTTPException

from app.dao.rating_dao import RatingDAO
from app.dao.session_dao import SessionDAO
from app.dependencies import get_rating_dao, get_session_dao
from app.schemas.rating import RatingRequest, RatingResponse
from app.utils.metrics import rating_score_distribution, rating_submissions

router = APIRouter(prefix="/api/ratings", tags=["ratings"])


@router.post("", response_model=RatingResponse)
async def submit_rating(
    request: RatingRequest,
    rating_dao: RatingDAO = Depends(get_rating_dao),
    session_dao: SessionDAO = Depends(get_session_dao),
) -> RatingResponse:
    valid = await session_dao.validate_token(request.session_id, request.token)
    if not valid:
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        rating = await rating_dao.create_rating(
            session_id=request.session_id,
            rating_type=request.rating_type,
            score=request.score,
        )

        rating_submissions.labels(type=request.rating_type).inc()
        rating_score_distribution.labels(type=request.rating_type).observe(
            request.score
        )

        return RatingResponse(
            id=cast(int, rating.id),
            session_id=str(rating.session_id),
            rating_type=cast(str, rating.rating_type),
            score=cast(int, rating.score),
            created_at=cast(datetime, rating.created_at),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
