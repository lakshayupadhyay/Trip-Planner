"""
backend/app/utils/supabase_client.py

Centralized Supabase client initialization.
Exports a single shared admin Supabase client for backend use,
as well as factories for separating service-role (admin) and anon (public) clients.

SAFETY:
  - Credentials are read via centralized Pydantic Settings.
  - The SERVICE_ROLE key has admin privileges and is strictly backend-only.
  - Public/anon key is separated for client-facing/scoped operations.
"""

from __future__ import annotations

from typing import Any
from supabase import create_client, Client
from app.config import get_settings

_settings = get_settings()

SUPABASE_URL: str = _settings.SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY: str | None = _settings.SUPABASE_SERVICE_ROLE_KEY
SUPABASE_ANON_KEY: str | None = _settings.SUPABASE_KEY or _settings.SUPABASE_ANON_KEY

# Validate required variables
if not SUPABASE_URL:
    raise EnvironmentError(
        "\n\n[ERROR] SUPABASE_URL is not set.\n"
        "  → Open your .env file and add:\n"
        "      SUPABASE_URL=https://your-project-id.supabase.co\n"
        "  → Never hardcode credentials in source code.\n"
    )

if not SUPABASE_SERVICE_ROLE_KEY:
    raise EnvironmentError(
        "\n\n[ERROR] SUPABASE_SERVICE_ROLE_KEY is not set.\n"
        "  → Open your .env file and add:\n"
        "      SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here\n"
        "  → Find this key in: Supabase Dashboard → Project Settings → API\n"
        "  → This key is secret — backend use only. Never send it to the frontend.\n"
    )


def get_supabase_client(use_service_role: bool = True) -> Client:
    """
    Factory function returning a configured Supabase client instance.

    Parameters
    ----------
    use_service_role : bool, default True
        If True, connects with administrative service-role permissions (backend only).
        If False, connects with the public anonymous key.
    """
    key = SUPABASE_SERVICE_ROLE_KEY if use_service_role else (SUPABASE_ANON_KEY or SUPABASE_SERVICE_ROLE_KEY)
    if not key:
        raise ValueError("No Supabase key configured for the requested client type.")
    return create_client(SUPABASE_URL, key)


def get_anon_supabase_client() -> Client:
    """Convenience factory returning an anonymous/public scoped Supabase client."""
    return get_supabase_client(use_service_role=False)


# ── Shared admin client exported for backward compatibility ─────────────────
supabase: Client = get_supabase_client(use_service_role=True)
