"""Unit tests validating database index definitions, TTL periods, and vector specs."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from pymongo import ASCENDING

from app.core.config import Settings
from app.db.indexes import create_vector_index, ensure_indexes


@pytest.mark.asyncio
async def test_ensure_indexes_specifications() -> None:
    """Validate that ensure_indexes configures required indexes with exact specs."""
    mock_db = MagicMock()

    # Setup mock collections with create_indexes as AsyncMock
    mock_schemes = MagicMock()
    mock_schemes.create_indexes = AsyncMock(
        return_value=["uniq_scheme_slug", "idx_status_state_level"]
    )
    mock_admins = MagicMock()
    mock_admins.create_indexes = AsyncMock(return_value=["uniq_admin_email"])
    mock_chunks = MagicMock()
    mock_chunks.create_indexes = AsyncMock(return_value=["idx_chunk_scheme_id"])
    mock_feedback = MagicMock()
    mock_feedback.create_indexes = AsyncMock(return_value=["ttl_feedback_90_days"])
    mock_audit = MagicMock()
    mock_audit.create_indexes = AsyncMock(return_value=["idx_audit_target_timestamp"])

    def get_collection(name: str):
        mapping = {
            "schemes": mock_schemes,
            "admin_users": mock_admins,
            "scheme_chunks": mock_chunks,
            "feedback": mock_feedback,
            "audit_logs": mock_audit,
        }
        return mapping[name]

    mock_db.__getitem__.side_effect = get_collection

    await ensure_indexes(mock_db, include_vector=False)

    # 1. schemes index calls
    schemes_call_args = mock_schemes.create_indexes.call_args[0][0]
    # Check unique slug
    slug_idx = next(
        idx
        for idx in schemes_call_args
        if idx.document.get("name") == "uniq_scheme_slug"
    )
    assert slug_idx.document.get("unique") is True
    assert list(slug_idx.document.get("key").items()) == [("slug", ASCENDING)]

    # Check compound (status, state, level)
    compound_idx = next(
        idx
        for idx in schemes_call_args
        if idx.document.get("name") == "idx_status_state_level"
    )
    assert list(compound_idx.document.get("key").items()) == [
        ("status", ASCENDING),
        ("state", ASCENDING),
        ("level", ASCENDING),
    ]

    # 2. admin_users index calls
    admin_call_args = mock_admins.create_indexes.call_args[0][0]
    admin_email_idx = next(
        idx for idx in admin_call_args if idx.document.get("name") == "uniq_admin_email"
    )
    assert admin_email_idx.document.get("unique") is True
    assert list(admin_email_idx.document.get("key").items()) == [("email", ASCENDING)]

    # 3. feedback 90-day TTL index
    feedback_call_args = mock_feedback.create_indexes.call_args[0][0]
    ttl_idx = next(
        idx
        for idx in feedback_call_args
        if idx.document.get("name") == "ttl_feedback_90_days"
    )
    assert ttl_idx.document.get("expireAfterSeconds") == 90 * 24 * 3600
    assert list(ttl_idx.document.get("key").items()) == [("created_at", ASCENDING)]


@pytest.mark.asyncio
async def test_vector_index_creation_spec(test_settings: Settings) -> None:
    """Validate vector search index definition and dimensionality match settings."""
    mock_db = MagicMock()
    mock_chunks = MagicMock()
    mock_chunks.create_search_index = AsyncMock(return_value="vector_index")

    # Mock list_search_indexes cursor to return READY
    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock(
        return_value=[{"name": "vector_index", "status": "READY", "queryable": True}]
    )
    mock_chunks.list_search_indexes.return_value = mock_cursor

    mock_db.__getitem__.return_value = mock_chunks

    index_name = await create_vector_index(
        mock_db,
        embedding_dim=test_settings.EMBEDDING_DIM,
        wait=True,
        timeout_seconds=5,
    )

    assert index_name == "vector_index"
    mock_chunks.create_search_index.assert_called_once()
    search_model = mock_chunks.create_search_index.call_args[1]["model"]
    definition = search_model.document.get("definition", {})
    fields = definition.get("fields", [])

    # Verify vector field definition
    vector_field = next(f for f in fields if f.get("type") == "vector")
    assert vector_field["path"] == "embedding"
    assert vector_field["numDimensions"] == test_settings.EMBEDDING_DIM
    assert vector_field["similarity"] == "cosine"
