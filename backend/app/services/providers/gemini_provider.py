"""
backend/app/services/providers/gemini_provider.py

Google Gemini AI provider implementation using official google-genai SDK.
Supports asynchronous generation, lazy client initialization, and mock injection.
"""

from __future__ import annotations

import os
from typing import Any
from fastapi import HTTPException
from dotenv import load_dotenv

from app.services.providers.base import LLMProvider

load_dotenv()


class GeminiProvider(LLMProvider):
    """
    LLM provider utilizing Google Gemini via the official google-genai SDK.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str | None = None,
        client: Any | None = None,
    ) -> None:
        self._api_key = api_key or os.getenv("GEMINI_API_KEY")
        self._model_name = model_name or os.getenv("GEMINI_MODEL") or "gemini-3.8-flash"
        self._client = client

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def client(self) -> Any:
        """Lazily initialize Google GenAI client."""
        if self._client is not None:
            return self._client

        if (
            not self._api_key
            or self._api_key == "your-gemini-api-key"
            or self._api_key.startswith("your_")
        ):
            raise HTTPException(
                status_code=500,
                detail="Gemini API key is not configured. Please set GEMINI_API_KEY in your backend .env file.",
            )

        try:
            from google import genai
            self._client = genai.Client(api_key=self._api_key)
            return self._client
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize Google GenAI client: {exc}",
            ) from exc

    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """
        Asynchronously invoke Gemini models to generate content.
        """
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"System Instructions:\n{system_prompt}\n\nTask:\n{prompt}"

        try:
            # Use official client's aio namespace for async generation
            response = await self.client.aio.models.generate_content(
                model=self._model_name,
                contents=full_prompt,
            )
            return response.text or ""

        except HTTPException:
            raise
        except Exception as exc:
            msg = str(exc)
            err_name = type(exc).__name__

            if "RESOURCE_EXHAUSTED" in msg or "429" in msg or "quota" in msg.lower():
                raise HTTPException(
                    status_code=429,
                    detail="Gemini API rate limit exceeded. Please retry in a few moments.",
                ) from exc

            if "DEADLINE_EXCEEDED" in msg or "timeout" in msg.lower():
                raise HTTPException(
                    status_code=504,
                    detail="Gemini API request timed out. Please retry.",
                ) from exc

            raise HTTPException(
                status_code=502,
                detail=f"Gemini AI provider error ({err_name}): {msg}",
            ) from exc

