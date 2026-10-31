"""Service for generating grounded, citation-backed scheme explanations."""

from app.services.llm_client import LLMClient


class ExplanationService:
    """Produces natural explanations based only on verified scheme texts."""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
