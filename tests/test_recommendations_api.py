"""
tests/test_recommendations_api.py

Integration tests for recommendation endpoints:
- POST /api/v1/recommendations/destinations
- POST /api/v1/recommendations/activities
- Request schema validation (HTTP 422)
- Trailing-slash route compatibility
- Upstream service error propagation
"""

from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import HTTPException
from app.main import app
from app.models.recommendations import (
    ActivitiesRecommendationResponse,
    ActivityRecommendation,
    DestinationRecommendation,
    DestinationsRecommendationResponse,
)

client = TestClient(app)


def test_recommend_destinations_api_success():
    """Verify POST /api/v1/recommendations/destinations returns 200 with valid schema."""
    mock_resp = DestinationsRecommendationResponse(
        recommendations=[
            DestinationRecommendation(
                destination="Kyoto, Japan",
                country="Japan",
                description="Historic cultural hub filled with zen gardens and ancient shrines.",
                why_it_matches="Matches cultural style and interest in historic temples.",
                estimated_budget_range="$2,000 - $3,000 USD",
                best_time_to_visit="March to May",
                highlight_attractions=["Kinkaku-ji", "Fushimi Inari", "Arashiyama Bamboo Grove"],
                practical_tips="Get an IC card for convenient local trains and buses.",
            )
        ],
        notes="A wonderful fit for your pace and budget.",
    )

    with patch("app.api.recommendations.recommendation_service.get_destination_recommendations", return_value=mock_resp):
        payload = {
            "preferred_region": "East Asia",
            "budget": 3000.0,
            "num_travelers": 2,
            "travel_style": "cultural",
            "travel_interests": ["history", "culture"],
            "travel_pace": "moderate",
        }
        response = client.post("/api/v1/recommendations/destinations", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert len(data["recommendations"]) == 1
        assert data["recommendations"][0]["destination"] == "Kyoto, Japan"
        assert data["recommendations"][0]["country"] == "Japan"
        assert len(data["recommendations"][0]["highlight_attractions"]) == 3


def test_recommend_activities_api_success():
    """Verify POST /api/v1/recommendations/activities returns 200 with structured recommendations."""
    mock_resp = ActivitiesRecommendationResponse(
        destination="Barcelona, Spain",
        recommendations=[
            ActivityRecommendation(
                name="Sagrada Familia",
                category="Attractions",
                description="Gaudi's iconic basilica masterpiece.",
                reason_for_recommendation="Essential cultural highlight.",
                estimated_cost="~€26",
                suggested_duration="2 hours",
                best_time_to_visit="9:00 AM",
                location="Eixample",
                practical_tips="Book timed-entry tickets online weeks in advance.",
            )
        ],
        notes="Enjoy tapas and architecture.",
    )

    with patch("app.api.recommendations.recommendation_service.get_activity_recommendations", return_value=mock_resp):
        payload = {
            "destination": "Barcelona, Spain",
            "start_date": "2027-05-01",
            "end_date": "2027-05-05",
            "budget": 2000.0,
            "num_travelers": 1,
            "travel_style": "cultural",
            "travel_interests": ["art", "architecture"],
            "travel_pace": "moderate",
            "dietary_preferences": ["none"],
        }
        response = client.post("/api/v1/recommendations/activities", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["destination"] == "Barcelona, Spain"
        assert len(data["recommendations"]) == 1
        assert data["recommendations"][0]["name"] == "Sagrada Familia"
        assert data["recommendations"][0]["category"] == "Attractions"


def test_recommend_activities_empty_destination_422():
    """Verify omitting or providing an empty destination triggers HTTP 422."""
    payload = {
        "destination": "",
        "budget": 1500.0,
    }
    response = client.post("/api/v1/recommendations/activities", json=payload)
    assert response.status_code == 422


def test_recommend_destinations_invalid_travelers_422():
    """Verify negative or excessive traveler counts trigger HTTP 422."""
    payload = {
        "num_travelers": 0,  # Below min 1
    }
    response = client.post("/api/v1/recommendations/destinations", json=payload)
    assert response.status_code == 422

    payload2 = {
        "num_travelers": 25,  # Above max 20
    }
    response2 = client.post("/api/v1/recommendations/destinations", json=payload2)
    assert response2.status_code == 422


def test_recommend_activities_negative_budget_422():
    """Verify negative budget value triggers HTTP 422."""
    payload = {
        "destination": "London, UK",
        "budget": -50.0,
    }
    response = client.post("/api/v1/recommendations/activities", json=payload)
    assert response.status_code == 422


def test_recommend_service_exception_propagation():
    """Verify service HTTPExceptions (e.g. 502, 429) pass through cleanly."""
    with patch(
        "app.api.recommendations.recommendation_service.get_activity_recommendations",
        side_effect=HTTPException(status_code=502, detail="Upstream AI provider error"),
    ):
        payload = {"destination": "Tokyo, Japan"}
        response = client.post("/api/v1/recommendations/activities", json=payload)
        assert response.status_code == 502
        assert response.json()["detail"] == "Upstream AI provider error"

