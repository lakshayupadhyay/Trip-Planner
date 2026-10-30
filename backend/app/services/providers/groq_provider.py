"""
backend/app/services/providers/groq_provider.py

Groq AI provider implementation using official groq Python SDK.
Supports ultra-fast asynchronous inference, lazy client initialization, and mock injection.
"""

from __future__ import annotations

import os
from typing import Any
from fastapi import HTTPException
from dotenv import load_dotenv

from app.services.providers.base import LLMProvider

load_dotenv()


class GroqProvider(LLMProvider):
    """
    LLM provider utilizing Groq's high-speed inference engine.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str | None = None,
        client: Any | None = None,
    ) -> None:
        self._api_key = api_key or os.getenv("GROQ_API_KEY")
        self._model_name = (
            model_name or os.getenv("GROQ_MODEL") or "llama-3.3-70b-versatile"
        )
        self._client = client

    @property
    def name(self) -> str:
        return "groq"

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def client(self) -> Any:
        """Lazily initialize AsyncGroq client."""
        if self._client is not None:
            return self._client

        if (
            not self._api_key
            or self._api_key == "your-groq-api-key"
            or self._api_key.startswith("your_")
        ):
            raise HTTPException(
                status_code=500,
                detail="Groq API key is not configured. Please set GROQ_API_KEY in your backend .env file.",
            )

        try:
            from groq import AsyncGroq
            self._client = AsyncGroq(api_key=self._api_key)
            return self._client
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize Groq client: {exc}",
            ) from exc

    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """
        Asynchronously invoke Groq chat completion API.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await self.client.chat.completions.create(
                model=self._model_name,
                messages=messages,
                temperature=0.7,
                response_format={"type": "json_object"},
            )
            choice = response.choices[0]
            return choice.message.content or ""

        except HTTPException:
            raise
        except Exception as exc:
            msg = str(exc)
            err_name = type(exc).__name__

            if "rate_limit_exceeded" in msg or "429" in msg or "rate limit" in msg.lower():
                raise HTTPException(
                    status_code=429,
                    detail="Groq API rate limit exceeded. Please retry in a few moments.",
                ) from exc

            if "timeout" in msg.lower():
                raise HTTPException(
                    status_code=504,
                    detail="Groq API request timed out. Please retry.",
                ) from exc

            raise HTTPException(
                status_code=502,
                detail=f"Groq AI provider error ({err_name}): {msg}",
            ) from exc

