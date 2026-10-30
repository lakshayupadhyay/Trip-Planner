"""
tests/test_itinerary_models.py

Unit tests for structured itinerary Pydantic models:
- Activity, DiningRecommendation, Transportation, DailyBudget
- DayItinerary and ItineraryResponse
- ItineraryGenerateRequest validation
"""

import pytest
from pydantic import ValidationError

from app.models.itinerary import (
    Activity,
    DiningRecommendation,
    Transportation,
    DailyBudget,
    DayItinerary,
    ItineraryResponse,
    ItineraryGenerateRequest,
    PromptPreviewResponse,
)


def test_activity_model_valid():
    """Verify Activity model fields and validation."""
    act = Activity(
        time_slot="morning",
        name="Senso-ji Temple",
        description="Tokyo's oldest and most significant ancient Buddhist temple.",
        location="Asakusa",
        suggested_duration="2 hours",
        estimated_cost="Free",
        best_time_to_visit="8:30 AM",
        booking_required=False,
        practical_tips="Visit early before tour groups arrive.",
    )
    assert act.name == "Senso-ji Temple"
    assert act.booking_required is False
    assert act.time_slot == "morning"


def test_dining_recommendation_model_valid():
    """Verify DiningRecommendation model fields and validation."""
    dining = DiningRecommendation(
        meal_type="Lunch",
        name="Daigo Zen Dining",
        cuisine="Shojin Ryori (Buddhist Vegetarian)",
        description="Serene traditional tatami dining experience.",
        estimated_cost="~$40 USD / person",
        dietary_compliance="100% vegetarian and vegan friendly",
        location="Minato City",
        practical_tips="Book table 1 week in advance.",
    )
    assert dining.meal_type == "Lunch"
    assert dining.name == "Daigo Zen Dining"
    assert "vegetarian" in dining.dietary_compliance.lower()


def test_transportation_and_budget_models_valid():
    """Verify Transportation and DailyBudget models."""
    trans = Transportation(
        mode="Ginza Metro Line",
        estimated_time="15 mins",
        estimated_cost="$1.80 USD",
        route_details="Asakusa to Ueno station",
        tips="Use Suica or Pasmo digital card.",
    )
    assert trans.mode == "Ginza Metro Line"

    budget = DailyBudget(
        activities_cost="$25 USD",
        dining_cost="$60 USD",
        transportation_cost="$5 USD",
        total_daily_estimated="$90 USD",
        currency="USD",
    )
    assert budget.total_daily_estimated == "$90 USD"


def test_day_itinerary_and_itinerary_response_valid():
    """Verify complete DayItinerary and ItineraryResponse parsing."""
    day = DayItinerary(
        day_number=1,
        date="2027-05-10",
        theme="Historic Traditions & Ancient Shrines",
        morning_activity=Activity(
            time_slot="morning",
            name="Meiji Shrine",
            description="Shinto shrine dedicated to Emperor Meiji nestled in dense forest.",
            suggested_duration="2 hours",
            estimated_cost="Free",
        ),
        lunch=DiningRecommendation(
            meal_type="Lunch",
            name="Afuri Ramen",
            cuisine="Yuzu Shio Ramen",
            description="Light citrusy broth with vegan options.",
            estimated_cost="$12 USD",
            dietary_compliance="Vegan broth option available",
        ),
        afternoon_activity=Activity(
            time_slot="afternoon",
            name="Yoyogi Park & Harajuku",
            description="Lively neighborhood exploration and scenic park stroll.",
            suggested_duration="2 hours",
            estimated_cost="Free",
        ),
        dinner=DiningRecommendation(
            meal_type="Dinner",
            name="Gonpachi Nishi-Azabu",
            cuisine="Izakaya",
            description="Atmospheric traditional izakaya.",
            estimated_cost="$35 USD",
        ),
        evening_activity=Activity(
            time_slot="evening",
            name="Shibuya Crossing",
            description="World famous scramble intersection illuminated at night.",
            suggested_duration="1 hour",
            estimated_cost="Free",
        ),
        transportation=Transportation(
            mode="Yamanote Line",
            estimated_time="10 mins",
            estimated_cost="$2.00 USD",
        ),
        daily_budget=DailyBudget(
            activities_cost="Free",
            dining_cost="$47 USD",
            transportation_cost="$4 USD",
            total_daily_estimated="$51 USD",
        ),
        practical_tips="Get an IC transit pass and comfortable walking shoes.",
    )

    resp = ItineraryResponse(
        destination="Tokyo, Japan",
        start_date="2027-05-10",
        end_date="2027-05-12",
        duration_days=3,
        total_budget=2000.0,
        travel_style="cultural",
        travel_pace="moderate",
        days=[day],
        trip_summary="A wonderful 3-day exploration of Tokyo's cultural marvels.",
        total_estimated_cost="~$1,450 USD total",
        packing_and_prep_tips=["Pocket Wi-Fi", "Slip-on shoes for temples"],
        provider_used="gemini",
    )

    assert resp.destination == "Tokyo, Japan"
    assert len(resp.days) == 1
    assert resp.days[0].day_number == 1
    assert resp.provider_used == "gemini"


def test_itinerary_response_empty_days_fails_validation():
    """Verify ItineraryResponse rejects empty days list."""
    with pytest.raises(ValidationError):
        ItineraryResponse(
            destination="Paris, France",
            start_date="2027-06-01",
            end_date="2027-06-05",
            duration_days=5,
            total_budget=1500.0,
            travel_style="cultural",
            travel_pace="moderate",
            days=[],  # Invalid min_length=1
            trip_summary="Summary",
            total_estimated_cost="$1,000",
        )


def test_itinerary_generate_request_validation():
    """Verify ItineraryGenerateRequest inherits TravelPreferences validations."""
    req = ItineraryGenerateRequest(
        destination="Rome, Italy",
        start_date="2027-09-01",
        end_date="2027-09-05",
        num_travelers=2,
        budget=2500.0,
        travel_style="cultural",
        travel_interests=["history", "food"],
        trip_id="123e4567-e89b-12d3-a456-426614174000",
        provider="groq",
    )
    assert req.destination == "Rome, Italy"
    assert req.trip_id == "123e4567-e89b-12d3-a456-426614174000"
    assert req.provider == "groq"

