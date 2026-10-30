"""
backend/app/services/providers/factory.py

Factory function to obtain configured LLM provider instance.
Supports environment-driven selection ('gemini', 'groq', 'huggingface', 'ollama')
and explicit runtime overrides.
"""

from __future__ import annotations

import os
from fastapi import HTTPException

from app.config import get_settings
from app.services.providers.base import LLMProvider
from app.services.providers.gemini_provider import GeminiProvider
from app.services.providers.groq_provider import GroqProvider
from app.services.providers.huggingface_provider import HuggingFaceProvider
from app.services.providers.ollama_provider import OllamaProvider


def get_llm_provider(
    provider_type: str | None = None,
    api_key: str | None = None,
    model_name: str | None = None,
) -> LLMProvider:
    """
    Factory function to retrieve an LLM provider instance based on centralized config or override.

    Parameters
    ----------
    provider_type : str | None
        Explicit provider name ('gemini', 'groq', 'huggingface', 'ollama').
        Defaults to AI_PROVIDER or LLM_PROVIDER from centralized settings.
    api_key : str | None
        Optional explicit API key override.
    model_name : str | None
        Optional explicit model name override.

    Returns
    -------
    LLMProvider
        Configured LLM provider instance.
    """
    settings = get_settings()
    selected = (
        provider_type
        or os.getenv("AI_PROVIDER")
        or os.getenv("LLM_PROVIDER")
        or settings.AI_PROVIDER
        or "gemini"
    ).strip().lower()

    if selected == "gemini":
        return GeminiProvider(
            api_key=api_key or settings.GEMINI_API_KEY,
            model_name=model_name or settings.GEMINI_MODEL,
        )
    elif selected == "groq":
        return GroqProvider(
            api_key=api_key or settings.GROQ_API_KEY,
            model_name=model_name or settings.GROQ_MODEL,
        )
    elif selected == "huggingface":
        return HuggingFaceProvider(
            api_key=api_key or settings.HUGGINGFACE_API_KEY,
            model_name=model_name,
        )
    elif selected == "ollama":
        return OllamaProvider(
            base_url=settings.OLLAMA_BASE_URL,
            model_name=model_name,
        )
    else:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported LLM provider '{selected}'. "
                f"Supported providers are: 'gemini', 'groq', 'huggingface', 'ollama'."
            ),
        )
