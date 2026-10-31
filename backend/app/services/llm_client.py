"""LLM client interface and Groq provider abstraction.

Allows changing LLM providers without touching service or business logic layers.
"""

from abc import ABC, abstractmethod


class LLMClient(ABC):
    """Abstract interface defining required LLM inference capabilities."""

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """Generate a text completion from a prompt and optional instructions."""
        pass


class GroqLLMClient(LLMClient):
    """Groq API implementation of the LLMClient interface."""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """Execute inference against Groq chat completions endpoint."""
        # Feature implementation in subsequent module
        raise NotImplementedError(
            "Groq client implementation scheduled for intake/LLM module."
        )
