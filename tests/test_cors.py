"""
tests/test_cors.py

CORS preflight and cross-origin request tests.

Validates that:
  1. OPTIONS preflight returns 200 with correct CORS headers for allowed origins.
  2. Disallowed origins are rejected with 400.
  3. FRONTEND_URL is automatically included in ALLOWED_ORIGINS.
  4. Trailing slashes in origin URLs do not cause mismatches.
  5. POST requests from allowed origins carry the correct CORS response headers.
  6. Multiple endpoints respond to preflight correctly.

NOTE:
  Tests build a minimal FastAPI app with CORSMiddleware configured identically
  to main.py, avoiding the Supabase client initialization that hangs in CI/sandbox.
"""

import pytest
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from app.config import Settings


# ── Constants ─────────────────────────────────────────────────────────────────

VERCEL_ORIGIN = "https://trip-planner-cyan-nu.vercel.app"
RENDER_ORIGIN = "https://trip-planner-qain.onrender.com"
LOCALHOST_ORIGIN = "http://localhost:5173"
DISALLOWED_ORIGIN = "https://malicious-site.example.com"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _build_test_app(allowed_origins: list[str]) -> FastAPI:
    """Build a minimal FastAPI app with CORSMiddleware matching main.py config."""
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.post("/api/v1/trips/")
    def _create_trip():
        return {"id": "test-trip-id", "destination": "Tokyo"}

    @app.post("/api/v1/itinerary/generate")
    def _generate():
        return {"days": []}

    @app.post("/api/v1/recommendations/destinations")
    def _recommend():
        return {"recommendations": []}

    return app


def _settings_with_vercel(**overrides):
    """Return a Settings instance where FRONTEND_URL is the Vercel origin."""
    defaults = dict(
        FRONTEND_URL=VERCEL_ORIGIN,
        BACKEND_URL=RENDER_ORIGIN,
        SUPABASE_URL="https://test.supabase.co",
        SUPABASE_SERVICE_ROLE_KEY="test-key",
    )
    defaults.update(overrides)
    return Settings(**defaults)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def vercel_settings():
    """Settings with Vercel origin as FRONTEND_URL."""
    return _settings_with_vercel()


@pytest.fixture
def client(vercel_settings):
    """TestClient whose app has the Vercel origin in ALLOWED_ORIGINS."""
    app = _build_test_app(vercel_settings.ALLOWED_ORIGINS)
    return TestClient(app)


@pytest.fixture
def client_trailing_slash():
    """TestClient where FRONTEND_URL had a trailing slash (normalized away)."""
    settings = _settings_with_vercel(FRONTEND_URL=VERCEL_ORIGIN + "/")
    app = _build_test_app(settings.ALLOWED_ORIGINS)
    return TestClient(app)


# ── 1. Preflight with allowed Vercel origin ───────────────────────────────────

def test_cors_preflight_vercel_origin_returns_200(client):
    """OPTIONS preflight from the Vercel origin must return 200 with CORS headers."""
    response = client.options(
        "/api/v1/trips/",
        headers={
            "Origin": VERCEL_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type, authorization",
        },
    )
    assert response.status_code == 200, (
        f"Expected 200 for preflight but got {response.status_code}: {response.text}"
    )
    assert response.headers["access-control-allow-origin"] == VERCEL_ORIGIN
    # Methods must include POST
    allowed_methods = response.headers.get("access-control-allow-methods", "")
    assert "POST" in allowed_methods.upper()
    # Headers must include content-type and authorization
    allowed_headers = response.headers.get("access-control-allow-headers", "").lower()
    assert "content-type" in allowed_headers
    assert "authorization" in allowed_headers
    # Credentials
    assert response.headers.get("access-control-allow-credentials") == "true"


# ── 2. Preflight with localhost origin ────────────────────────────────────────

def test_cors_preflight_localhost_returns_200(client):
    """OPTIONS preflight from localhost must also succeed (dev environment)."""
    response = client.options(
        "/api/v1/trips/",
        headers={
            "Origin": LOCALHOST_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == LOCALHOST_ORIGIN


# ── 3. Preflight with disallowed origin ───────────────────────────────────────

def test_cors_preflight_disallowed_origin_returns_400(client):
    """OPTIONS preflight from an origin not in ALLOWED_ORIGINS must be rejected."""
    response = client.options(
        "/api/v1/trips/",
        headers={
            "Origin": DISALLOWED_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers


# ── 4. Trailing slash in FRONTEND_URL ─────────────────────────────────────────

def test_cors_trailing_slash_frontend_url_still_works(client_trailing_slash):
    """FRONTEND_URL with trailing slash must still match the origin without one."""
    response = client_trailing_slash.options(
        "/api/v1/trips/",
        headers={
            "Origin": VERCEL_ORIGIN,  # No trailing slash
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == VERCEL_ORIGIN


# ── 5. POST request carries CORS headers ─────────────────────────────────────

def test_post_request_has_cors_headers(client):
    """Actual POST from Vercel origin must include Access-Control-Allow-Origin."""
    response = client.post(
        "/api/v1/trips/",
        headers={
            "Origin": VERCEL_ORIGIN,
            "Content-Type": "application/json",
        },
    )
    assert response.headers.get("access-control-allow-origin") == VERCEL_ORIGIN
    assert response.headers.get("access-control-allow-credentials") == "true"


# ── 6. FRONTEND_URL auto-included in ALLOWED_ORIGINS (config unit tests) ─────

def test_frontend_url_auto_included_in_allowed_origins():
    """Settings with FRONTEND_URL must automatically add it to ALLOWED_ORIGINS."""
    settings = _settings_with_vercel()
    assert VERCEL_ORIGIN in settings.ALLOWED_ORIGINS


def test_backend_url_auto_included_in_allowed_origins():
    """Settings with BACKEND_URL must automatically add it to ALLOWED_ORIGINS."""
    settings = _settings_with_vercel()
    assert RENDER_ORIGIN in settings.ALLOWED_ORIGINS


def test_allowed_origins_deduplication():
    """Origins must not be duplicated when FRONTEND_URL is also in ALLOWED_ORIGINS."""
    settings = Settings(
        FRONTEND_URL=VERCEL_ORIGIN,
        ALLOWED_ORIGINS=f"{VERCEL_ORIGIN},http://localhost:5173",
        SUPABASE_URL="https://test.supabase.co",
        SUPABASE_SERVICE_ROLE_KEY="test-key",
    )
    count = settings.ALLOWED_ORIGINS.count(VERCEL_ORIGIN)
    assert count == 1, f"Vercel origin appeared {count} times, expected exactly 1"


# ── 7. Preflight on other endpoints ──────────────────────────────────────────

def test_cors_preflight_itinerary_endpoint(client):
    """OPTIONS preflight on /api/v1/itinerary/generate must also succeed."""
    response = client.options(
        "/api/v1/itinerary/generate",
        headers={
            "Origin": VERCEL_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == VERCEL_ORIGIN


def test_cors_preflight_recommendations_endpoint(client):
    """OPTIONS preflight on /api/v1/recommendations/destinations must succeed."""
    response = client.options(
        "/api/v1/recommendations/destinations",
        headers={
            "Origin": VERCEL_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == VERCEL_ORIGIN
