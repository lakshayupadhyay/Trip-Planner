"""
backend/app/models/user.py

Pydantic v2 data models for user authentication and profile endpoints.

Models
------
UserRegisterRequest  – Request body for POST /api/v1/auth/register.
UserLoginRequest     – Request body for POST /api/v1/auth/login.
TokenResponse        – Response body returned after successful login/register.
UserResponse         – Public user profile (no credentials exposed).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ── Registration ───────────────────────────────────────────────────────────────

class UserRegisterRequest(BaseModel):
    """
    Request body for user registration.

    Enforces minimum-length rules on password and full_name so that
    weak credentials are rejected before they reach the database.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr = Field(..., description="User's email address.")
    password: str = Field(
        ...,
        min_length=8,
        description="Account password (minimum 8 characters).",
    )
    full_name: str = Field(
        ...,
        min_length=2,
        description="User's full name (minimum 2 characters).",
    )


# ── Login ──────────────────────────────────────────────────────────────────────

class UserLoginRequest(BaseModel):
    """Request body for user login."""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr = Field(..., description="Registered email address.")
    password: str   = Field(..., description="Account password.")


# ── Token response ─────────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    """
    Response body returned after a successful login or registration.

    SAFETY: Never include raw passwords, service-role keys, or any
    Supabase internal credentials in this response.
    """

    access_token: str = Field(..., description="JWT access token.")
    token_type: str   = Field(default="bearer", description="Token type (always 'bearer').")
    user_id: str      = Field(..., description="UUID of the authenticated user.")


# ── User profile ───────────────────────────────────────────────────────────────

class UserResponse(BaseModel):
    """
    Public-facing user profile.

    Intentionally omits the password and any server-side credentials.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    full_name: str | None = None
    created_at: str | None = None
