"""
backend/app/config.py

Centralized configuration management for the Personalized Travel Itinerary Planner.
Built with Pydantic Settings (pydantic-settings v2).

Handles:
  - Environment variable discovery and typed validation (.env, system env)
  - Multi-environment switching (development, staging, production, test)
  - Supabase credentials (separate anon and service-role keys)
  - AI Providers (Gemini, Groq, Hugging Face, Ollama)
  - JWT security (secret length validation, configurable algorithm and expiry)
  - Server and CORS configuration
  - Safe secret redaction in logs and string representations
"""

from __future__ import annotations

import os
import secrets
from functools import lru_cache
from typing import Any, Literal
from pydantic import AliasChoices, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

SENSITIVE_KEYS: set[str] = {
    "supabase_service_role_key",
    "secret_key",
    "gemini_api_key",
    "groq_api_key",
    "huggingface_api_key",
    "openai_api_key",
    "redis_url",
}


class Settings(BaseSettings):
    """
    Application Settings schema with hierarchical validation and defaults.
    Loads from .env in project root or environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env", "backend/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ── Server & Runtime Environment ──────────────────────────────────────────
    ENVIRONMENT: Literal["development", "staging", "production", "test"] = Field(
        default="development",
        validation_alias=AliasChoices("ENVIRONMENT", "APP_ENV"),
        description="Target runtime environment",
    )
    DEBUG: bool = Field(default=False, description="FastAPI debug flag")
    BACKEND_URL: str = Field(
        default="http://localhost:8000",
        description="Backend API base URL",
    )
    FRONTEND_URL: str = Field(
        default="http://localhost:5173",
        description="Frontend web application base URL",
    )
    ALLOWED_ORIGINS: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ],
        description="Allowed CORS origins",
    )
    CORS_ORIGINS: str | None = Field(
        default=None,
        description="Comma-separated CORS origins string override",
    )
    LOG_LEVEL: str = Field(default="INFO", description="Standard logging level")

    # ── Supabase Configuration ────────────────────────────────────────────────
    SUPABASE_URL: str = Field(
        default="",
        description="Supabase project URL",
    )
    SUPABASE_KEY: str | None = Field(
        default=None,
        validation_alias=AliasChoices("SUPABASE_KEY", "SUPABASE_ANON_KEY"),
        description="Supabase public/anon key",
    )
    SUPABASE_SERVICE_ROLE_KEY: str | None = Field(
        default=None,
        description="Supabase administrative service-role key (backend only)",
    )

    # ── JWT Authentication & Security ─────────────────────────────────────────
    SECRET_KEY: str = Field(
        default="dev-insecure-secret-key-change-this-in-production-min-32-chars",
        min_length=32,
        description="Secret key for JWT token signing (minimum 32 characters)",
    )
    ALGORITHM: str = Field(
        default="HS256",
        description="JWT cryptographic signing algorithm",
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=60 * 24,  # 24 hours
        ge=1,
        description="JWT token validity in minutes",
    )

    # ── AI / LLM Providers ────────────────────────────────────────────────────
    AI_PROVIDER: str = Field(
        default="gemini",
        validation_alias=AliasChoices("AI_PROVIDER", "LLM_PROVIDER"),
        description="Primary AI provider: 'gemini', 'groq', 'huggingface', 'ollama'",
    )
    GEMINI_API_KEY: str | None = Field(default=None, description="Google Gemini API key")
    GEMINI_MODEL: str = Field(default="gemini-3.8-flash", description="Google Gemini model identifier")
    GROQ_API_KEY: str | None = Field(default=None, description="Groq Cloud API key")
    GROQ_MODEL: str = Field(default="llama-3.3-70b-versatile", description="Groq model identifier")
    HUGGINGFACE_API_KEY: str | None = Field(default=None, description="Hugging Face API token")
    OLLAMA_BASE_URL: str = Field(
        default="http://localhost:11434",
        description="Base URL for local Ollama server instance",
    )
    OPENAI_API_KEY: str | None = Field(default=None, description="Optional OpenAI API key")

    # ── Optional Infrastructure ───────────────────────────────────────────────
    REDIS_URL: str | None = Field(default=None, description="Optional Redis caching URL")

    # ── Field Validators & Normalizers ────────────────────────────────────────

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: Any) -> list[str]:
        """Allow origins to be defined as comma-separated string or list."""
        if isinstance(value, str):
            return [o.strip() for o in value.split(",") if o.strip()]
        if isinstance(value, (list, tuple)):
            return [str(o).strip() for o in value if str(o).strip()]
        return value

    @model_validator(mode="after")
    def sync_aliases_and_validate(self) -> "Settings":
        """Reconcile environment variable aliases and validate consistency."""
        object.__setattr__(self, "AI_PROVIDER", self.AI_PROVIDER.strip().lower())

        # Integrate CORS_ORIGINS override if set
        if self.CORS_ORIGINS:
            parsed = [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]
            combined = list(dict.fromkeys(self.ALLOWED_ORIGINS + parsed))
            object.__setattr__(self, "ALLOWED_ORIGINS", combined)

        # Production Environment Validation
        if self.ENVIRONMENT == "production":
            if self.DEBUG is True:
                raise ValueError("DEBUG must be False in production environment.")
            if "insecure" in self.SECRET_KEY.lower():
                raise ValueError(
                    "Default insecure SECRET_KEY cannot be used in production. "
                    "Generate a strong 32+ character key via `secrets.token_urlsafe(32)`."
                )

        return self

    # ── Helper Validation Methods ─────────────────────────────────────────────

    def validate_ai_provider_credentials(self) -> None:
        """
        Validate that the currently selected AI provider has valid credentials configured.
        Raises ValueError with clear, actionable message if missing.
        """
        provider = self.AI_PROVIDER.lower()
        if provider == "gemini":
            if not self.GEMINI_API_KEY or not self.GEMINI_API_KEY.strip():
                raise ValueError(
                    "AI_PROVIDER is set to 'gemini' but GEMINI_API_KEY is not configured in environment. "
                    "Set GEMINI_API_KEY in your .env or platform secrets."
                )
        elif provider == "groq":
            if not self.GROQ_API_KEY or not self.GROQ_API_KEY.strip():
                raise ValueError(
                    "AI_PROVIDER is set to 'groq' but GROQ_API_KEY is not configured in environment. "
                    "Set GROQ_API_KEY in your .env or platform secrets."
                )
        elif provider == "huggingface":
            if not self.HUGGINGFACE_API_KEY or not self.HUGGINGFACE_API_KEY.strip():
                raise ValueError(
                    "AI_PROVIDER is set to 'huggingface' but HUGGINGFACE_API_KEY is not configured. "
                    "Set HUGGINGFACE_API_KEY in your .env or platform secrets."
                )
        elif provider == "ollama":
            if not self.OLLAMA_BASE_URL or not self.OLLAMA_BASE_URL.strip():
                raise ValueError(
                    "AI_PROVIDER is set to 'ollama' but OLLAMA_BASE_URL is not set."
                )
        else:
            raise ValueError(
                f"Unsupported AI_PROVIDER '{provider}'. Supported providers are: "
                f"'gemini', 'groq', 'huggingface', 'ollama'."
            )

    def validate_supabase_credentials(self, require_service_role: bool = True) -> None:
        """
        Validate that Supabase URL and service role credentials are configured.
        """
        if not self.SUPABASE_URL or not self.SUPABASE_URL.strip():
            raise ValueError(
                "SUPABASE_URL is not set. Please specify your Supabase project URL in .env."
            )
        if require_service_role and (not self.SUPABASE_SERVICE_ROLE_KEY or not self.SUPABASE_SERVICE_ROLE_KEY.strip()):
            raise ValueError(
                "SUPABASE_SERVICE_ROLE_KEY is not set. Backend operations require the service-role admin key."
            )

    def safe_dict(self) -> dict[str, Any]:
        """
        Return settings as a dictionary with all sensitive keys safely redacted.
        Safe for logging, debugging, or telemetry output.
        """
        raw = self.model_dump()
        redacted: dict[str, Any] = {}
        for k, v in raw.items():
            if k.lower() in SENSITIVE_KEYS and v is not None:
                redacted[k] = "***REDACTED***"
                redacted[k.lower()] = "***REDACTED***"
                redacted[k.upper()] = "***REDACTED***"
            else:
                redacted[k] = v
                redacted[k.lower()] = v
        return redacted

    def __repr__(self) -> str:
        """String representation of settings with all secrets strictly redacted."""
        items = [f"{k}={v!r}" for k, v in self.safe_dict().items()]
        return f"Settings({', '.join(items)})"

    def __str__(self) -> str:
        return self.__repr__()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached singleton application settings instance."""
    return Settings()


def generate_jwt_secret(length: int = 32) -> str:
    """Generate a cryptographically secure random token suitable for SECRET_KEY."""
    return secrets.token_urlsafe(max(32, length))
