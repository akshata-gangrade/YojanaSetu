"""Natural language user situation extractor into structured profile attributes."""

from app.services.llm_client import LLMClient


class ProfileExtractorService:
    """Service to parse citizen input into structured criteria using LLM."""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
