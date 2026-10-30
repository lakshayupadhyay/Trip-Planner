"""
tests/test_itinerary_api.py

API endpoint tests for the itinerary prompt preview endpoint:
- POST /api/v1/itinerary/prompt-preview (200 success with destination, duration_days, prompt)
- Validation errors on missing destination, invalid dates, and invalid budget
- Deterministic output verification
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_prompt_preview_endpoint_success():
    """Verify POST /api/v1/itinerary/prompt-preview returns 200 and matches expected structure."""
    payload = {
        "destination": "Germany",
        "start_date": "2027-06-01",
        "end_date": "2027-06-07",
        "num_travelers": 2,
        "budget": 2800.0,
        "travel_style": "cultural",
        "travel_interests": ["history", "castles", "food"],
        "dietary_preferences": ["none"],
        "travel_pace": "moderate",
        "additional_requirements": "Prefer rail travel between cities",
    }

    response = client.post("/api/v1/itinerary/prompt-preview", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["destination"] == "Germany"
    assert data["duration_days"] == 7
    assert isinstance(data["prompt"], str)
    assert "1. AI Role and Instructions" in data["prompt"]
    assert "7 Days (6 Nights)" in data["prompt"]
    assert "Germany" in data["prompt"]
    assert "rail travel" in data["prompt"]


def test_prompt_preview_invalid_dates():
    """Verify endpoint rejects payloads where end_date <= start_date with HTTP 422."""
    payload = {
        "destination": "Paris, France",
        "start_date": "2027-06-10",
        "end_date": "2027-06-05",  # Invalid
        "num_travelers": 1,
        "budget": 1500.0,
        "travel_style": "relaxation",
        "travel_interests": ["art"],
        "travel_pace": "slow",
    }

    response = client.post("/api/v1/itinerary/prompt-preview", json=payload)
    assert response.status_code == 422
    assert "end_date" in str(response.json()["detail"])


def test_prompt_preview_invalid_budget():
    """Verify endpoint rejects negative or zero budget with HTTP 422."""
    payload = {
        "destination": "Paris, France",
        "start_date": "2027-06-01",
        "end_date": "2027-06-05",
        "num_travelers": 1,
        "budget": -50.0,  # Invalid
        "travel_style": "cultural",
        "travel_interests": ["history"],
        "travel_pace": "moderate",
    }

    response = client.post("/api/v1/itinerary/prompt-preview", json=payload)
    assert response.status_code == 422


def test_prompt_preview_missing_destination():
    """Verify endpoint rejects missing or empty destination with HTTP 422."""
    payload = {
        "destination": "",  # Invalid: min 2 chars
        "start_date": "2027-06-01",
        "end_date": "2027-06-05",
        "num_travelers": 1,
        "budget": 1000.0,
        "travel_style": "cultural",
        "travel_interests": ["history"],
        "travel_pace": "moderate",
    }

    response = client.post("/api/v1/itinerary/prompt-preview", json=payload)
    assert response.status_code == 422


def test_prompt_preview_deterministic():
    """Verify that multiple invocations with identical parameters produce deterministic prompts."""
    payload = {
        "destination": "London, UK",
        "start_date": "2027-09-01",
        "end_date": "2027-09-04",
        "num_travelers": 2,
        "budget": 2000.0,
        "travel_style": "cultural",
        "travel_interests": ["theatre", "museums"],
        "travel_pace": "moderate",
    }

    res1 = client.post("/api/v1/itinerary/prompt-preview", json=payload).json()
    res2 = client.post("/api/v1/itinerary/prompt-preview", json=payload).json()

    assert res1["prompt"] == res2["prompt"]
    assert res1["duration_days"] == res2["duration_days"] == 4

