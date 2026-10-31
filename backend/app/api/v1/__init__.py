"""API v1 routers package."""

from fastapi import APIRouter

from app.api.v1.admin import router as admin_router
from app.api.v1.feedback import router as feedback_router
from app.api.v1.health import router as health_router
from app.api.v1.intake import router as intake_router
from app.api.v1.match import router as match_router
from app.api.v1.qa import router as qa_router
from app.api.v1.schemes import router as schemes_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(intake_router)
api_router.include_router(match_router)
api_router.include_router(schemes_router)
api_router.include_router(qa_router)
api_router.include_router(feedback_router)
api_router.include_router(admin_router)
