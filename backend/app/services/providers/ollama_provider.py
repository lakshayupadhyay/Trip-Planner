"""
backend/app/services/providers/ollama_provider.py

Local Ollama AI provider implementation using asynchronous HTTP requests.
Enables offline, privacy-first local LLM execution (e.g. Llama 3, Mistral, Gemma).
"""

from __future__ import annotations

import os
from typing import Any
from fastapi import HTTPException
import httpx

from app.config import get_settings
from app.services.providers.base import LLMProvider


class OllamaProvider(LLMProvider):
    """
    LLM provider connecting to a local or self-hosted Ollama server.
    """

    def __init__(
        self,
        base_url: str | None = None,
        model_name: str | None = None,
        client: Any | None = None,
    ) -> None:
        settings = get_settings()
        self._base_url = (base_url or settings.OLLAMA_BASE_URL or "http://localhost:11434").rstrip("/")
        self._model_name = model_name or "llama3"
        self._client = client

    @property
    def name(self) -> str:
        return "ollama"

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def base_url(self) -> str:
        return self._base_url

    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """
        Send text generation request to Ollama HTTP API endpoint.
        """
        payload = {
            "model": self._model_name,
            "prompt": prompt,
            "stream": False,
        }
        if system_prompt:
            payload["system"] = system_prompt

        url = f"{self._base_url}/api/generate"

        try:
            if self._client is not None:
                response = await self._client.post(url, json=payload, timeout=60.0)
            else:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(url, json=payload)

            if response.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail=f"Ollama returned HTTP error {response.status_code}: {response.text}",
                )

            data = response.json()
            return data.get("response", "")

        except httpx.ConnectError as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Failed to connect to local Ollama server at '{self._base_url}'. Ensure Ollama is running.",
            ) from exc
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error communicating with Ollama: {exc}",
            ) from exc

