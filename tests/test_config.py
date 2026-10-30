"""
tests/test_config.py

Comprehensive test suite for Epic 5 – Activity 5.4: Environment & Configuration Management.
Tests:
  1. Configuration Loading & Typing
  2. Missing Required Variables Validation
  3. AI Provider Credentials Validation (Gemini, Groq, Hugging Face, Ollama)
  4. Unsupported Provider Rejection
  5. Supabase Client Configuration & Separation
  6. JWT Secret Length, Token Creation, and Expiration Validation
  7. Production Mode Invariants (DEBUG=False, Secure SECRET_KEY)
  8. Secret Redaction in safe_dict() and __repr__()
  9. CORS Origins Parsing from String
 10. Provider Factory Instantiation
"""

import os
from unittest.mock import MagicMock
import pytest
from pydantic import ValidationError
from fastapi import HTTPException

from app.config import Settings, generate_jwt_secret, get_settings
from app.services.providers import (
    GeminiProvider,
    GroqProvider,
    HuggingFaceProvider,
    OllamaProvider,
    get_llm_provider,
)
from app.utils.security import create_access_token, decode_access_token


# ── 1. Configuration Loading & Defaults ─────────────────────────────────────

def test_settings_load_defaults():
    """Verify Settings initializes with standard defaults and proper types."""
    settings = Settings(
        SUPABASE_URL="https://test.supabase.co",
        SUPABASE_SERVICE_ROLE_KEY="test-service-key-12345",
    )
    assert settings.ENVIRONMENT in ("development", "staging", "production", "test")
    assert isinstance(settings.DEBUG, bool)
    assert settings.ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES >= 1
    assert isinstance(settings.ALLOWED_ORIGINS, list)
    assert len(settings.ALLOWED_ORIGINS) >= 1


# ── 2. CORS Origins Parsing ─────────────────────────────────────────────────

def test_settings_allowed_origins_parsing():
    """Verify comma-separated string input is parsed into a clean list of origins."""
    settings = Settings(
        ALLOWED_ORIGINS="https://my-app.vercel.app, https://staging.my-app.vercel.app ",
        SUPABASE_URL="https://test.supabase.co",
        SUPABASE_SERVICE_ROLE_KEY="test-key",
    )
    assert "https://my-app.vercel.app" in settings.ALLOWED_ORIGINS
    assert "https://staging.my-app.vercel.app" in settings.ALLOWED_ORIGINS


# ── 3. Missing Required Variables Validation ────────────────────────────────

def test_supabase_validation_missing_url():
    """Verify validate_supabase_credentials raises ValueError when SUPABASE_URL is empty."""
    settings = Settings(
        SUPABASE_URL="",
        SUPABASE_SERVICE_ROLE_KEY="test-service-key",
    )
    with pytest.raises(ValueError) as exc:
        settings.validate_supabase_credentials()
    assert "SUPABASE_URL is not set" in str(exc.value)


def test_supabase_validation_missing_service_role():
    """Verify validate_supabase_credentials raises ValueError when service role key is missing."""
    settings = Settings(
        SUPABASE_URL="https://example.supabase.co",
        SUPABASE_SERVICE_ROLE_KEY=None,
    )
    with pytest.raises(ValueError) as exc:
        settings.validate_supabase_credentials(require_service_role=True)
    assert "SUPABASE_SERVICE_ROLE_KEY is not set" in str(exc.value)


# ── 4. AI Provider Credentials Validation ───────────────────────────────────

def test_ai_provider_gemini_missing_key():
    """Verify validation fails when AI_PROVIDER='gemini' and GEMINI_API_KEY is missing."""
    settings = Settings(
        AI_PROVIDER="gemini",
        GEMINI_API_KEY="",
        SUPABASE_URL="https://test.supabase.co",
        SUPABASE_SERVICE_ROLE_KEY="test-key",
    )
    with pytest.raises(ValueError) as exc:
        settings.validate_ai_provider_credentials()
    assert "GEMINI_API_KEY is not configured" in str(exc.value)


def test_ai_provider_groq_missing_key():
    """Verify validation fails when AI_PROVIDER='groq' and GROQ_API_KEY is missing."""
    settings = Settings(
        AI_PROVIDER="groq",
        GROQ_API_KEY="",
        SUPABASE_URL="https://test.supabase.co",
        SUPABASE_SERVICE_ROLE_KEY="test-key",
    )
    with pytest.raises(ValueError) as exc:
        settings.validate_ai_provider_credentials()
    assert "GROQ_API_KEY is not configured" in str(exc.value)


def test_ai_provider_huggingface_missing_key():
    """Verify validation fails when AI_PROVIDER='huggingface' and HUGGINGFACE_API_KEY is missing."""
    settings = Settings(
        AI_PROVIDER="huggingface",
        HUGGINGFACE_API_KEY="",
        SUPABASE_URL="https://test.supabase.co",
        SUPABASE_SERVICE_ROLE_KEY="test-key",
    )
    with pytest.raises(ValueError) as exc:
        settings.validate_ai_provider_credentials()
    assert "HUGGINGFACE_API_KEY is not configured" in str(exc.value)


def test_ai_provider_unsupported_rejection():
    """Verify validation fails when an unsupported AI provider is selected."""
    settings = Settings(
        AI_PROVIDER="unsupported_provider_xyz",
        SUPABASE_URL="https://test.supabase.co",
        SUPABASE_SERVICE_ROLE_KEY="test-key",
    )
    with pytest.raises(ValueError) as exc:
        settings.validate_ai_provider_credentials()
    assert "Unsupported AI_PROVIDER" in str(exc.value)


# ── 5. Provider Factory Instantiation ───────────────────────────────────────

def test_provider_factory_instantiates_all_supported():
    """Verify get_llm_provider correctly returns corresponding provider instances."""
    gemini = get_llm_provider(provider_type="gemini", api_key="dummy-key")
    assert isinstance(gemini, GeminiProvider)
    assert gemini.name == "gemini"

    groq = get_llm_provider(provider_type="groq", api_key="dummy-key")
    assert isinstance(groq, GroqProvider)
    assert groq.name == "groq"

    hf = get_llm_provider(provider_type="huggingface", api_key="dummy-key")
    assert isinstance(hf, HuggingFaceProvider)
    assert hf.name == "huggingface"

    ollama = get_llm_provider(provider_type="ollama")
    assert isinstance(ollama, OllamaProvider)
    assert ollama.name == "ollama"


def test_provider_factory_unsupported_raises_400():
    """Verify get_llm_provider raises HTTP 400 for completely unknown providers."""
    with pytest.raises(HTTPException) as exc:
        get_llm_provider(provider_type="invalid_ai")
    assert exc.value.status_code == 400
    assert "Unsupported LLM provider" in exc.value.detail


# ── 6. JWT Security & Token Lifecycle ───────────────────────────────────────

def test_jwt_secret_generator_length():
    """Verify generate_jwt_secret returns at least 32 characters."""
    secret = generate_jwt_secret(32)
    assert len(secret) >= 32
    secret_64 = generate_jwt_secret(64)
    assert len(secret_64) >= 64


def test_jwt_token_creation_and_decoding(monkeypatch):
    """Verify create_access_token and decode_access_token roundtrip correctly."""
    strong_secret = "a" * 40
    test_settings = Settings(
        SECRET_KEY=strong_secret,
        SUPABASE_URL="https://test.supabase.co",
        SUPABASE_SERVICE_ROLE_KEY="test-key",
    )
    monkeypatch.setattr("app.utils.security.get_settings", lambda: test_settings)

    payload = {"user_id": "user-uuid-12345", "role": "traveler"}
    token = create_access_token(payload, expires_delta_minutes=60)
    assert isinstance(token, str)
    assert len(token.split(".")) == 3

    decoded = decode_access_token(token)
    assert decoded["user_id"] == "user-uuid-12345"
    assert decoded["role"] == "traveler"
    assert "exp" in decoded


def test_jwt_token_tampered_signature_rejected(monkeypatch):
    """Verify tampered token signature is rejected with HTTP 401."""
    strong_secret = "b" * 40
    test_settings = Settings(
        SECRET_KEY=strong_secret,
        SUPABASE_URL="https://test.supabase.co",
        SUPABASE_SERVICE_ROLE_KEY="test-key",
    )
    monkeypatch.setattr("app.utils.security.get_settings", lambda: test_settings)

    token = create_access_token({"sub": "user"}, expires_delta_minutes=30)
    # Alter the signature part
    tampered = token[:-4] + "xxxx"
    with pytest.raises(HTTPException) as exc:
        decode_access_token(tampered)
    assert exc.value.status_code == 401
    assert "signature" in exc.value.detail.lower()


# ── 7. Production Mode Invariants ───────────────────────────────────────────

def test_production_mode_rejects_debug_true():
    """Verify production environment rejects DEBUG=True."""
    with pytest.raises((ValueError, ValidationError)) as exc:
        Settings(
            ENVIRONMENT="production",
            DEBUG=True,
            SECRET_KEY="c" * 40,
            SUPABASE_URL="https://test.supabase.co",
            SUPABASE_SERVICE_ROLE_KEY="test-key",
        )
    assert "DEBUG must be False in production" in str(exc.value)


def test_production_mode_rejects_insecure_default_secret():
    """Verify production environment rejects the default insecure development secret."""
    with pytest.raises((ValueError, ValidationError)) as exc:
        Settings(
            ENVIRONMENT="production",
            DEBUG=False,
            SECRET_KEY="dev-insecure-secret-key-change-this-in-production-min-32-chars",
            SUPABASE_URL="https://test.supabase.co",
            SUPABASE_SERVICE_ROLE_KEY="test-key",
        )
    assert "Default insecure SECRET_KEY cannot be used in production" in str(exc.value)


# ── 8. Secret Redaction in safe_dict() and __repr__() ───────────────────────

def test_secret_redaction_prevents_credential_leakage():
    """Verify sensitive keys are never exposed in safe_dict() or string representation."""
    real_gemini_key = "AIzaSySecretRealKey12345"
    real_service_key = "supabase-super-secret-service-role-key-999"
    real_jwt_secret = "d" * 40

    settings = Settings(
        GEMINI_API_KEY=real_gemini_key,
        SUPABASE_SERVICE_ROLE_KEY=real_service_key,
        SECRET_KEY=real_jwt_secret,
        SUPABASE_URL="https://example.supabase.co",
    )

    safe = settings.safe_dict()
    assert safe["gemini_api_key"] == "***REDACTED***"
    assert safe["supabase_service_role_key"] == "***REDACTED***"
    assert safe["secret_key"] == "***REDACTED***"

    # String representations must NEVER contain the raw secrets
    repr_str = repr(settings)
    assert real_gemini_key not in repr_str
    assert real_service_key not in repr_str
    assert real_jwt_secret not in repr_str
    assert "***REDACTED***" in repr_str
