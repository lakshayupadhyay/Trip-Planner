"""
backend/app/services/providers/huggingface_provider.py

Hugging Face Inference API provider implementation.
Enables execution of open-source models hosted on the Hugging Face Hub.
"""

from __future__ import annotations

import os
from typing import Any
from fastapi import HTTPException
import httpx

from app.config import get_settings
from app.services.providers.base import LLMProvider


class HuggingFaceProvider(LLMProvider):
    """
    LLM provider connecting to Hugging Face Serverless Inference API.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str | None = None,
        client: Any | None = None,
    ) -> None:
        settings = get_settings()
        self._api_key = api_key or settings.HUGGINGFACE_API_KEY
        self._model_name = model_name or "meta-llama/Meta-Llama-3-8B-Instruct"
        self._client = client

    @property
    def name(self) -> str:
        return "huggingface"

    @property
    def model_name(self) -> str:
        return self._model_name

    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """
        Send generation request to Hugging Face Inference API.
        """
        if not self._api_key:
            raise HTTPException(
                status_code=500,
                detail=(
                    "HUGGINGFACE_API_KEY environment variable is not set. "
                    "Configure HUGGINGFACE_API_KEY in your environment to use Hugging Face."
                ),
            )

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        payload = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": 2048,
                "return_full_text": False,
            },
        }

        url = f"https://api-inference.huggingface.co/models/{self._model_name}"

        try:
            if self._client is not None:
                response = await self._client.post(url, headers=headers, json=payload, timeout=60.0)
            else:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(url, headers=headers, json=payload)

            if response.status_code == 401:
                raise HTTPException(status_code=401, detail="Invalid Hugging Face API key.")
            if response.status_code == 429:
                raise HTTPException(status_code=429, detail="Hugging Face rate limit exceeded.")
            if response.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail=f"Hugging Face Inference API error: {response.text}",
                )

            data = response.json()
            if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
                return data[0]["generated_text"]
            if isinstance(data, dict) and "generated_text" in data:
                return data["generated_text"]
            return str(data)

        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to communicate with Hugging Face API: {exc}",
            ) from exc

