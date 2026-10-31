"""Citizen intake router for natural language profile parsing."""

from fastapi import APIRouter, Depends

from app.api.deps import get_intake_service
from app.core.rate_limit import rate_limit_intake_dependency
from app.schemas.api import IntakeExtractRequest, IntakeExtractResponse
from app.services.intake_service import IntakeService

router = APIRouter(prefix="/intake", tags=["Intake"])


@router.post(
    "/extract",
    response_model=IntakeExtractResponse,
    dependencies=[Depends(rate_limit_intake_dependency)],
    summary="Extract demographic criteria and suggest follow-up questions",
)
async def extract_citizen_intake(
    request: IntakeExtractRequest,
    intake_service: IntakeService = Depends(get_intake_service),
) -> IntakeExtractResponse:
    """Extract profile attributes from citizen message and calculate next question."""
    return await intake_service.process_intake(
        message=request.message,
        language=request.language,
        current_profile=request.current_profile,
    )
