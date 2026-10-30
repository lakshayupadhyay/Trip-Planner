"""
tests/test_itinerary_generation_api.py

API endpoint integration tests for:
- POST /api/v1/itinerary/generate
- POST /api/v1/itinerary/generate/ (trailing slash)
- Request payload validation (422)
- Upstream service error propagation
"""

from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException
from app.main import app
from app.models.itinerary import (
    Activity,
    DailyBudget,
    DayItinerary,
    ItineraryResponse,
    Transportation,
)

client = TestClient(app)


def get_mock_itinerary_response():
    """Build a valid mock ItineraryResponse for API tests."""
    return ItineraryResponse(
        destination="Kyoto, Japan",
        start_date="2027-04-01",
        end_date="2027-04-02",
        duration_days=2,
        total_budget=1500.0,
        travel_style="cultural",
        travel_pace="moderate",
        trip_summary="A balanced 2-day cultural journey through Kyoto.",
        total_estimated_cost="~$380 USD total",
        packing_and_prep_tips=["Wear walking shoes", "Carry an umbrella"],
        provider_used="gemini",
        days=[
            DayItinerary(
                day_number=1,
                date="2027-04-01",
                theme="Historic Temples and Peaceful Canals",
                morning_activity=Activity(
                    time_slot="morning",
                    name="Fushimi Inari Shrine",
                    description="Climb through thousands of vermilion torii gates.",
                    suggested_duration="2 hours",
                    estimated_cost="Free",
                ),
                afternoon_activity=Activity(
                    time_slot="afternoon",
                    name="Kiyomizu-dera",
                    description="Historic wooden terrace with panoramic mountain views.",
                    suggested_duration="2 hours",
                    estimated_cost="¥400",
                ),
                transportation=Transportation(
                    mode="JR Nara Line & Walking",
                    estimated_time="20 mins",
                    estimated_cost="¥150",
                ),
                daily_budget=DailyBudget(
                    activities_cost="~$3 USD",
                    dining_cost="~$45 USD",
                    transportation_cost="~$3 USD",
                    total_daily_estimated="~$51 USD",
                ),
                practical_tips="Visit Fushimi Inari before 8am.",
            )
        ],
    )


def test_generate_itinerary_endpoint_success():
    """Verify POST /api/v1/itinerary/generate returns 200 with structured response."""
    mock_resp = get_mock_itinerary_response()

    with patch(
        "app.api.itinerary.itinerary_service.generate_itinerary",
        new_callable=AsyncMock,
        return_value=mock_resp,
    ):
        payload = {
            "destination": "Kyoto, Japan",
            "start_date": "2027-04-01",
            "end_date": "2027-04-02",
            "num_travelers": 2,
            "budget": 1500.0,
            "travel_style": "cultural",
            "travel_interests": ["history", "food"],
            "travel_pace": "moderate",
        }
        response = client.post("/api/v1/itinerary/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["destination"] == "Kyoto, Japan"
        assert len(data["days"]) == 1
        assert data["days"][0]["morning_activity"]["name"] == "Fushimi Inari Shrine"
        assert data["provider_used"] == "gemini"


def test_generate_itinerary_endpoint_trailing_slash():
    """Verify POST /api/v1/itinerary/generate/ handles trailing slash cleanly."""
    mock_resp = get_mock_itinerary_response()

    with patch(
        "app.api.itinerary.itinerary_service.generate_itinerary",
        new_callable=AsyncMock,
        return_value=mock_resp,
    ):
        payload = {
            "destination": "Kyoto, Japan",
            "start_date": "2027-04-01",
            "end_date": "2027-04-02",
            "num_travelers": 2,
            "budget": 1500.0,
            "travel_style": "cultural",
            "travel_interests": ["history", "food"],
            "travel_pace": "moderate",
        }
        response = client.post("/api/v1/itinerary/generate/", json=payload)
        assert response.status_code == 200


def test_generate_itinerary_invalid_dates_422():
    """Verify end_date <= start_date returns HTTP 422."""
    payload = {
        "destination": "Kyoto, Japan",
        "start_date": "2027-04-05",
        "end_date": "2027-04-01",  # Invalid
        "num_travelers": 1,
        "budget": 1000.0,
        "travel_style": "cultural",
        "travel_interests": ["history"],
    }
    response = client.post("/api/v1/itinerary/generate", json=payload)
    assert response.status_code == 422


def test_generate_itinerary_invalid_budget_422():
    """Verify negative budget returns HTTP 422."""
    payload = {
        "destination": "Kyoto, Japan",
        "start_date": "2027-04-01",
        "end_date": "2027-04-05",
        "num_travelers": 1,
        "budget": -100.0,  # Invalid
        "travel_style": "cultural",
        "travel_interests": ["history"],
    }
    response = client.post("/api/v1/itinerary/generate", json=payload)
    assert response.status_code == 422


def test_generate_itinerary_missing_destination_422():
    """Verify missing destination returns HTTP 422."""
    payload = {
        "destination": "",
        "start_date": "2027-04-01",
        "end_date": "2027-04-05",
        "budget": 1000.0,
        "travel_style": "cultural",
        "travel_interests": ["history"],
    }
    response = client.post("/api/v1/itinerary/generate", json=payload)
    assert response.status_code == 422


def test_generate_itinerary_service_error_propagation():
    """Verify service exceptions pass through cleanly."""
    with patch(
        "app.api.itinerary.itinerary_service.generate_itinerary",
        new_callable=AsyncMock,
        side_effect=HTTPException(status_code=502, detail="Upstream AI provider error"),
    ):
        payload = {
            "destination": "Kyoto, Japan",
            "start_date": "2027-04-01",
            "end_date": "2027-04-03",
            "budget": 1000.0,
            "travel_style": "cultural",
            "travel_interests": ["history"],
        }
        response = client.post("/api/v1/itinerary/generate", json=payload)
        assert response.status_code == 502
        assert response.json()["detail"] == "Upstream AI provider error"

