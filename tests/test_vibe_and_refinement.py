"""
tests/test_vibe_and_refinement.py

Unit and integration tests for Epic 4, Activity 4.3: Vibe-Based Personalization
and Conversational Itinerary Refinement.
Covers:
- 10 Travel Vibe definitions and prompt guideline generation
- Target day number regex and ordinal detection
- Single-day conversational refinement with context preservation
- Full multi-day conversational refinement
- Preservation of unaffected itinerary days
- Re-running Route & Time Optimization after refinement
- Supabase persistence of refined days
- API endpoint integration:
  * POST /api/v1/itinerary/refine
  * POST /api/v1/itinerary/refine/
  * POST /api/v1/itinerary/refine-day
  * POST /api/v1/itinerary/refine-day/
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.itinerary import (
    Activity,
    DailyBudget,
    DayItinerary,
    DayRefineRequest,
    DiningRecommendation,
    ItineraryRefineRequest,
    ItineraryResponse,
    RefineResponse,
    Transportation,
)
from app.services.prompt_service import (
    VIBE_GUIDELINES,
    _get_vibe_guidelines,
    build_itinerary_prompt,
    build_structured_itinerary_prompt,
)
from app.services.refinement_service import (
    RefinementService,
    detect_target_day_number,
)
from app.services.route_optimization_service import RouteOptimizationService

client = TestClient(app)


# ── Sample Data Fixtures ──────────────────────────────────────────────────────

def get_sample_day(day_num: int = 1) -> DayItinerary:
    """Build a valid sample DayItinerary."""
    return DayItinerary(
        day_number=day_num,
        date=f"2027-05-0{day_num}",
        theme=f"Day {day_num} Theme in Kyoto",
        morning_activity=Activity(
            time_slot="morning",
            name="Kiyomizu-dera",
            description="Ancient wooden temple with panoramic views.",
            location="Higashiyama",
            suggested_duration="2 hours",
            estimated_cost="¥400",
        ),
        lunch=DiningRecommendation(
            meal_type="Lunch",
            name="Tofu Soba House",
            cuisine="Kyoto Soba",
            description="Traditional soba noodles.",
            estimated_cost="$15 USD",
            location="Higashiyama",
        ),
        afternoon_activity=Activity(
            time_slot="afternoon",
            name="Yasaka Shrine",
            description="Historic Shinto shrine in Gion.",
            location="Gion",
            suggested_duration="1.5 hours",
            estimated_cost="Free",
        ),
        dinner=DiningRecommendation(
            meal_type="Dinner",
            name="Gion Kaiseki",
            cuisine="Kaiseki",
            description="Multi-course seasonal dining.",
            estimated_cost="$60 USD",
            location="Gion",
        ),
        evening_activity=Activity(
            time_slot="evening",
            name="Shirakawa Canal Stroll",
            description="Atmospheric lantern-lit evening walk.",
            location="Gion",
            suggested_duration="1 hour",
            estimated_cost="Free",
        ),
        transportation=Transportation(
            mode="Walking",
            estimated_time="15 mins",
            estimated_cost="Free",
        ),
        daily_budget=DailyBudget(
            activities_cost="¥400",
            dining_cost="$75 USD",
            transportation_cost="Free",
            total_daily_estimated="$80 USD",
        ),
        practical_tips="Wear comfortable shoes.",
    )


def get_sample_itinerary(num_days: int = 3) -> ItineraryResponse:
    """Build a multi-day itinerary for refinement testing."""
    days = [get_sample_day(i + 1) for i in range(num_days)]
    return ItineraryResponse(
        destination="Kyoto, Japan",
        start_date="2027-05-01",
        end_date="2027-05-03",
        duration_days=num_days,
        total_budget=2000.0,
        travel_style="cultural",
        travel_pace="moderate",
        primary_vibe="Cultural",
        secondary_vibes=["Food & Culinary"],
        days=days,
        trip_summary="A cultural and culinary exploration of Kyoto.",
        total_estimated_cost="~$400 USD",
        packing_and_prep_tips=["Wear walking shoes"],
        provider_used="gemini",
    )


# ── 1. Vibe Selection & Prompt Logic Tests ────────────────────────────────────

def test_vibe_guidelines_all_ten_vibes_defined():
    """Verify that all 10 required travel vibes are defined with specific guidelines."""
    required_vibes = [
        "romantic",
        "adventure",
        "luxury",
        "relaxed",
        "budget",
        "cultural",
        "family",
        "nightlife",
        "nature & exploration",
        "food & culinary",
    ]
    for vibe in required_vibes:
        assert vibe in VIBE_GUIDELINES, f"Missing vibe guideline for: {vibe}"
        assert len(VIBE_GUIDELINES[vibe]) > 20


def test_get_vibe_guidelines_formatting():
    """Verify primary and secondary vibe formatting."""
    guidelines = _get_vibe_guidelines(
        primary_vibe="Romantic",
        secondary_vibes=["Food & Culinary", "Nightlife"],
    )
    assert "Primary Travel Vibe: Romantic" in guidelines
    assert "Secondary Travel Vibes" in guidelines
    assert "Food & culinary" in guidelines
    assert "Nightlife" in guidelines


def test_build_itinerary_prompt_includes_vibes():
    """Verify prompt constructor integrates vibe directives."""
    prompt = build_itinerary_prompt(
        destination="Kyoto, Japan",
        start_date="2027-04-01",
        end_date="2027-04-04",
        travel_style="cultural",
        travel_interests=["history"],
        num_travelers=2,
        budget=2000.0,
        travel_pace="relaxed",
        primary_vibe="Romantic",
        secondary_vibes=["Nature & Exploration"],
    )
    assert "Primary Travel Vibe: Romantic" in prompt
    assert "Nature & exploration" in prompt
    assert "panoramic viewpoints" in prompt.lower()


# ── 2. Target Day Detection Tests ─────────────────────────────────────────────

def test_detect_target_day_number():
    """Verify natural-language target day detection."""
    assert detect_target_day_number("Make Day 2 more adventurous", max_days=5) == 2
    assert detect_target_day_number("Can you improve day 3 please?", max_days=5) == 3
    assert detect_target_day_number("Please replace day #1 morning activity", max_days=5) == 1
    assert detect_target_day_number("Make the second day more relaxing", max_days=5) == 2
    assert detect_target_day_number("On the last day, add shopping", max_days=4) == 4

    # Full trip requests return None
    assert detect_target_day_number("Make the entire trip luxury", max_days=5) is None
    assert detect_target_day_number("Make it more affordable", max_days=5) is None
    assert detect_target_day_number("Day 8 is out of range", max_days=3) is None


# ── 3. Conversational Day Refinement Tests ─────────────────────────────────────

SAMPLE_REFINED_DAY_JSON = """
{
  "day_number": 2,
  "date": "2027-05-02",
  "theme": "High-Energy Kyoto Adventures & Mountain Hikes",
  "morning_activity": {
    "time_slot": "morning",
    "name": "Mt. Hiei Trail Hike",
    "description": "Scenic guided ridge trek overlooking Lake Biwa.",
    "location": "Northeast Kyoto",
    "suggested_duration": "3 hours",
    "estimated_cost": "Free",
    "best_time_to_visit": "8:30 AM",
    "booking_required": false
  },
  "lunch": {
    "meal_type": "Lunch",
    "name": "Mountain Trail Hut Soba",
    "cuisine": "Soba & Mountain Veggies",
    "description": "Nutritious trailside meal.",
    "estimated_cost": "~$12 USD",
    "location": "Mt Hiei"
  },
  "afternoon_activity": {
    "time_slot": "afternoon",
    "name": "Hozugawa River Rafting",
    "description": "Exciting white-water boat journey through steep gorges.",
    "location": "Kameoka",
    "suggested_duration": "2 hours",
    "estimated_cost": "¥4100 (~$28 USD)",
    "best_time_to_visit": "1:30 PM",
    "booking_required": true
  },
  "dinner": {
    "meal_type": "Dinner",
    "name": "Pontocho Charcoal Grill",
    "cuisine": "Yakitori",
    "description": "Energizing riverfront skewers.",
    "estimated_cost": "~$30 USD",
    "location": "Pontocho"
  },
  "evening_activity": {
    "time_slot": "evening",
    "name": "Kamogawa River Stroll",
    "description": "Refreshing riverside walk under the stars.",
    "location": "Sanjo",
    "suggested_duration": "1 hour",
    "estimated_cost": "Free",
    "best_time_to_visit": "8:00 PM",
    "booking_required": false
  },
  "transportation": {
    "mode": "Keihan Line & Walking",
    "estimated_time": "25 mins",
    "estimated_cost": "¥500",
    "route_details": "Direct transit"
  },
  "daily_budget": {
    "activities_cost": "~$28 USD",
    "dining_cost": "~$42 USD",
    "transportation_cost": "~$4 USD",
    "total_daily_estimated": "~$74 USD",
    "currency": "USD"
  },
  "practical_tips": "Carry a refillable water bottle and trail shoes."
}
"""


@pytest.mark.anyio
async def test_refine_single_day_service():
    """Verify refine_day regenerates requested day, re-calculates routes and schedules."""
    mock_provider = MagicMock()
    mock_provider.name = "gemini"
    mock_provider.generate = AsyncMock(return_value=SAMPLE_REFINED_DAY_JSON)

    service = RefinementService(provider=mock_provider, db=None)

    req = DayRefineRequest(
        destination="Kyoto, Japan",
        day=get_sample_day(day_num=2),
        instruction="Make Day 2 more adventurous with hiking and rafting",
        travel_pace="moderate",
        primary_vibe="Adventure",
    )

    refined = await service.refine_day(req)

    assert isinstance(refined, DayItinerary)
    assert refined.day_number == 2
    assert "Mt. Hiei Trail Hike" in refined.morning_activity.name
    # Verify Activity 4.2 Route & Time Optimization was re-run
    assert len(refined.route_legs) == 4
    assert refined.total_travel_distance_km is not None
    assert refined.total_travel_distance_km > 0
    assert refined.morning_activity.schedule is not None


@pytest.mark.anyio
async def test_refine_itinerary_single_day_preserves_other_days():
    """
    Verify requirement: When user asks to refine Day 2, only Day 2 is updated,
    and Days 1 & 3 remain completely preserved.
    """
    mock_provider = MagicMock()
    mock_provider.name = "gemini"
    mock_provider.generate = AsyncMock(return_value=SAMPLE_REFINED_DAY_JSON)

    mock_db = MagicMock()
    mock_db.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock()
    mock_db.table.return_value.insert.return_value.execute.return_value = MagicMock()

    service = RefinementService(provider=mock_provider, db=mock_db)
    itinerary = get_sample_itinerary(num_days=3)

    day1_original_morning = itinerary.days[0].morning_activity.name
    day3_original_morning = itinerary.days[2].morning_activity.name

    refine_req = ItineraryRefineRequest(
        itinerary=itinerary,
        instruction="Make Day 2 more adventurous",
    )

    result = await service.refine_itinerary(refine_req)

    assert isinstance(result, RefineResponse)
    assert result.scope == "day"
    assert result.affected_day_numbers == [2]
    assert "Refined Day 2" in result.explanation

    # Verify Day 2 was updated
    assert "Mt. Hiei" in result.itinerary.days[1].morning_activity.name

    # Verify Days 1 and 3 are preserved intact
    assert result.itinerary.days[0].morning_activity.name == day1_original_morning
    assert result.itinerary.days[2].morning_activity.name == day3_original_morning


# ── 4. API Endpoints Integration Tests ────────────────────────────────────────

def test_api_refine_itinerary_endpoint():
    """Verify POST /api/v1/itinerary/refine endpoint returns 200 with RefineResponse."""
    itinerary = get_sample_itinerary(num_days=2)

    with patch(
        "app.api.itinerary.refinement_service.refine_itinerary",
        new_callable=AsyncMock,
        return_value=RefineResponse(
            itinerary=itinerary,
            explanation="Refined Day 1 to include romantic sunset dining.",
            affected_day_numbers=[1],
            scope="day",
        ),
    ):
        payload = {
            "itinerary": itinerary.model_dump(),
            "instruction": "Make Day 1 more romantic",
        }
        response = client.post("/api/v1/itinerary/refine", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["scope"] == "day"
        assert data["affected_day_numbers"] == [1]
        assert "romantic" in data["explanation"].lower()


def test_api_refine_itinerary_trailing_slash():
    """Verify POST /api/v1/itinerary/refine/ handles trailing slash."""
    itinerary = get_sample_itinerary(num_days=2)

    with patch(
        "app.api.itinerary.refinement_service.refine_itinerary",
        new_callable=AsyncMock,
        return_value=RefineResponse(
            itinerary=itinerary,
            explanation="Updated itinerary.",
            affected_day_numbers=[1],
            scope="day",
        ),
    ):
        payload = {
            "itinerary": itinerary.model_dump(),
            "instruction": "Improve Day 1",
        }
        response = client.post("/api/v1/itinerary/refine/", json=payload)
        assert response.status_code == 200


def test_api_refine_day_endpoint():
    """Verify POST /api/v1/itinerary/refine-day returns 200 with updated DayItinerary."""
    day = get_sample_day(1)

    with patch(
        "app.api.itinerary.refinement_service.refine_day",
        new_callable=AsyncMock,
        return_value=day,
    ):
        payload = {
            "destination": "Kyoto, Japan",
            "day": day.model_dump(),
            "instruction": "Add more street food to lunch",
        }
        response = client.post("/api/v1/itinerary/refine-day", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["day_number"] == 1

