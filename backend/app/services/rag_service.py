"""Retrieval-Augmented Generation (RAG) service for scheme documentation."""

from abc import ABC, abstractmethod

from app.schemas.api import SchemeAskResponse


class EmbeddingClient(ABC):
    """Abstract interface for generating hosted multilingual embeddings."""

    @abstractmethod
    async def embed_query(self, text: str) -> list[float]:
        """Generate vector embedding for a search query."""
        pass


class RAGService:
    """Service to coordinate vector retrieval and grounded context assembly."""

    def __init__(self, embedding_client: EmbeddingClient | None = None):
        self.embedding_client = embedding_client

    async def answer_question(
        self,
        scheme_slug: str,
        question: str,
        language: str = "en",
    ) -> SchemeAskResponse:
        """Answer citizen questions grounded in verified scheme guidelines.

        Stub implementation returning answerable=False until the full RAG module is built.
        """
        is_hi = language.lower().startswith("hi")
        default_answer = (
            "आधिकारिक योजना दिशानिर्देशों में यह जानकारी उपलब्ध नहीं है।"
            if is_hi
            else "Information not available in official scheme guidelines."
        )
        return SchemeAskResponse(
            answer=default_answer,
            citations=[],
            answerable=False,
        )
