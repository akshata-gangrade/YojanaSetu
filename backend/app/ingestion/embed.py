"""Ingestion module: Generates vector embeddings for chunked scheme documents."""

from app.services.rag_service import EmbeddingClient


class SchemeEmbedder:
    """Chunks scheme documentation and attaches vector embeddings for Atlas search."""

    def __init__(self, embedding_client: EmbeddingClient):
        self.embedding_client = embedding_client
