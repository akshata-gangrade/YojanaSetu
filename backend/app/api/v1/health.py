"""Health check router for container orchestration and uptime monitoring."""

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.schemas.health import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def check_health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """Return application operational status and active environment."""
    return HealthResponse(
        status="ok",
        environment=settings.ENV,
        version="0.1.0",
    )
