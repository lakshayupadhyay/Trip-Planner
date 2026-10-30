"""
tests/test_llm_providers.py

Unit tests for AI Model Provider Architecture:
- LLMProvider ABC interface enforcement
- GeminiProvider initialization, mock async generation, and error mapping
- GroqProvider initialization, mock async generation, and error mapping
- get_llm_provider factory resolution and error handling
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from app.services.providers.base import LLMProvider
from app.services.providers.gemini_provider import GeminiProvider
from app.services.providers.groq_provider import GroqProvider
from app.services.providers.factory import get_llm_provider


# ── 1. Abstract Base Class Enforcement ────────────────────────────────────────

def test_llm_provider_abstract():
    """Verify LLMProvider cannot be instantiated directly."""
    with pytest.raises(TypeError):
        LLMProvider()


# ── 2. GeminiProvider Tests ───────────────────────────────────────────────────

def test_gemini_provider_properties():
    """Verify GeminiProvider properties and defaults."""
    provider = GeminiProvider(api_key="test-key", model_name="gemini-3.8-flash")
    assert provider.name == "gemini"
    assert provider.model_name == "gemini-3.8-flash"


def test_gemini_provider_missing_key_raises_500():
    """Verify missing API key raises HTTP 500 upon client access."""
    provider = GeminiProvider(api_key=None, client=None)
    provider._api_key = None

    with pytest.raises(HTTPException) as exc_info:
        _ = provider.client
    assert exc_info.value.status_code == 500
    assert "Gemini API key is not configured" in exc_info.value.detail


@pytest.mark.anyio
async def test_gemini_provider_generate_success():
    """Verify asynchronous content generation with mocked Google GenAI client."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"message": "Hello from Gemini"}'
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    provider = GeminiProvider(api_key="valid-key", client=mock_client)
    result = await provider.generate(prompt="Plan a trip", system_prompt="You are a guide")

    assert result == '{"message": "Hello from Gemini"}'
    mock_client.aio.models.generate_content.assert_called_once()


@pytest.mark.anyio
async def test_gemini_provider_rate_limit_error():
    """Verify RESOURCE_EXHAUSTED translates to HTTP 429."""
    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(
        side_effect=Exception("429 RESOURCE_EXHAUSTED: Quota exceeded")
    )

    provider = GeminiProvider(api_key="valid-key", client=mock_client)
    with pytest.raises(HTTPException) as exc_info:
        await provider.generate(prompt="Plan a trip")

    assert exc_info.value.status_code == 429
    assert "rate limit exceeded" in exc_info.value.detail.lower()


@pytest.mark.anyio
async def test_gemini_provider_timeout_error():
    """Verify DEADLINE_EXCEEDED translates to HTTP 504."""
    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(
        side_effect=Exception("DEADLINE_EXCEEDED: timeout occurred")
    )

    provider = GeminiProvider(api_key="valid-key", client=mock_client)
    with pytest.raises(HTTPException) as exc_info:
        await provider.generate(prompt="Plan a trip")

    assert exc_info.value.status_code == 504
    assert "timed out" in exc_info.value.detail.lower()


# ── 3. GroqProvider Tests ─────────────────────────────────────────────────────

def test_groq_provider_properties():
    """Verify GroqProvider properties and defaults."""
    provider = GroqProvider(api_key="test-key", model_name="llama-3.3-70b-versatile")
    assert provider.name == "groq"
    assert provider.model_name == "llama-3.3-70b-versatile"


def test_groq_provider_missing_key_raises_500():
    """Verify missing Groq API key raises HTTP 500 upon client access."""
    provider = GroqProvider(api_key=None, client=None)
    provider._api_key = None

    with pytest.raises(HTTPException) as exc_info:
        _ = provider.client
    assert exc_info.value.status_code == 500
    assert "Groq API key is not configured" in exc_info.value.detail


@pytest.mark.anyio
async def test_groq_provider_generate_success():
    """Verify asynchronous chat completion with mocked Groq client."""
    mock_client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = '{"message": "Hello from Groq"}'
    mock_response = MagicMock(choices=[mock_choice])
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    provider = GroqProvider(api_key="valid-key", client=mock_client)
    result = await provider.generate(prompt="Plan a trip", system_prompt="You are a planner")

    assert result == '{"message": "Hello from Groq"}'
    mock_client.chat.completions.create.assert_called_once()


@pytest.mark.anyio
async def test_groq_provider_rate_limit_error():
    """Verify rate limit exception translates to HTTP 429."""
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(
        side_effect=Exception("rate_limit_exceeded: 429 too many requests")
    )

    provider = GroqProvider(api_key="valid-key", client=mock_client)
    with pytest.raises(HTTPException) as exc_info:
        await provider.generate(prompt="Plan a trip")

    assert exc_info.value.status_code == 429
    assert "rate limit exceeded" in exc_info.value.detail.lower()


# ── 4. Provider Factory Tests ─────────────────────────────────────────────────

def test_get_llm_provider_factory():
    """Verify get_llm_provider instantiates proper provider based on argument."""
    gemini_p = get_llm_provider("gemini", api_key="dummy-key")
    assert isinstance(gemini_p, GeminiProvider)
    assert gemini_p.name == "gemini"

    groq_p = get_llm_provider("groq", api_key="dummy-key")
    assert isinstance(groq_p, GroqProvider)
    assert groq_p.name == "groq"


def test_get_llm_provider_unsupported_raises_400():
    """Verify unsupported provider name raises HTTP 400."""
    with pytest.raises(HTTPException) as exc_info:
        get_llm_provider("unsupported_ai_provider")
    assert exc_info.value.status_code == 400
    assert "Unsupported LLM provider" in exc_info.value.detail

