"""Scheme matching router executing deterministic eligibility evaluation."""

from fastapi import APIRouter, Depends

from app.api.deps import get_match_service
from app.core.rate_limit import rate_limit_dependency
from app.schemas.api import MatchRequest, MatchResponse
from app.services.match_service import MatchService

router = APIRouter(prefix="/match", tags=["Match"])


@router.post(
    "",
    response_model=MatchResponse,
    dependencies=[Depends(rate_limit_dependency)],
    summary="Deterministically match citizen profile against verified schemes",
)
async def match_citizen_schemes(
    request: MatchRequest,
    match_service: MatchService = Depends(get_match_service),
) -> MatchResponse:
    """Evaluate profile against verified schemes in Python rule engine. Zero LLM involvement."""
    return await match_service.match_schemes(
        profile=request.profile,
        language=request.language,
    )
