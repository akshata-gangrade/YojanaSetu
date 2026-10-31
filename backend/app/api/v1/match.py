"""Scheme matching router executing deterministic eligibility evaluation."""

from fastapi import APIRouter

router = APIRouter(prefix="/match", tags=["Match"])
