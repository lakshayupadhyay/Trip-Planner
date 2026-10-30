"""
tests/test_trips_api.py

Integration and API endpoint tests for FastAPI endpoints:
- Root /
- /health
- /health/db
- /api/v1/trips (validation, mock service handling)
"""

from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.api.trips import trip_service

client = TestClient(app)


def test_root_endpoint():
    """Verify root / returns 200 and expected status."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Travel Planner API is running!", "status": "ok"}


def test_health_endpoint():
    """Verify /health returns 200 and healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_trip_invalid_payload():
    """Verify POST /api/v1/trips returns 422 Unprocessable Entity when fields are missing."""
    response = client.post("/api/v1/trips/", json={"destination": ""})
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("destination" in str(e["loc"]) for e in errors)


def test_create_trip_invalid_dates():
    """Verify POST /api/v1/trips returns 422 when end_date <= start_date."""
    payload = {
        "user_id": "test-uuid",
        "destination": "Rome",
        "start_date": "2027-05-10",
        "end_date": "2027-05-01",  # Before start date
        "num_travelers": 2,
        "budget": 2000.0,
        "travel_style": "cultural",
        "travel_interests": ["history"],
        "travel_pace": "moderate",
    }
    response = client.post("/api/v1/trips/", json=payload)
    assert response.status_code == 422
    detail = str(response.json()["detail"])
    assert "end_date" in detail


def test_create_trip_success_with_mock_service(monkeypatch):
    """Verify POST /api/v1/trips succeeds and returns TripResponse when service succeeds."""
    mock_record = {
        "id": "trip-uuid-123",
        "user_id": "user-uuid-456",
        "destination": "Barcelona, Spain",
        "start_date": "2027-06-01",
        "end_date": "2027-06-08",
        "num_travelers": 2,
        "budget": 3000.0,
        "travel_style": "relaxation",
        "travel_interests": ["beaches", "food"],
        "dietary_preferences": ["none"],
        "travel_pace": "moderate",
        "additional_requirements": None,
        "status": "pending",
        "created_at": "2026-10-29T21:00:00Z",
    }

    monkeypatch.setattr(trip_service, "create_trip", MagicMock(return_value=mock_record))

    payload = {
        "user_id": "user-uuid-456",
        "destination": "Barcelona, Spain",
        "start_date": "2027-06-01",
        "end_date": "2027-06-08",
        "num_travelers": 2,
        "budget": 3000.0,
        "travel_style": "relaxation",
        "travel_interests": ["beaches", "food"],
        "dietary_preferences": ["none"],
        "travel_pace": "moderate",
    }

    response = client.post("/api/v1/trips/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == "trip-uuid-123"
    assert data["destination"] == "Barcelona, Spain"
    assert data["num_travelers"] == 2
    assert data["budget"] == 3000.0


def test_get_user_trips_with_mock_service(monkeypatch):
    """Verify GET /api/v1/trips/{user_id} returns user trips list."""
    mock_records = [
        {
            "id": "trip-1",
            "user_id": "user-123",
            "destination": "Tokyo",
            "start_date": "2027-09-01",
            "end_date": "2027-09-10",
            "num_travelers": 1,
            "budget": 2500.0,
            "travel_style": "adventure",
            "travel_interests": ["nature"],
            "dietary_preferences": [],
            "travel_pace": "fast",
            "additional_requirements": None,
            "status": "pending",
            "created_at": "2026-10-29T21:00:00Z",
        }
    ]

    monkeypatch.setattr(trip_service, "get_trips_by_user", MagicMock(return_value=mock_records))

    response = client.get("/api/v1/trips/user-123")
    assert response.status_code == 200
    trips = response.json()
    assert len(trips) == 1
    assert trips[0]["destination"] == "Tokyo"

