"""
backend/app/utils/security.py

Security utilities for JWT token creation, verification, and secret management.
Configured via centralized Pydantic Settings.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any
from fastapi import HTTPException

from app.config import get_settings


def create_access_token(
    data: dict[str, Any],
    expires_delta_minutes: int | None = None,
) -> str:
    """
    Create a standard HMAC-SHA256 signed JWT token without external heavy dependencies.
    Encodes payload with expiration, issued-at, and signs with SECRET_KEY.
    """
    settings = get_settings()
    expire_minutes = expires_delta_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    now = int(time.time())
    exp = now + (expire_minutes * 60)

    header = {"alg": settings.ALGORITHM, "typ": "JWT"}
    payload = {**data, "iat": now, "exp": exp}

    def _b64encode(val: dict[str, Any]) -> str:
        dumped = json.dumps(val, separators=(",", ":")).encode("utf-8")
        return base64.urlsafe_b64encode(dumped).decode("utf-8").rstrip("=")

    header_b64 = _b64encode(header)
    payload_b64 = _b64encode(payload)
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")

    secret_bytes = settings.SECRET_KEY.encode("utf-8")
    signature = hmac.new(secret_bytes, signing_input, hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(signature).decode("utf-8").rstrip("=")

    return f"{header_b64}.{payload_b64}.{sig_b64}"


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Verify and decode an HMAC-SHA256 signed JWT token.
    Raises HTTPException(401) on invalid signature or expiration.
    """
    settings = get_settings()
    parts = token.strip().split(".")
    if len(parts) != 3:
        raise HTTPException(status_code=401, detail="Invalid token structure.")

    header_b64, payload_b64, sig_b64 = parts
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")

    # Verify signature
    secret_bytes = settings.SECRET_KEY.encode("utf-8")
    expected_sig = hmac.new(secret_bytes, signing_input, hashlib.sha256).digest()
    expected_sig_b64 = base64.urlsafe_b64encode(expected_sig).decode("utf-8").rstrip("=")

    if not hmac.compare_digest(sig_b64, expected_sig_b64):
        raise HTTPException(status_code=401, detail="Invalid token signature.")

    # Decode payload
    def _b64decode(val: str) -> dict[str, Any]:
        padded = val + "=" * (-len(val) % 4)
        raw = base64.urlsafe_b64decode(padded.encode("utf-8"))
        return json.loads(raw.decode("utf-8"))

    payload = _b64decode(payload_b64)
    now = int(time.time())
    if payload.get("exp", 0) < now:
        raise HTTPException(status_code=401, detail="Token has expired.")

    return payload

