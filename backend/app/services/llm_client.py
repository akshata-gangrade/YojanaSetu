"""LLM client interface and Groq provider abstraction.

Allows changing LLM providers without touching service or business logic layers.
Enforces timeout, exponential backoff retries, daily call cap, and structured JSON parsing.
"""

from abc import ABC, abstractmethod
import asyncio
from datetime import datetime, timezone
import json
import logging
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

GROQ_CHAT_COMPLETIONS_URL = "https://api.groq.com/openai/v1/chat/completions"


class LLMError(Exception):
    """Base exception for all LLM client failures."""

    pass


class LLMDailyCapExceededError(LLMError):
    """Raised when the application-wide daily LLM call budget is exhausted."""

    pass


class LLMTimeoutError(LLMError):
    """Raised when an LLM inference request exceeds the configured timeout."""

    pass


class LLMAuthenticationError(LLMError):
    """Raised when the provider rejects credentials (401 Unauthorized)."""

    pass


class LLMRateLimitError(LLMError):
    """Raised when the provider rejects calls due to rate limits (429)."""

    pass


class LLMTruncatedOutputError(LLMError):
    """Raised when the LLM returns empty or truncated completion content."""

    pass


class DailyCallTracker:
    """Thread-safe tracker enforcing daily LLM call limits based on UTC date."""

    def __init__(self, cap: int):
        self.cap = cap
        self._date: str = ""
        self._count: int = 0
        self._lock = asyncio.Lock()

    async def increment_or_check(self) -> int:
        """Increment call counter for today, raising error if cap is exceeded."""
        async with self._lock:
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            if self._date != today:
                self._date = today
                self._count = 0

            if self._count >= self.cap:
                raise LLMDailyCapExceededError(
                    f"Daily LLM call cap of {self.cap} calls reached for {today}."
                )

            self._count += 1
            return self._count

    async def get_count(self) -> int:
        """Get current call count for today."""
        async with self._lock:
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            if self._date != today:
                return 0
            return self._count

    async def reset(self) -> None:
        """Reset counter (useful for test isolation)."""
        async with self._lock:
            self._date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            self._count = 0


class LLMClient(ABC):
    """Abstract interface defining required LLM inference capabilities."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.2,
    ) -> str:
        """Generate unstructured text completion from prompt and optional instructions."""
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        schema: dict[str, Any],
        system_prompt: str | None = None,
        schema_name: str = "structured_output",
        temperature: float = 0.0,
    ) -> dict[str, Any]:
        """Generate structured JSON adhering to a specified JSON Schema."""
        pass


class GroqClient(LLMClient):
    """Groq API implementation of the LLMClient interface."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        daily_call_cap: int | None = None,
        timeout: float = 20.0,
        max_retries: int = 2,
        client: httpx.AsyncClient | None = None,
    ):
        settings = get_settings()
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or settings.GROQ_MODEL
        self.timeout = timeout
        self.max_retries = max_retries
        cap = (
            daily_call_cap
            if daily_call_cap is not None
            else settings.LLM_DAILY_CALL_CAP
        )
        self.tracker = DailyCallTracker(cap=cap)
        self._external_client = client

    def _get_headers(self) -> dict[str, str]:
        """Construct authorization headers without logging credentials."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def _post_with_retry(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Execute HTTP POST with exponential backoff and parameter degradation."""
        # Check and increment daily call cap before dispatching network request
        await self.tracker.increment_or_check()

        working_payload = dict(payload)
        headers = self._get_headers()
        url = GROQ_CHAT_COMPLETIONS_URL

        client_provided = self._external_client is not None
        last_error: Exception | None = None

        for attempt in range(self.max_retries + 1):
            client = self._external_client or httpx.AsyncClient(timeout=self.timeout)
            try:
                response = await client.post(url, json=working_payload, headers=headers)

                # Check for 401 Unauthorized
                if response.status_code == 401:
                    raise LLMAuthenticationError(
                        "Groq API rejected authentication credentials."
                    )

                # Check for 400 parameter rejections (e.g. reasoning_effort or temperature)
                if response.status_code == 400:
                    resp_text = response.text
                    # Check if reasoning_effort is unsupported
                    degraded = False
                    if (
                        "reasoning_effort" in resp_text
                        and "reasoning_effort" in working_payload
                    ):
                        logger.warning(
                            "Groq model rejected reasoning_effort. Retrying without it."
                        )
                        working_payload.pop("reasoning_effort", None)
                        degraded = True
                    # Check if temperature is unsupported
                    if "temperature" in resp_text and "temperature" in working_payload:
                        logger.warning(
                            "Groq model rejected temperature. Retrying without it."
                        )
                        working_payload.pop("temperature", None)
                        degraded = True

                    if degraded:
                        # Immediate retry with stripped parameters without consuming a backoff attempt
                        continue

                    # Non-recoverable 400
                    raise LLMError(f"Groq API returned 400 Bad Request: {resp_text}")

                # Check for 429 Rate Limit
                if response.status_code == 429:
                    if attempt < self.max_retries:
                        backoff = 0.5 * (2**attempt)
                        logger.warning(
                            "Groq rate limit encountered. Retrying in %.2fs...", backoff
                        )
                        await asyncio.sleep(backoff)
                        continue
                    raise LLMRateLimitError(
                        "Groq API rate limit exceeded and retries exhausted."
                    )

                # Check for 5xx Server Errors
                if response.status_code >= 500:
                    if attempt < self.max_retries:
                        backoff = 0.5 * (2**attempt)
                        logger.warning(
                            "Groq server error %d. Retrying in %.2fs...",
                            response.status_code,
                            backoff,
                        )
                        await asyncio.sleep(backoff)
                        continue
                    raise LLMError(
                        f"Groq server error {response.status_code}: {response.text}"
                    )

                response.raise_for_status()
                return response.json()

            except (httpx.TimeoutException, TimeoutError) as exc:
                last_error = LLMTimeoutError(
                    f"Groq request timed out after {self.timeout}s"
                )
                if attempt < self.max_retries:
                    backoff = 0.5 * (2**attempt)
                    logger.warning(
                        "Groq request timed out. Retrying in %.2fs...", backoff
                    )
                    await asyncio.sleep(backoff)
                    continue
                raise last_error from exc
            except (httpx.NetworkError, httpx.TransportError) as exc:
                last_error = LLMError(f"Groq network error: {exc}")
                if attempt < self.max_retries:
                    backoff = 0.5 * (2**attempt)
                    logger.warning("Groq network error. Retrying in %.2fs...", backoff)
                    await asyncio.sleep(backoff)
                    continue
                raise last_error from exc
            finally:
                if not client_provided:
                    await client.aclose()

        if last_error:
            raise last_error
        raise LLMError("Groq request failed after all retries.")

    def _extract_choice_content(self, data: dict[str, Any]) -> str:
        """Extract text from completion response and validate non-truncation."""
        choices = data.get("choices", [])
        if not choices:
            raise LLMTruncatedOutputError("Empty choices array returned by Groq.")

        first_choice = choices[0]
        finish_reason = first_choice.get("finish_reason")
        if finish_reason == "length":
            raise LLMTruncatedOutputError(
                "Completion was truncated due to max_completion_tokens limit."
            )

        message = first_choice.get("message", {})
        content = message.get("content")
        if not content or not content.strip():
            raise LLMTruncatedOutputError("Empty completion text returned by Groq.")

        return content.strip()

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.2,
    ) -> str:
        """Generate unstructured text completion."""
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_completion_tokens": 2048,
        }

        data = await self._post_with_retry(payload)
        return self._extract_choice_content(data)

    async def generate_structured(
        self,
        prompt: str,
        schema: dict[str, Any],
        system_prompt: str | None = None,
        schema_name: str = "structured_output",
        temperature: float = 0.0,
    ) -> dict[str, Any]:
        """Generate structured JSON conforming to specified schema."""
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_completion_tokens": 2048,
            "reasoning_effort": "low",
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": schema_name,
                    "strict": True,
                    "schema": schema,
                },
            },
        }

        data = await self._post_with_retry(payload)
        content_text = self._extract_choice_content(data)

        try:
            parsed = json.loads(content_text)
            if not isinstance(parsed, dict):
                raise ValueError(f"Expected JSON object, got {type(parsed).__name__}")
            return parsed
        except (json.JSONDecodeError, ValueError) as err:
            raise LLMError(
                f"Failed to parse LLM structured output as JSON: {err}"
            ) from err


# Backwards compatibility alias
GroqLLMClient = GroqClient
