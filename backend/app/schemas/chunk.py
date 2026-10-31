"""Pydantic models for scheme_chunks collection with vector embeddings."""

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import ChunkSection


class SchemeChunkBase(BaseModel):
    """Core knowledge chunk metadata and text content."""

    model_config = ConfigDict(extra="forbid")

    scheme_id: str = Field(
        ...,
        description="Foreign identifier linking to parent scheme document.",
    )
    section: ChunkSection = Field(
        ...,
        description="Logical document section for categorized retrieval.",
    )
    text: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Unmodified guideline text excerpt extracted from official source.",
    )
    embedding: list[float] = Field(
        ...,
        description="Multilingual dense vector embedding of the chunk text.",
    )
    source_url: str = Field(
        ...,
        description="Official source URL where this specific chunk originated.",
    )
    page: int | None = Field(
        default=None,
        ge=1,
        description="Page number in official PDF guideline if applicable.",
    )


class SchemeChunkCreate(SchemeChunkBase):
    """Schema for inserting a new embedded chunk into scheme_chunks."""

    pass


class SchemeChunk(SchemeChunkBase):
    """Retrieved scheme chunk model with MongoDB identifier."""

    id: str | None = Field(
        default=None,
        description="MongoDB document identifier string.",
    )
    score: float | None = Field(
        default=None,
        description="Vector search similarity score if retrieved via vector query.",
    )
