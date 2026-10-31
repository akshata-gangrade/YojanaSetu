"""Retrieval-Augmented Generation (RAG) service for scheme documentation."""

from abc import ABC, abstractmethod


class EmbeddingClient(ABC):
    """Abstract interface for generating hosted multilingual embeddings."""

    @abstractmethod
    async def embed_query(self, text: str) -> list[float]:
        """Generate vector embedding for a search query."""
        pass


class RAGService:
    """Service to coordinate vector retrieval and context assembly."""

    def __init__(self, embedding_client: EmbeddingClient):
        self.embedding_client = embedding_client
