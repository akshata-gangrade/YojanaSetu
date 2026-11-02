"""Schemes discovery and detail router serving verified government schemes."""

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_rag_service, get_scheme_repo
from app.core.config import Settings, get_settings
from app.core.errors import NotFoundError
from app.core.rate_limit import rate_limit_ask_dependency, rate_limit_dependency
from app.repositories.base import ISchemeRepository
from app.schemas.api import PaginatedSchemesResponse, SchemeAskRequest, SchemeAskResponse
from app.schemas.enums import SchemeLevel, SchemeStatus
from app.schemas.scheme import Scheme
from app.services.rag_service import RAGService

router = APIRouter(prefix="/schemes", tags=["Schemes"])


@router.get(
    "",
    response_model=PaginatedSchemesResponse,
    dependencies=[Depends(rate_limit_dependency)],
    summary="List verified government schemes with pagination and filtering",
)
async def list_verified_schemes(
    skip: int = Query(0, ge=0, description="Number of schemes to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum schemes to return"),
    state: str | None = Query(None, description="Filter by Indian State (lowercase)"),
    level: SchemeLevel | None = Query(None, description="Filter by level ('central' or 'state')"),
    category: str | None = Query(None, description="Filter by category tag"),
    scheme_repo: ISchemeRepository = Depends(get_scheme_repo),
    settings: Settings = Depends(get_settings),
) -> PaginatedSchemesResponse:
    """Retrieve verified schemes with whitelisted query parameters."""
    level_str = level.value if level else None
    schemes = await scheme_repo.get_verified_schemes(
        skip=skip,
        limit=limit,
        state=state,
        level=level_str,
        include_samples=settings.INCLUDE_SAMPLE_SCHEMES,
        include_unverified=settings.PUBLISH_UNREVIEWED_SCHEMES,
    )

    # In-memory category filter if requested
    if category:
        clean_cat = category.strip().lower()
        schemes = [
            s
            for s in schemes
            if any(clean_cat == tag.strip().lower() for tag in s.category_tags)
        ]

    total = await scheme_repo.count_verified(
        state=state,
        level=level_str,
        include_samples=settings.INCLUDE_SAMPLE_SCHEMES,
        include_unverified=settings.PUBLISH_UNREVIEWED_SCHEMES,
    )

    return PaginatedSchemesResponse(
        items=schemes,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{slug}",
    response_model=Scheme,
    dependencies=[Depends(rate_limit_dependency)],
    summary="Retrieve details for a single verified government scheme",
)
async def get_scheme_by_slug(
    slug: str,
    scheme_repo: ISchemeRepository = Depends(get_scheme_repo),
    settings: Settings = Depends(get_settings),
) -> Scheme:
    """Fetch scheme by unique slug, including unverified demo schemes if enabled."""
    scheme = await scheme_repo.get_by_slug(slug)
    if not scheme:
        raise NotFoundError(f"Scheme '{slug}' not found.")

    allowed_statuses = {SchemeStatus.VERIFIED}
    if settings.PUBLISH_UNREVIEWED_SCHEMES:
        allowed_statuses.add(SchemeStatus.NEEDS_REVIEW)

    if scheme.status not in allowed_statuses:
        raise NotFoundError(f"Scheme '{slug}' not found.")

    if scheme.is_sample and not settings.INCLUDE_SAMPLE_SCHEMES:
        raise NotFoundError(f"Scheme '{slug}' not found.")

    return scheme


@router.post(
    "/{slug}/ask",
    response_model=SchemeAskResponse,
    dependencies=[Depends(rate_limit_ask_dependency)],
    summary="Ask a grounded question about official scheme guidelines",
)
async def ask_scheme_question(
    slug: str,
    request: SchemeAskRequest,
    scheme_repo: ISchemeRepository = Depends(get_scheme_repo),
    rag_service: RAGService = Depends(get_rag_service),
    settings: Settings = Depends(get_settings),
) -> SchemeAskResponse:
    """Query scheme guidelines via RAG (stubbed until RAG module is active)."""
    scheme = await scheme_repo.get_by_slug(slug)
    if not scheme:
        raise NotFoundError(f"Scheme '{slug}' not found.")

    allowed_statuses = {SchemeStatus.VERIFIED}
    if settings.PUBLISH_UNREVIEWED_SCHEMES:
        allowed_statuses.add(SchemeStatus.NEEDS_REVIEW)

    if scheme.status not in allowed_statuses:
        raise NotFoundError(f"Scheme '{slug}' not found.")

    if scheme.is_sample and not settings.INCLUDE_SAMPLE_SCHEMES:
        raise NotFoundError(f"Scheme '{slug}' not found.")

    return await rag_service.answer_question(
        scheme_slug=slug,
        question=request.question,
        language=request.language,
    )
