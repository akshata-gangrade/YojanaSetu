"""Health check response models."""

from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Payload returned by the /health endpoint."""

    status: Literal["ok", "degraded", "down"] = Field(
        default="ok",
        description="Overall service health status.",
    )
    environment: str = Field(
        ...,
        description="Active runtime environment name.",
    )
    version: str = Field(
        default="0.1.0",
        description="Current application version.",
    )
