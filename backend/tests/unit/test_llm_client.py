"""Unit tests for LLMClient and GroqClient with 100% mocked network calls."""

import json
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.core.config import Settings
from app.services.llm_client import (
    DailyCallTracker,
    GroqClient,
    LLMAuthenticationError,
    LLMDailyCapExceededError,
    LLMError,
    LLMRateLimitError,
    LLMTimeoutError,
    LLMTruncatedOutputError,
)


@pytest.fixture
def test_settings_custom() -> Settings:
    return Settings(
        _env_file=None,
        ENV="development",
        API_PREFIX="/api/v1",
        MONGODB_URI="mongodb://localhost:27017",
        MONGODB_DB="yojanasetu_test",
        GROQ_API_KEY="gsk_mock_test_key_12345",
        GROQ_MODEL="llama-3.3-70b-versatile",
        EMBEDDING_PROVIDER="hosted",
        EMBEDDING_API_KEY="dummy_embedding_test_key",
        EMBEDDING_MODEL="hosted-multilingual-e5",
        EMBEDDING_DIM=384,
        JWT_SECRET="super_secret_test_jwt_key_that_is_long_enough",
        JWT_ISSUER="yojanasetu",
        ACCESS_TOKEN_MINUTES=60,
        ALLOWED_ORIGINS=["http://localhost:5173"],
        ENABLE_DOCS=True,
        RATE_LIMIT_PER_MINUTE=60,
        LLM_DAILY_CALL_CAP=5,
        SIMILARITY_THRESHOLD=0.7,
        LOG_LEVEL="INFO",
        INCLUDE_SAMPLE_SCHEMES=False,
    )


class TestGroqClientInitialization:
    """Verify settings loading, model inheritance, and configuration."""

    def test_reads_model_from_settings_never_hardcoded(
        self, test_settings_custom: Settings
    ):
        with patch(
            "app.services.llm_client.get_settings", return_value=test_settings_custom
        ):
            client = GroqClient()
            assert client.model == "llama-3.3-70b-versatile"
            assert client.api_key == "gsk_mock_test_key_12345"
            assert client.timeout == 20.0
            assert client.max_retries == 2


class TestDailyCallTracker:
    """Verify application-wide daily call limits."""

    @pytest.mark.asyncio
    async def test_call_cap_enforcement_and_reset(self):
        tracker = DailyCallTracker(cap=3)
        assert await tracker.get_count() == 0

        # Increment up to cap
        assert await tracker.increment_or_check() == 1
        assert await tracker.increment_or_check() == 2
        assert await tracker.increment_or_check() == 3

        # Exceed cap raises error
        with pytest.raises(LLMDailyCapExceededError) as exc_info:
            await tracker.increment_or_check()
        assert "Daily LLM call cap of 3 calls reached" in str(exc_info.value)

        # Reset allows calls again
        await tracker.reset()
        assert await tracker.get_count() == 0
        assert await tracker.increment_or_check() == 1


class TestGroqClientInference:
    """Verify structured output parsing, error handling, retries, and parameter degradation."""

    @pytest.mark.asyncio
    async def test_generate_structured_success(self, test_settings_custom: Settings):
        expected_json = {
            "age": 28,
            "gender": "female",
            "income_value": 2.5,
            "income_unit": "lakh",
        }
        mock_response_data = {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {
                        "content": json.dumps(expected_json),
                    },
                }
            ]
        }

        mock_http_response = httpx.Response(
            status_code=200,
            json=mock_response_data,
            request=httpx.Request(
                "POST", "https://api.groq.com/openai/v1/chat/completions"
            ),
        )

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.post.return_value = mock_http_response

        with patch(
            "app.services.llm_client.get_settings", return_value=test_settings_custom
        ):
            client = GroqClient(client=mock_client)
            result = await client.generate_structured(
                prompt="Citizen says 28F earning 2.5 lakh",
                schema={"type": "object"},
                temperature=0.0,
            )

            assert result == expected_json
            mock_client.post.assert_called_once()
            call_kwargs = mock_client.post.call_args[1]
            payload = call_kwargs["json"]
            assert payload["temperature"] == 0.0
            assert payload["max_completion_tokens"] >= 2000
            assert payload["reasoning_effort"] == "low"
            assert payload["response_format"]["type"] == "json_schema"

    @pytest.mark.asyncio
    async def test_graceful_degradation_when_reasoning_effort_rejected(
        self, test_settings_custom: Settings
    ):
        expected_json = {"age": 45}

        # First call returns 400 rejecting reasoning_effort
        error_resp = httpx.Response(
            status_code=400,
            text='{"error": {"message": "reasoning_effort is not supported for this model"}}',
            request=httpx.Request(
                "POST", "https://api.groq.com/openai/v1/chat/completions"
            ),
        )
        # Second call returns 200 OK without reasoning_effort
        success_resp = httpx.Response(
            status_code=200,
            json={
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {"content": json.dumps(expected_json)},
                    }
                ]
            },
            request=httpx.Request(
                "POST", "https://api.groq.com/openai/v1/chat/completions"
            ),
        )

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.post.side_effect = [error_resp, success_resp]

        with patch(
            "app.services.llm_client.get_settings", return_value=test_settings_custom
        ):
            client = GroqClient(client=mock_client)
            result = await client.generate_structured(
                prompt="test prompt",
                schema={"type": "object"},
            )

            assert result == expected_json
            assert mock_client.post.call_count == 2
            second_call_payload = mock_client.post.call_args_list[1][1]["json"]
            assert "reasoning_effort" not in second_call_payload

    @pytest.mark.asyncio
    async def test_truncated_output_raises_truncated_error(
        self, test_settings_custom: Settings
    ):
        mock_response_data = {
            "choices": [
                {
                    "finish_reason": "length",  # Hit completion limit
                    "message": {
                        "content": '{"age": 30, "incomplete',
                    },
                }
            ]
        }
        mock_http_response = httpx.Response(
            status_code=200,
            json=mock_response_data,
            request=httpx.Request(
                "POST", "https://api.groq.com/openai/v1/chat/completions"
            ),
        )

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.post.return_value = mock_http_response

        with patch(
            "app.services.llm_client.get_settings", return_value=test_settings_custom
        ):
            client = GroqClient(client=mock_client)
            with pytest.raises(LLMTruncatedOutputError) as exc_info:
                await client.generate_structured(
                    prompt="test prompt",
                    schema={"type": "object"},
                )
            assert "truncated due to max_completion_tokens" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_authentication_error_on_401(self, test_settings_custom: Settings):
        mock_http_response = httpx.Response(
            status_code=401,
            text='{"error": {"message": "Invalid API Key"}}',
            request=httpx.Request(
                "POST", "https://api.groq.com/openai/v1/chat/completions"
            ),
        )
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.post.return_value = mock_http_response

        with patch(
            "app.services.llm_client.get_settings", return_value=test_settings_custom
        ):
            client = GroqClient(client=mock_client)
            with pytest.raises(LLMAuthenticationError):
                await client.generate("hello")

    @pytest.mark.asyncio
    async def test_retry_on_rate_limit_and_succeed(
        self, test_settings_custom: Settings
    ):
        rate_limit_resp = httpx.Response(
            status_code=429,
            text='{"error": "rate limit"}',
            request=httpx.Request(
                "POST", "https://api.groq.com/openai/v1/chat/completions"
            ),
        )
        success_resp = httpx.Response(
            status_code=200,
            json={
                "choices": [
                    {"finish_reason": "stop", "message": {"content": "Hello World"}}
                ]
            },
            request=httpx.Request(
                "POST", "https://api.groq.com/openai/v1/chat/completions"
            ),
        )

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.post.side_effect = [rate_limit_resp, success_resp]

        with patch(
            "app.services.llm_client.get_settings", return_value=test_settings_custom
        ):
            with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
                client = GroqClient(client=mock_client, max_retries=2)
                response = await client.generate("hello", temperature=0.2)
                assert response == "Hello World"
                assert mock_client.post.call_count == 2
                mock_sleep.assert_called_once()

    @pytest.mark.asyncio
    async def test_timeout_exhausts_retries(self, test_settings_custom: Settings):
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.post.side_effect = httpx.ReadTimeout("Timed out")

        with patch(
            "app.services.llm_client.get_settings", return_value=test_settings_custom
        ):
            with patch("asyncio.sleep", new_callable=AsyncMock):
                client = GroqClient(client=mock_client, max_retries=2)
                with pytest.raises(LLMTimeoutError):
                    await client.generate("hello")
                assert mock_client.post.call_count == 3
