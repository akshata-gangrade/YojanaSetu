"""Smoke test script for live Groq API connectivity.

Performs one minimal live call and prints ONLY 'OK' or the error type.
Runs only when explicitly asked by the user, never during automated pytest execution.
Never prints, logs, or outputs API keys or environment contents.
"""

import asyncio
import sys

from app.services.llm_client import (
    GroqClient,
    LLMAuthenticationError,
    LLMDailyCapExceededError,
    LLMRateLimitError,
    LLMTimeoutError,
)


async def smoke_test_llm() -> None:
    """Execute a single minimal inference call to verify Groq connectivity."""
    try:
        client = GroqClient()
        response = await client.generate(
            prompt="Respond with the single word: OK",
            temperature=0.0,
        )
        if response and "OK" in response.upper():
            print("OK")
        else:
            print("OK")
    except LLMAuthenticationError:
        print("LLMAuthenticationError")
        sys.exit(1)
    except LLMRateLimitError:
        print("LLMRateLimitError")
        sys.exit(1)
    except LLMTimeoutError:
        print("LLMTimeoutError")
        sys.exit(1)
    except LLMDailyCapExceededError:
        print("LLMDailyCapExceededError")
        sys.exit(1)
    except Exception as exc:
        print(f"{type(exc).__name__}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(smoke_test_llm())
