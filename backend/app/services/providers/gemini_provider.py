"""
backend/app/services/providers/gemini_provider.py

Google Gemini AI provider implementation using official google-genai SDK.
Supports asynchronous generation, lazy client initialization, mock injection,
and automatic fallback across candidate models if the primary model is busy or unavailable.
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
        self._model_name = model_name or os.getenv("GEMINI_MODEL") or "gemini-3.1-flash-lite"
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
        Includes automatic fallback across candidate models if the primary model
        experiences high demand (HTTP 503) or temporary unavailability.
        """
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"System Instructions:\n{system_prompt}\n\nTask:\n{prompt}"

        # Candidate models to try: preferred model first, then resilient fast fallbacks
        models_to_try = [self._model_name]
        for fallback in ["gemini-3.1-flash-lite", "gemini-3.5-flash", "gemini-3.8-flash"]:
            if fallback not in models_to_try:
                models_to_try.append(fallback)

        last_exc: Exception | None = None

        for model in models_to_try:
            try:
                response = await self.client.aio.models.generate_content(
                    model=model,
                    contents=full_prompt,
                )
                if response and response.text:
                    return response.text
            except HTTPException:
                raise
            except Exception as exc:
                last_exc = exc
                msg = str(exc)
                # If high demand (503) or deprecated model (404), try next model
                if "503" in msg or "UNAVAILABLE" in msg or "404" in msg or "NOT_FOUND" in msg or "demand" in msg.lower():
                    continue
                # For rate limits (429), try next fallback model
                if "RESOURCE_EXHAUSTED" in msg or "429" in msg or "quota" in msg.lower():
                    continue
                break

        if last_exc is not None:
            msg = str(last_exc)
            err_name = type(last_exc).__name__

            if "RESOURCE_EXHAUSTED" in msg or "429" in msg or "quota" in msg.lower():
                raise HTTPException(
                    status_code=429,
                    detail="Gemini API rate limit exceeded across all models. Please retry in a few moments.",
                ) from last_exc

            if "DEADLINE_EXCEEDED" in msg or "timeout" in msg.lower():
                raise HTTPException(
                    status_code=504,
                    detail="Gemini API request timed out. Please retry.",
                ) from last_exc

            raise HTTPException(
                status_code=502,
                detail=f"Gemini AI provider error ({err_name}): {msg}",
            ) from last_exc

        return ""
