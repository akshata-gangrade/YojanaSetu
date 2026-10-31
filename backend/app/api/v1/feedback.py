"""Citizen feedback router for accuracy ratings and user experiences."""

from fastapi import APIRouter, Depends, status

from app.api.deps import get_feedback_repo
from app.core.rate_limit import rate_limit_dependency
from app.repositories.base import IFeedbackRepository
from app.schemas.api import FeedbackResponse
from app.schemas.feedback import FeedbackCreate

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post(
    "",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit_dependency)],
    summary="Submit anonymous helpfulness feedback for a scheme",
)
async def submit_feedback(
    request: FeedbackCreate,
    feedback_repo: IFeedbackRepository = Depends(get_feedback_repo),
) -> FeedbackResponse:
    """Record anonymous citizen feedback without any personal identifiers."""
    saved = await feedback_repo.create_feedback(request)
    return FeedbackResponse(status="ok", id=saved.id)
