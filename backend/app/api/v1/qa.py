"""Scheme Question & Answering router with grounded RAG explanations."""

from fastapi import APIRouter

router = APIRouter(prefix="/qa", tags=["QA"])
