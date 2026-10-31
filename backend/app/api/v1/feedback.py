"""Citizen feedback router for accuracy ratings and user experiences."""

from fastapi import APIRouter

router = APIRouter(prefix="/feedback", tags=["Feedback"])
