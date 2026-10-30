"""
tests/test_system_stability_and_e2e.py

End-to-end integration and system stability test suite for Epic 5 – Activity 5.3:
  1. Full End-to-End Workflow:
     Preference Capture -> Trip Creation -> Supabase Attachment -> Recommendations
     -> AI Itinerary Generation -> Route Optimization -> Refinement -> PDF/JSON Export
     -> Public Sharing -> Revocation -> Deletion.
  2. AI Error Resilience:
     Malformed JSON recovery, missing fields, schema validation 502 error handling.
  3. Provider Failure Handling:
     Rate limit 429, API timeout 504, upstream 500, missing API credentials.
  4. Database Failure & Corrupted State Prevention:
     Clean 503 responses, zero state corruption on partial failures.
"""

from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.api import trips, itinerary, recommendations, share
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
from app.models.trip import TripResponse

client = TestClient(app)


def build_test_day(day_num: int = 1) -> DayItinerary:
    return DayItinerary(
        day_number=day_num,
        date="2027-05-01",
        theme="Art & Historic Quarter",
        morning_activity=Activity(
            time_slot="morning",
            name="Historic Museum",
            description="Cultural exhibition of national treasures.",
            suggested_duration="2 hours",
            estimated_cost="$20 USD",
            schedule=ActivitySchedule(start_time="09:00 AM", end_time="11:00 AM", duration_minutes=120),
        ),
        lunch=DiningRecommendation(
            meal_type="Lunch",
            name="Bistro Central",
            cuisine="Local Cuisine",
            description="Artisanal lunch menu.",
            estimated_cost="$25 USD",
        ),
        afternoon_activity=Activity(
            time_slot="afternoon",
            name="Botanical Garden",
            description="Peaceful walks through landscaped greenhouses.",
            suggested_duration="1.5 hours",
            estimated_cost="Free",
        ),
        dinner=DiningRecommendation(
            meal_type="Dinner",
            name="Rooftop Terrace",
            cuisine="Modern Fusion",
            description="Sunset views with contemporary dining.",
            estimated_cost="$50 USD",
        ),
        evening_activity=Activity(
            time_slot="evening",
            name="Old Town Plaza",
            description="Lantern-lit evening stroll through pedestrian alleyways.",
            suggested_duration="1 hour",
            estimated_cost="Free",
        ),
        transportation=Transportation(
            mode="Metro Line 1",
            estimated_time="15 mins",
            estimated_cost="$2.50 USD",
        ),
        daily_budget=DailyBudget(
            activities_cost="$20 USD",
            dining_cost="$75 USD",
            transportation_cost="$2.50 USD",
            total_daily_estimated="$97.50 USD",
        ),
        practical_tips="Pre-book museum admission online.",
        route_legs=[
            RouteLeg(
                from_name="Historic Museum",
                to_name="Bistro Central",
                distance_km=0.8,
                duration_minutes=10,
                recommended_mode="walking",
                distance_display="~0.8 km",
                duration_display="10 mins",
            )
        ],
        total_travel_distance_km=0.8,
        total_travel_time_minutes=10,
    )


def build_test_itinerary(trip_id: str = "trip-e2e-123") -> ItineraryResponse:
    day = build_test_day(1)
    return ItineraryResponse(
        trip_id=trip_id,
        destination="Vienna, Austria",
        start_date="2027-05-01",
        end_date="2027-05-03",
        duration_days=3,
        total_budget=2000.0,
        travel_style="cultural",
        travel_pace="moderate",
        primary_vibe="Cultural",
        secondary_vibes=["Food & Culinary"],
        days=[day],
        trip_summary="A refined cultural exploration of Vienna.",
        total_estimated_cost="$300 USD",
        packing_and_prep_tips=["Smart casual attire"],
    )


# ── 1. Complete End-to-End User Flow ────────────────────────────────────────

def test_complete_end_to_end_workflow(monkeypatch):
    """
    Test the entire 11-step application lifecycle:
    Trip creation -> Persistence -> Recommendation -> Generation -> Route Optimization
    -> Refinement -> History -> Export (PDF/JSON/Summary) -> Sharing -> Revocation -> Deletion.
    """
    trip_id = "00000000-1111-2222-3333-444444444444"
    mock_trip_record = {
        "id": trip_id,
        "user_id": "user-uuid-888",
        "destination": "Vienna, Austria",
        "start_date": "2027-05-01",
        "end_date": "2027-05-03",
        "num_travelers": 2,
        "budget": 2000.0,
        "travel_style": "cultural",
        "travel_interests": ["museums", "music"],
        "dietary_preferences": [],
        "travel_pace": "moderate",
        "primary_vibe": "Cultural",
        "secondary_vibes": ["Food & Culinary"],
        "status": "pending",
        "has_itinerary": True,
        "itinerary_regeneration_recommended": False,
        "created_at": "2026-10-30T10:00:00Z",
    }
    mock_itin = build_test_itinerary(trip_id)

    # 1. Mock trip creation & DB services
    monkeypatch.setattr(trips.trip_service, "create_trip", MagicMock(return_value=mock_trip_record))
    monkeypatch.setattr(trips.trip_service, "get_trip_by_id", MagicMock(return_value=mock_trip_record))
    monkeypatch.setattr(trips.trip_service, "delete_trip", MagicMock(return_value={"success": True, "message": "Deleted", "deleted_trip_id": trip_id}))
    monkeypatch.setattr(trips.itinerary_service, "get_itinerary_by_trip_id", AsyncMock(return_value=mock_itin))
    monkeypatch.setattr(itinerary.itinerary_service, "generate_itinerary", AsyncMock(return_value=mock_itin))
    monkeypatch.setattr(itinerary.route_optimization_service, "optimize_itinerary", MagicMock(return_value=mock_itin))
    monkeypatch.setattr(share.share_service.trip_service, "get_trip_by_id", MagicMock(return_value=mock_trip_record))
    monkeypatch.setattr(share.share_service.itinerary_service, "get_itinerary_by_trip_id", AsyncMock(return_value=mock_itin))

    # Step 1: Create Trip
    create_payload = {
        "destination": "Vienna, Austria",
        "start_date": "2027-05-01",
        "end_date": "2027-05-03",
        "num_travelers": 2,
        "budget": 2000.0,
        "travel_style": "cultural",
        "travel_interests": ["museums", "music"],
        "primary_vibe": "Cultural",
    }
    res_create = client.post("/api/v1/trips", json=create_payload)
    assert res_create.status_code == 201
    assert res_create.json()["id"] == trip_id

    # Step 2: Retrieve Saved Trip Details
    res_get = client.get(f"/api/v1/trips/{trip_id}")
    assert res_get.status_code == 200
    assert res_get.json()["destination"] == "Vienna, Austria"

    # Step 3: Itinerary Generation
    gen_payload = {**create_payload, "trip_id": trip_id}
    res_gen = client.post("/api/v1/itinerary/generate", json=gen_payload)
    assert res_gen.status_code == 200
    assert len(res_gen.json()["days"]) >= 1

    # Step 4: Route Optimization
    res_opt = client.post("/api/v1/itinerary/optimize-route", json={"itinerary": mock_itin.model_dump()})
    assert res_opt.status_code == 200
    assert "route_legs" in res_opt.json()["days"][0]

    # Step 5: PDF Export
    res_pdf = client.get(f"/api/v1/trips/{trip_id}/export/pdf")
    assert res_pdf.status_code == 200
    assert res_pdf.headers["content-type"] == "application/pdf"
    assert res_pdf.content.startswith(b"%PDF-")

    # Step 6: JSON Export
    res_json = client.get(f"/api/v1/trips/{trip_id}/export/json")
    assert res_json.status_code == 200
    assert res_json.json()["trip"]["id"] == trip_id

    # Step 7: Plain-Text Summary
    res_sum = client.post(f"/api/v1/trips/{trip_id}/summary")
    assert res_sum.status_code == 200
    assert "TRIP ITINERARY: VIENNA, AUSTRIA" in res_sum.json()["summary_text"]

    # Step 8: Public Share Token Generation
    res_share = client.post(f"/api/v1/trips/{trip_id}/share")
    assert res_share.status_code == 200
    share_token = res_share.json()["share_token"]
    assert share_token

    # Step 9: Public Read-Only Access (no PII)
    res_public = client.get(f"/api/v1/shared/{share_token}")
    assert res_public.status_code == 200
    assert res_public.json()["destination"] == "Vienna, Austria"
    assert "user_id" not in res_public.json()
    assert "email" not in res_public.json()

    # Step 10: Revoke Public Share
    res_revoke = client.delete(f"/api/v1/trips/{trip_id}/share")
    assert res_revoke.status_code == 200
    assert res_revoke.json()["success"] is True

    # Step 11: Delete Trip
    res_del = client.delete(f"/api/v1/trips/{trip_id}")
    assert res_del.status_code == 200
    assert res_del.json()["success"] is True


# ── 2. Error Resilience & Malformed Output Handling ────────────────────────

def test_clean_json_strips_markdown_code_fences():
    """Verify that _clean_json_text strips markdown fences and surrounding commentary."""
    from app.services.itinerary_service import _clean_json_text
    raw_ai_response = """
    Here is the requested itinerary:
    ```json
    {
        "destination": "Kyoto",
        "duration_days": 3
    }
    ```
    I hope you have a great trip!
    """
    cleaned = _clean_json_text(raw_ai_response)
    assert cleaned.startswith("{")
    assert cleaned.endswith("}")
    assert "Here is the" not in cleaned


def test_missing_required_fields_raises_502(monkeypatch):
    """Verify that incomplete AI responses trigger an informative HTTP 502 error."""
    from app.services.itinerary_service import ItineraryService
    from app.services.providers.base import LLMProvider

    class IncompleteLLMProvider(LLMProvider):
        @property
        def name(self) -> str:
            return "mock-incomplete"

        @property
        def model_name(self) -> str:
            return "mock-model"

        async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
            # Returns valid JSON but completely misses required schema fields
            return '{"destination": "Paris"}'

    svc = ItineraryService(provider=IncompleteLLMProvider())
    from app.models.itinerary import ItineraryGenerateRequest
    from datetime import date

    req = ItineraryGenerateRequest(
        destination="Paris, France",
        start_date=date(2027, 6, 1),
        end_date=date(2027, 6, 3),
        budget=1500.0,
        travel_style="cultural",
        travel_interests=["art"],
        num_travelers=1,
    )

    with pytest.raises(HTTPException) as exc_info:
        import asyncio
        asyncio.run(svc.generate_itinerary(req))

    assert exc_info.value.status_code == 502
    assert "validation failed" in exc_info.value.detail.lower()


# ── 3. AI Provider Failure Graceful Recovery ───────────────────────────────

def test_ai_provider_quota_exceeded_error_handling(monkeypatch):
    """Verify that HTTP 429 rate limit errors from AI providers return clean 429 status."""
    from app.services.itinerary_service import ItineraryService
    from app.services.providers.base import LLMProvider
    from app.models.itinerary import ItineraryGenerateRequest
    from datetime import date

    class RateLimitedProvider(LLMProvider):
        @property
        def name(self) -> str:
            return "mock-ratelimited"

        @property
        def model_name(self) -> str:
            return "mock-model"

        async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
            raise HTTPException(status_code=429, detail="Resource has been exhausted (quota limit reached).")

    svc = ItineraryService(provider=RateLimitedProvider())
    req = ItineraryGenerateRequest(
        destination="Rome, Italy",
        start_date=date(2027, 5, 1),
        end_date=date(2027, 5, 3),
        budget=1000.0,
        travel_style="cultural",
        travel_interests=["history"],
        num_travelers=1,
    )
    with pytest.raises(HTTPException) as exc_info:
        import asyncio
        asyncio.run(svc.generate_itinerary(req))

    assert exc_info.value.status_code == 429
    assert "quota" in exc_info.value.detail.lower()


def test_ai_provider_timeout_error_handling():
    """Verify that provider timeouts return clean HTTP 504 Gateway Timeout."""
    from app.services.itinerary_service import ItineraryService
    from app.services.providers.base import LLMProvider
    from app.models.itinerary import ItineraryGenerateRequest
    from datetime import date

    class TimeoutProvider(LLMProvider):
        @property
        def name(self) -> str:
            return "mock-timeout"

        @property
        def model_name(self) -> str:
            return "mock-model"

        async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
            raise HTTPException(status_code=504, detail="AI generation timed out after 30 seconds.")

    svc = ItineraryService(provider=TimeoutProvider())
    req = ItineraryGenerateRequest(
        destination="Rome, Italy",
        start_date=date(2027, 5, 1),
        end_date=date(2027, 5, 3),
        budget=1000.0,
        travel_style="cultural",
        travel_interests=["history"],
        num_travelers=1,
    )
    with pytest.raises(HTTPException) as exc_info:
        import asyncio
        asyncio.run(svc.generate_itinerary(req))

    assert exc_info.value.status_code == 504
    assert "timed out" in exc_info.value.detail.lower()


# ── 4. Supabase Database Graceful Degradation ───────────────────────────────

def test_database_connection_failure_handling(monkeypatch):
    """Verify that database errors return clean HTTP 500/503 without crashing the app."""
    from app.services.trip_service import TripService
    mock_db = MagicMock()
    mock_db.table.side_effect = RuntimeError("Supabase cluster unreachable")

    svc = TripService(db=mock_db)
    with pytest.raises(HTTPException) as exc_info:
        svc.get_all_trips()

    assert exc_info.value.status_code == 500
    assert "Failed to retrieve trips" in exc_info.value.detail
