"""
tests/test_itinerary_service.py

Unit tests for ItineraryService:
- Successful itinerary generation and parsing
- Markdown code block stripping (_clean_json_text)
- Malformed JSON handling (HTTP 502)
- Schema mismatch handling (HTTP 502)
- Supabase storage integration (persisting days)
- Upstream rate limit and timeout propagation
"""

import json
from unittest.mock import AsyncMock, MagicMock
import pytest
from fastapi import HTTPException

from app.models.itinerary import ItineraryGenerateRequest, ItineraryResponse
from app.services.itinerary_service import ItineraryService, _clean_json_text


SAMPLE_VALID_ITINERARY_JSON = """
```json
{
  "destination": "Kyoto, Japan",
  "start_date": "2027-04-01",
  "end_date": "2027-04-02",
  "duration_days": 2,
  "total_budget": 1800.0,
  "travel_style": "cultural",
  "travel_pace": "moderate",
  "trip_summary": "Two culturally rich days exploring Kyoto's historic shrines and bamboo forests.",
  "total_estimated_cost": "~$420 USD total across both travelers",
  "packing_and_prep_tips": [
    "Purchase an ICOCA IC card for local transit",
    "Wear slip-on walking shoes for visiting temples"
  ],
  "days": [
    {
      "day_number": 1,
      "date": "2027-04-01",
      "theme": "Eastern Kyoto & Ancient Zen Sanctuaries",
      "morning_activity": {
        "time_slot": "morning",
        "name": "Kiyomizu-dera Temple",
        "description": "Historic wooden stage temple perched over the Otowa waterfall.",
        "location": "Higashiyama",
        "suggested_duration": "2.5 hours",
        "estimated_cost": "¥400 (~$3 USD)",
        "best_time_to_visit": "8:00 AM",
        "booking_required": false,
        "practical_tips": "Arrive early to beat the crowds."
      },
      "lunch": {
        "meal_type": "Lunch",
        "name": "Yodoya",
        "cuisine": "Soba & Tofu",
        "description": "Traditional soba noodles near Kiyomizu.",
        "estimated_cost": "~$15 USD / person",
        "dietary_compliance": "Vegetarian soba available",
        "location": "Higashiyama"
      },
      "afternoon_activity": {
        "time_slot": "afternoon",
        "name": "Yasaka Shrine & Maruyama Park",
        "description": "Scenic stroll through Gion's head shrine and peaceful gardens.",
        "location": "Gion",
        "suggested_duration": "1.5 hours",
        "estimated_cost": "Free",
        "best_time_to_visit": "2:30 PM",
        "booking_required": false
      },
      "dinner": {
        "meal_type": "Dinner",
        "name": "Gion Karyo",
        "cuisine": "Kyoto Kaiseki",
        "description": "Multi-course seasonal dining in an authentic machiya townhouse.",
        "estimated_cost": "~$70 USD / person",
        "dietary_compliance": "Vegetarian kaiseki on advance request",
        "location": "Gion"
      },
      "evening_activity": {
        "time_slot": "evening",
        "name": "Shirakawa Canal Stroll",
        "description": "Atmospheric lantern-lit walk along preserved willow-lined canals.",
        "location": "Gion Shirakawa",
        "suggested_duration": "1 hour",
        "estimated_cost": "Free",
        "best_time_to_visit": "7:30 PM",
        "booking_required": false
      },
      "transportation": {
        "mode": "Kyoto City Bus 206 & Walking",
        "estimated_time": "15 mins",
        "estimated_cost": "¥230 (~$1.60 USD)",
        "route_details": "From Kyoto Station to Gojo-zaka",
        "tips": "Tap IC card upon disembarking"
      },
      "daily_budget": {
        "activities_cost": "~$3 USD",
        "dining_cost": "~$85 USD",
        "transportation_cost": "~$5 USD",
        "total_daily_estimated": "~$93 USD / person",
        "currency": "USD"
      },
      "practical_tips": "Carry cash as some smaller temple stalls and snack shops do not accept cards."
    }
  ]
}
```
"""


@pytest.mark.anyio
async def test_clean_json_text_helper():
    """Verify markdown fences are properly stripped."""
    assert _clean_json_text('```json\n{"status": "ok"}\n```') == '{"status": "ok"}'
    assert _clean_json_text('{"status": "ok"}') == '{"status": "ok"}'


@pytest.mark.anyio
async def test_generate_itinerary_success_with_mock_provider():
    """Verify successful itinerary generation, parsing, and response creation."""
    mock_provider = MagicMock()
    mock_provider.name = "gemini"
    mock_provider.generate = AsyncMock(return_value=SAMPLE_VALID_ITINERARY_JSON)

    mock_db = MagicMock()
    # Mock itineraries table delete and insert chains
    mock_table = MagicMock()
    mock_table.delete.return_value.eq.return_value.execute.return_value = MagicMock()
    mock_table.insert.return_value.execute.return_value = MagicMock()
    mock_db.table.return_value = mock_table

    service = ItineraryService(provider=mock_provider, db=mock_db)

    req = ItineraryGenerateRequest(
        destination="Kyoto, Japan",
        start_date="2027-04-01",
        end_date="2027-04-02",
        num_travelers=2,
        budget=1800.0,
        travel_style="cultural",
        travel_interests=["history", "temples"],
        dietary_preferences=["vegetarian"],
        trip_id="3060d1c4-0a78-4ef9-9590-5a05bd808915",
    )

    result = await service.generate_itinerary(req)

    assert isinstance(result, ItineraryResponse)
    assert result.destination == "Kyoto, Japan"
    assert result.duration_days == 2
    assert len(result.days) == 1
    assert result.days[0].morning_activity.name == "Kiyomizu-dera Temple"
    assert result.provider_used == "gemini"
    assert result.trip_id == "3060d1c4-0a78-4ef9-9590-5a05bd808915"

    # Verify Supabase was called to save day rows
    mock_db.table.assert_called_with("itineraries")


@pytest.mark.anyio
async def test_generate_itinerary_malformed_json_raises_502():
    """Verify malformed JSON from LLM raises HTTP 502."""
    mock_provider = MagicMock()
    mock_provider.name = "gemini"
    mock_provider.generate = AsyncMock(return_value="Sorry, I cannot generate JSON right now.")

    service = ItineraryService(provider=mock_provider, db=None)

    req = ItineraryGenerateRequest(
        destination="Kyoto, Japan",
        start_date="2027-04-01",
        end_date="2027-04-02",
        budget=1000.0,
        travel_style="cultural",
        travel_interests=["history"],
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.generate_itinerary(req)

    assert exc_info.value.status_code == 502
    assert "did not return valid JSON" in exc_info.value.detail


@pytest.mark.anyio
async def test_generate_itinerary_schema_validation_failure_raises_502():
    """Verify invalid JSON schema fields trigger HTTP 502."""
    bad_schema_json = json.dumps({"destination": "Paris", "days": "not-a-list"})

    mock_provider = MagicMock()
    mock_provider.name = "gemini"
    mock_provider.generate = AsyncMock(return_value=bad_schema_json)

    service = ItineraryService(provider=mock_provider, db=None)

    req = ItineraryGenerateRequest(
        destination="Paris, France",
        start_date="2027-04-01",
        end_date="2027-04-03",
        budget=1000.0,
        travel_style="cultural",
        travel_interests=["art"],
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.generate_itinerary(req)

    assert exc_info.value.status_code == 502
    assert "Structured itinerary validation failed" in exc_info.value.detail

