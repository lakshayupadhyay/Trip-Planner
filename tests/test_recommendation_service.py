"""
tests/test_recommendation_service.py

Unit tests for RecommendationService using mocked Google Gemini client responses:
- Destination recommendation generation and parsing
- Activity and dining recommendation generation and parsing
- Markdown code block stripping (_clean_json_text)
- Missing API key error handling (500)
- Malformed JSON handling (502)
- Rate limit error handling (429)
- Timeout error handling (504)
"""

from unittest.mock import MagicMock
import pytest
from fastapi import HTTPException

from app.models.recommendations import (
    ActivityRecommendationRequest,
    DestinationRecommendationRequest,
    ActivitiesRecommendationResponse,
    DestinationsRecommendationResponse,
)
from app.services.recommendation_service import RecommendationService, _clean_json_text


# ── Fixtures & Mock Helpers ───────────────────────────────────────────────────

def create_mock_client(return_text: str):
    """Create a mock genai.Client whose models.generate_content returns the given text."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = return_text
    mock_client.models.generate_content.return_value = mock_response
    return mock_client


MOCK_ACTIVITIES_JSON = """
```json
{
  "destination": "Kyoto, Japan",
  "recommendations": [
    {
      "name": "Fushimi Inari-taisha",
      "category": "Attractions",
      "description": "Iconic shrine known for thousands of vermilion torii gates.",
      "reason_for_recommendation": "Perfect for cultural exploration and peaceful hiking.",
      "estimated_cost": "Free",
      "suggested_duration": "2-3 hours",
      "best_time_to_visit": "Early morning (7:00 AM) to avoid crowds",
      "location": "Fushimi Ward",
      "practical_tips": "Wear comfortable walking shoes for the summit hike."
    },
    {
      "name": "Shigetsu (Tenryu-ji)",
      "category": "Dining",
      "description": "Michelin Bib Gourmand Zen temple dining serving traditional Shojin Ryori.",
      "reason_for_recommendation": "Fully honors strict vegetarian and vegan preferences.",
      "estimated_cost": "~$35 USD / person",
      "suggested_duration": "1.5 hours",
      "best_time_to_visit": "Lunch (11:30 AM)",
      "location": "Arashiyama",
      "practical_tips": "Reservations required at least 3 days in advance."
    }
  ],
  "notes": "Kyoto rewards early morning visits and respectful temple etiquette."
}
```
"""

MOCK_DESTINATIONS_JSON = """
{
  "recommendations": [
    {
      "destination": "Florence, Italy",
      "country": "Italy",
      "description": "Cradle of the Renaissance boasting world-class art and Tuscan cuisine.",
      "why_it_matches": "Fits your cultural travel style and love for historic architecture.",
      "estimated_budget_range": "$1,500 - $2,200 USD per person",
      "best_time_to_visit": "May or September",
      "highlight_attractions": ["Uffizi Gallery", "Duomo di Firenze", "Ponte Vecchio"],
      "practical_tips": "Purchase museum tickets in advance to skip hours-long queues."
    }
  ],
  "notes": "Compact and walkable city ideal for moderate pace travelers."
}
"""


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_clean_json_text():
    """Verify markdown code blocks are cleanly stripped."""
    assert _clean_json_text('```json\n{"a": 1}\n```') == '{"a": 1}'
    assert _clean_json_text('```\n{"b": 2}\n```') == '{"b": 2}'
    assert _clean_json_text('{"c": 3}') == '{"c": 3}'


def test_get_activity_recommendations_success():
    """Verify activity recommendations parse correctly from mocked Gemini response."""
    mock_client = create_mock_client(MOCK_ACTIVITIES_JSON)
    service = RecommendationService(client=mock_client)

    req = ActivityRecommendationRequest(
        destination="Kyoto, Japan",
        budget=3000.0,
        travel_style="cultural",
        travel_interests=["history", "nature"],
        dietary_preferences=["vegetarian"],
        travel_pace="moderate",
    )

    response = service.get_activity_recommendations(req)

    assert isinstance(response, ActivitiesRecommendationResponse)
    assert response.destination == "Kyoto, Japan"
    assert len(response.recommendations) == 2
    assert response.recommendations[0].name == "Fushimi Inari-taisha"
    assert response.recommendations[0].category == "Attractions"
    assert response.recommendations[1].name == "Shigetsu (Tenryu-ji)"
    assert response.recommendations[1].category == "Dining"
    assert "vegetarian" in response.recommendations[1].reason_for_recommendation


def test_get_destination_recommendations_success():
    """Verify destination suggestions parse correctly from mocked Gemini response."""
    mock_client = create_mock_client(MOCK_DESTINATIONS_JSON)
    service = RecommendationService(client=mock_client)

    req = DestinationRecommendationRequest(
        preferred_region="Southern Europe",
        budget=2000.0,
        travel_style="cultural",
        travel_interests=["history", "food", "art"],
        travel_pace="moderate",
    )

    response = service.get_destination_recommendations(req)

    assert isinstance(response, DestinationsRecommendationResponse)
    assert len(response.recommendations) == 1
    assert response.recommendations[0].destination == "Florence, Italy"
    assert response.recommendations[0].country == "Italy"
    assert "Uffizi Gallery" in response.recommendations[0].highlight_attractions


def test_missing_api_key_raises_http_500():
    """Verify accessing client without API key raises HTTP 500."""
    service = RecommendationService(api_key=None, client=None)
    service._api_key = None  # ensure none

    with pytest.raises(HTTPException) as exc_info:
        _ = service.client
    assert exc_info.value.status_code == 500
    assert "Gemini API key is not configured" in exc_info.value.detail


def test_malformed_json_raises_http_502():
    """Verify malformed JSON from Gemini raises HTTP 502."""
    mock_client = create_mock_client("This is not JSON at all!")
    service = RecommendationService(client=mock_client)

    req = ActivityRecommendationRequest(destination="Rome, Italy")
    with pytest.raises(HTTPException) as exc_info:
        service.get_activity_recommendations(req)

    assert exc_info.value.status_code == 502
    assert "Failed to parse AI response into structured JSON" in exc_info.value.detail


def test_rate_limit_raises_http_429():
    """Verify RESOURCE_EXHAUSTED raises HTTP 429."""
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception("429 RESOURCE_EXHAUSTED: quota exceeded")
    service = RecommendationService(client=mock_client)

    req = ActivityRecommendationRequest(destination="Tokyo, Japan")
    with pytest.raises(HTTPException) as exc_info:
        service.get_activity_recommendations(req)

    assert exc_info.value.status_code == 429
    assert "rate limit exceeded" in exc_info.value.detail.lower()


def test_timeout_raises_http_504():
    """Verify DEADLINE_EXCEEDED raises HTTP 504."""
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception("DEADLINE_EXCEEDED: timeout waiting for response")
    service = RecommendationService(client=mock_client)

    req = DestinationRecommendationRequest(preferred_region="Europe")
    with pytest.raises(HTTPException) as exc_info:
        service.get_destination_recommendations(req)

    assert exc_info.value.status_code == 504
    assert "timed out" in exc_info.value.detail.lower()

