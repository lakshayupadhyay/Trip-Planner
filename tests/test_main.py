"""
tests/test_main.py
Application entry point, CORS, and health check tests.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_health():
    """Verify GET / returns 200 ok and X-Process-Time-Ms header."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "x-process-time-ms" in response.headers


def test_health_check():
    """Verify GET /health returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_db_health_endpoint():
    """Verify GET /health/db returns structured status."""
    response = client.get("/health/db")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
