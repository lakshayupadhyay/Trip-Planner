"""
tests/test_trip_management.py

Comprehensive test suite for Epic 5 – Activity 5.1: Trip Save & Management:
- GET /api/v1/trips/ (List all saved trips, with has_itinerary and vibe metadata)
- GET /api/v1/trips/{trip_id} (Retrieve single trip by ID)
- GET /api/v1/trips/{trip_id} (404 when missing)
- PUT /api/v1/trips/{trip_id} (Update destination, dates, budget, vibes, preferences)
- PUT /api/v1/trips/{trip_id} (422 validation on invalid dates or budget)
- Itinerary regeneration recommendation flag on major trip changes
- DELETE /api/v1/trips/{trip_id} (Delete trip and associated itineraries)
- DELETE /api/v1/trips/{trip_id} (404 when missing)
- GET /api/v1/trips/{trip_id}/itinerary (Retrieve saved itinerary without AI generation)
- GET /api/v1/itinerary/{trip_id} (Alias endpoint for saved itinerary)
"""

from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.trips import trip_service, itinerary_service
from app.models.itinerary import (
    Activity,
    ActivitySchedule,
    DailyBudget,
    DayItinerary,
    DiningRecommendation,
    ItineraryResponse,
    RouteLeg,
    Transportation,
)

client = TestClient(app)


def get_mock_day(day_num: int = 1) -> DayItinerary:
    return DayItinerary(
        day_number=day_num,
        date=f"2027-06-0{day_num}",
        theme="Ancient Kyoto & Shinto Shrines",
        morning_activity=Activity(
            time_slot="morning",
            name="Fushimi Inari Shrine",
            description="Thousand vermilion torii gates winding through holy mountain paths.",
            location="Fushimi",
            suggested_duration="2.5 hours",
            estimated_cost="Free",
            best_time_to_visit="8:00 AM",
            booking_required=False,
            schedule=ActivitySchedule(
                start_time="8:00 AM",
                end_time="10:30 AM",
                duration_minutes=150,
            ),
        ),
        lunch=DiningRecommendation(
            meal_type="Lunch",
            name="Inari Soba Tei",
            cuisine="Japanese Soba",
            description="Traditional freshly hand-rolled buckwheat noodles.",
            estimated_cost="~$15 USD / person",
            location="Fushimi",
        ),
        afternoon_activity=Activity(
            time_slot="afternoon",
            name="Kiyomizu-dera Temple",
            description="Magnificent wooden stage overlooking the Kyoto valley.",
            location="Higashiyama",
            suggested_duration="2 hours",
            estimated_cost="¥400 (~$3 USD)",
            schedule=ActivitySchedule(
                start_time="1:30 PM",
                end_time="3:30 PM",
                duration_minutes=120,
            ),
        ),
        dinner=DiningRecommendation(
            meal_type="Dinner",
            name="Gion Kaiseki",
            cuisine="Kyoto Seasonal Kaiseki",
            description="Multi-course seasonal dining in an authentic machiya townhouse.",
            estimated_cost="~$60 USD / person",
            location="Gion",
        ),
        evening_activity=Activity(
            time_slot="evening",
            name="Gion Lantern Walk",
            description="Atmospheric lantern-lit walk through historical geisha preservation district.",
            location="Gion",
            suggested_duration="1 hour",
            estimated_cost="Free",
        ),
        transportation=Transportation(
            mode="Keihan Line & Walking",
            estimated_time="20 mins",
            estimated_cost="~$3 USD",
            route_details="Fushimi-Inari Station to Kiyomizu-Gojo",
        ),
        daily_budget=DailyBudget(
            activities_cost="~$3 USD",
            dining_cost="~$75 USD",
            transportation_cost="~$3 USD",
            total_daily_estimated="~$81 USD",
        ),
        practical_tips="Arrive early at Fushimi Inari to avoid peak crowds.",
        route_legs=[
            RouteLeg(
                from_name="Fushimi Inari Shrine",
                to_name="Inari Soba Tei",
                distance_km=0.6,
                duration_minutes=8,
                recommended_mode="walking",
                distance_display="~0.6 km",
                duration_display="8 mins",
            )
        ],
        total_travel_distance_km=0.6,
        total_travel_time_minutes=8,
    )


# ── 1. List All Trips Endpoint ────────────────────────────────────────────────

def test_list_all_trips_endpoint(monkeypatch):
    """Verify GET /api/v1/trips/ returns all trips with itinerary availability."""
    mock_trips = [
        {
            "id": "trip-uuid-1",
            "user_id": "user-uuid-100",
            "destination": "Kyoto, Japan",
            "start_date": "2027-06-01",
            "end_date": "2027-06-05",
            "num_travelers": 2,
            "budget": 3500.0,
            "travel_style": "cultural",
            "travel_interests": ["history", "food"],
            "dietary_preferences": ["vegetarian"],
            "travel_pace": "moderate",
            "primary_vibe": "Cultural",
            "secondary_vibes": ["Food & Culinary"],
            "additional_requirements": None,
            "status": "pending",
            "has_itinerary": True,
            "itinerary_regeneration_recommended": False,
            "created_at": "2026-10-30T10:00:00Z",
        },
        {
            "id": "trip-uuid-2",
            "user_id": "user-uuid-100",
            "destination": "Paris, France",
            "start_date": "2027-07-10",
            "end_date": "2027-07-16",
            "num_travelers": 1,
            "budget": 2200.0,
            "travel_style": "relaxation",
            "travel_interests": ["art", "cafes"],
            "dietary_preferences": [],
            "travel_pace": "slow",
            "primary_vibe": "Romantic",
            "secondary_vibes": ["Food & Culinary"],
            "additional_requirements": None,
            "status": "pending",
            "has_itinerary": False,
            "itinerary_regeneration_recommended": False,
            "created_at": "2026-10-30T11:00:00Z",
        },
    ]

    monkeypatch.setattr(trip_service, "get_all_trips", MagicMock(return_value=mock_trips))

    response = client.get("/api/v1/trips/")
    assert response.status_code == 200
    trips = response.json()
    assert len(trips) == 2
    assert trips[0]["id"] == "trip-uuid-1"
    assert trips[0]["has_itinerary"] is True
    assert trips[0]["primary_vibe"] == "Cultural"
    assert trips[1]["has_itinerary"] is False


# ── 2. Get Single Trip Endpoint ───────────────────────────────────────────────

def test_get_single_trip_by_id(monkeypatch):
    """Verify GET /api/v1/trips/{trip_id} returns trip details."""
    mock_trip = {
        "id": "88888888-4444-4444-4444-123456789abc",
        "user_id": "user-uuid-100",
        "destination": "Rome, Italy",
        "start_date": "2027-05-15",
        "end_date": "2027-05-22",
        "num_travelers": 2,
        "budget": 4000.0,
        "travel_style": "cultural",
        "travel_interests": ["history", "architecture"],
        "dietary_preferences": [],
        "travel_pace": "moderate",
        "primary_vibe": "Cultural",
        "secondary_vibes": ["Food & Culinary"],
        "additional_requirements": None,
        "status": "pending",
        "has_itinerary": True,
        "itinerary_regeneration_recommended": False,
        "created_at": "2026-10-30T09:00:00Z",
    }

    monkeypatch.setattr(trip_service, "get_trip_by_id", MagicMock(return_value=mock_trip))

    response = client.get("/api/v1/trips/88888888-4444-4444-4444-123456789abc")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "88888888-4444-4444-4444-123456789abc"
    assert data["destination"] == "Rome, Italy"
    assert data["has_itinerary"] is True


def test_get_trip_404_when_not_found(monkeypatch):
    """Verify GET /api/v1/trips/{trip_id} returns 404 when trip is missing."""
    from fastapi import HTTPException
    monkeypatch.setattr(trip_service, "get_trip_by_id", MagicMock(side_effect=HTTPException(status_code=404, detail="Trip not found.")))
    monkeypatch.setattr(trip_service, "get_trips_by_user", MagicMock(return_value=[]))

    response = client.get("/api/v1/trips/99999999-0000-0000-0000-000000000000")
    assert response.status_code == 404


# ── 3. Update Trip Endpoint ───────────────────────────────────────────────────

def test_update_trip_success(monkeypatch):
    """Verify PUT /api/v1/trips/{trip_id} updates trip and returns refreshed model."""
    mock_updated = {
        "id": "trip-uuid-1",
        "user_id": "user-uuid-100",
        "destination": "Kyoto, Japan",
        "start_date": "2027-06-01",
        "end_date": "2027-06-08",  # Extended dates
        "num_travelers": 3,
        "budget": 4500.0,
        "travel_style": "adventure",
        "travel_interests": ["hiking", "temples"],
        "dietary_preferences": ["vegan"],
        "travel_pace": "fast",
        "primary_vibe": "Adventure",
        "secondary_vibes": ["Nature & Exploration"],
        "additional_requirements": "Bring trekking poles",
        "status": "pending",
        "has_itinerary": True,
        "itinerary_regeneration_recommended": True,
        "created_at": "2026-10-30T10:00:00Z",
    }

    monkeypatch.setattr(trip_service, "update_trip", MagicMock(return_value=mock_updated))

    payload = {
        "end_date": "2027-06-08",
        "num_travelers": 3,
        "budget": 4500.0,
        "travel_style": "adventure",
        "primary_vibe": "Adventure",
        "secondary_vibes": ["Nature & Exploration"],
    }

    response = client.put("/api/v1/trips/trip-uuid-1", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["num_travelers"] == 3
    assert data["budget"] == 4500.0
    assert data["primary_vibe"] == "Adventure"
    assert data["itinerary_regeneration_recommended"] is True


def test_update_trip_invalid_dates_422():
    """Verify PUT /api/v1/trips/{trip_id} rejects invalid end_date <= start_date."""
    payload = {
        "start_date": "2027-08-10",
        "end_date": "2027-08-05",  # Invalid
    }
    response = client.put("/api/v1/trips/trip-uuid-1", json=payload)
    assert response.status_code == 422


# ── 4. Delete Trip Endpoint ───────────────────────────────────────────────────

def test_delete_trip_success(monkeypatch):
    """Verify DELETE /api/v1/trips/{trip_id} deletes trip and returns confirmation."""
    mock_result = {
        "success": True,
        "message": "Trip 'trip-uuid-1' and all associated itineraries were successfully deleted.",
        "deleted_trip_id": "trip-uuid-1",
    }

    monkeypatch.setattr(trip_service, "delete_trip", MagicMock(return_value=mock_result))

    response = client.delete("/api/v1/trips/trip-uuid-1")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["deleted_trip_id"] == "trip-uuid-1"


def test_delete_trip_404_when_not_found(monkeypatch):
    """Verify DELETE /api/v1/trips/{trip_id} raises 404 when trip is absent."""
    from fastapi import HTTPException
    monkeypatch.setattr(trip_service, "delete_trip", MagicMock(side_effect=HTTPException(status_code=404, detail="Trip not found.")))

    response = client.delete("/api/v1/trips/missing-trip-id")
    assert response.status_code == 404


# ── 5. Retrieve Saved Itinerary Endpoint ──────────────────────────────────────

def test_get_saved_itinerary_endpoint(monkeypatch):
    """Verify GET /api/v1/trips/{trip_id}/itinerary and /api/v1/itinerary/{trip_id} return saved itinerary without AI calls."""
    mock_itinerary = ItineraryResponse(
        trip_id="trip-uuid-1",
        destination="Kyoto, Japan",
        start_date="2027-06-01",
        end_date="2027-06-02",
        duration_days=1,
        total_budget=2000.0,
        travel_style="cultural",
        travel_pace="moderate",
        primary_vibe="Cultural",
        secondary_vibes=["Food & Culinary"],
        days=[get_mock_day(1)],
        trip_summary="Saved cultural journey through Kyoto's historic shrines.",
        total_estimated_cost="~$160 USD",
        packing_and_prep_tips=["Wear walking shoes"],
        provider_used="gemini",
        route_optimized=True,
    )

    from app.services.itinerary_service import ItineraryService
    monkeypatch.setattr(ItineraryService, "get_itinerary_by_trip_id", MagicMock(return_value=mock_itinerary))

    # Test via /api/v1/trips/{trip_id}/itinerary
    resp1 = client.get("/api/v1/trips/trip-uuid-1/itinerary")
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["destination"] == "Kyoto, Japan"
    assert len(data1["days"]) == 1
    assert data1["days"][0]["morning_activity"]["name"] == "Fushimi Inari Shrine"
    assert data1["route_optimized"] is True

    # Test via /api/v1/itinerary/{trip_id}
    resp2 = client.get("/api/v1/itinerary/trip-uuid-1")
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["destination"] == "Kyoto, Japan"
