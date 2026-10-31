"""Administrative router for scheme verification, auditing, and ingestion."""

from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["Admin"])
