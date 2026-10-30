"""
tests/test_share_export.py

Comprehensive test suite for Epic 5 – Activity 5.2: Share & Export Module.
Tests:
  - POST   /api/v1/trips/{trip_id}/share (Generate share token & URL)
  - DELETE /api/v1/trips/{trip_id}/share (Revoke share token)
  - GET    /api/v1/shared/{share_token} (Public read-only view, zero PII)
  - GET    /api/v1/shared/{share_token} (404 on invalid, 410 on revoked)
  - GET    /api/v1/trips/{trip_id}/export/pdf (Server-side PDF generation)
  - GET    /api/v1/trips/{trip_id}/export/json (Structured JSON export)
  - POST   /api/v1/trips/{trip_id}/summary (Clipboard text summary)
"""

from unittest.mock import AsyncMock, MagicMock
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.share import share_service
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
from app.models.share import (
    SharedTripPublicResponse,
    TripRevokeResponse,
    TripShareResponse,
    TripSummaryResponse,
)

client = TestClient(app)


def get_mock_itinerary(trip_id: str = "trip-test-123") -> ItineraryResponse:
    day = DayItinerary(
        day_number=1,
        date="2027-06-01",
        theme="Historic Kyoto & Shinto Shrines",
        morning_activity=Activity(
            time_slot="morning",
            name="Fushimi Inari Shrine",
            description="Famous path lined with thousands of vermilion torii gates.",
            location="Fushimi",
            suggested_duration="2.5 hours",
            estimated_cost="Free",
            schedule=ActivitySchedule(
                start_time="08:30 AM",
                end_time="11:00 AM",
                duration_minutes=150,
            ),
        ),
        lunch=DiningRecommendation(
            meal_type="Lunch",
            name="Inari Soba Tei",
            cuisine="Japanese Soba",
            description="Fresh handmade buckwheat noodles.",
            estimated_cost="~$15 USD",
        ),
        afternoon_activity=Activity(
            time_slot="afternoon",
            name="Kiyomizu-dera",
            description="Ancient wooden temple with scenic panoramic views.",
            suggested_duration="2 hours",
            estimated_cost="¥400 (~$3 USD)",
        ),
        dinner=DiningRecommendation(
            meal_type="Dinner",
            name="Gion Kaiseki",
            cuisine="Kyoto Seasonal",
            description="Traditional multi-course feast.",
            estimated_cost="~$60 USD",
        ),
        evening_activity=Activity(
            time_slot="evening",
            name="Gion Lantern Stroll",
            description="Scenic evening walk through historic preservation streets.",
            suggested_duration="1 hour",
            estimated_cost="Free",
        ),
        transportation=Transportation(
            mode="Keihan Line & Walking",
            estimated_time="20 mins",
            estimated_cost="~$3 USD",
        ),
        daily_budget=DailyBudget(
            activities_cost="~$3 USD",
            dining_cost="~$75 USD",
            transportation_cost="~$3 USD",
            total_daily_estimated="~$81 USD",
        ),
        practical_tips="Arrive early in the morning to beat the crowds.",
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

    return ItineraryResponse(
        trip_id=trip_id,
        destination="Kyoto, Japan",
        start_date="2027-06-01",
        end_date="2027-06-05",
        duration_days=5,
        total_budget=3000.0,
        travel_style="cultural",
        travel_pace="moderate",
        days=[day],
        trip_summary="A serene 5-day cultural and culinary journey through ancient Kyoto.",
        total_estimated_cost="$405 USD (excluding accommodation)",
        packing_and_prep_tips=["Comfortable walking shoes", "Pocket Wi-Fi device"],
        primary_vibe="Cultural",
        secondary_vibes=["Food & Culinary"],
    )


def get_mock_trip(trip_id: str = "trip-test-123") -> dict:
    return {
        "id": trip_id,
        "user_id": "secret-user-uuid-999",
        "destination": "Kyoto, Japan",
        "start_date": "2027-06-01",
        "end_date": "2027-06-05",
        "num_travelers": 2,
        "budget": 3000.0,
        "travel_style": "cultural",
        "travel_pace": "moderate",
        "primary_vibe": "Cultural",
        "secondary_vibes": ["Food & Culinary"],
        "has_itinerary": True,
        "created_at": "2026-10-30T12:00:00Z",
    }


# ── 1. Share Generation Tests ───────────────────────────────────────────────

def test_share_trip_endpoint_creates_token(monkeypatch):
    """Verify POST /api/v1/trips/{trip_id}/share returns a secure share token & url."""
    mock_resp = TripShareResponse(
        trip_id="trip-test-123",
        share_token="secure_token_abc123",
        share_url="http://localhost:5173/?share=secure_token_abc123",
        is_active=True,
    )
    monkeypatch.setattr(share_service, "create_or_get_share_link", MagicMock(return_value=mock_resp))

    response = client.post("/api/v1/trips/trip-test-123/share")
    assert response.status_code == 200
    data = response.json()
    assert data["trip_id"] == "trip-test-123"
    assert data["share_token"] == "secure_token_abc123"
    assert "share_url" in data
    assert data["is_active"] is True


def test_share_trip_endpoint_trailing_slash(monkeypatch):
    """Verify POST /api/v1/trips/{trip_id}/share/ trailing slash alias works."""
    mock_resp = TripShareResponse(
        trip_id="trip-test-123",
        share_token="token_trailing_slash",
        share_url="http://localhost:5173/?share=token_trailing_slash",
        is_active=True,
    )
    monkeypatch.setattr(share_service, "create_or_get_share_link", MagicMock(return_value=mock_resp))

    response = client.post("/api/v1/trips/trip-test-123/share/")
    assert response.status_code == 200
    assert response.json()["share_token"] == "token_trailing_slash"


def test_share_trip_missing_trip_returns_404():
    """Verify POST /api/v1/trips/{trip_id}/share returns 404 for unknown trip ID."""
    response = client.post("/api/v1/trips/non-existent-uuid-9999/share")
    assert response.status_code == 404


# ── 2. Share Revocation Tests ───────────────────────────────────────────────

def test_revoke_share_endpoint(monkeypatch):
    """Verify DELETE /api/v1/trips/{trip_id}/share revokes the active share link."""
    mock_resp = TripRevokeResponse(
        trip_id="trip-test-123",
        success=True,
        message="Trip sharing link has been revoked.",
    )
    monkeypatch.setattr(share_service, "revoke_share_link", MagicMock(return_value=mock_resp))

    response = client.delete("/api/v1/trips/trip-test-123/share")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["trip_id"] == "trip-test-123"


# ── 3. Public Read-Only Share View Tests ───────────────────────────────────

def test_get_shared_trip_public_success(monkeypatch):
    """Verify GET /api/v1/shared/{share_token} returns public trip data with NO user PII."""
    mock_itinerary = get_mock_itinerary("trip-test-123")
    public_resp = SharedTripPublicResponse(
        share_token="tok_12345",
        trip_id="trip-test-123",
        destination="Kyoto, Japan",
        start_date="2027-06-01",
        end_date="2027-06-05",
        duration_days=5,
        total_budget=3000.0,
        travel_style="cultural",
        travel_pace="moderate",
        primary_vibe="Cultural",
        secondary_vibes=["Food & Culinary"],
        trip_summary="A serene 5-day cultural journey.",
        total_estimated_cost="$405 USD",
        packing_and_prep_tips=["Shoes"],
        days=mock_itinerary.days,
        is_shared=True,
    )
    monkeypatch.setattr(
        share_service, "get_shared_trip", AsyncMock(return_value=public_resp)
    )

    response = client.get("/api/v1/shared/tok_12345")
    assert response.status_code == 200
    data = response.json()
    assert data["destination"] == "Kyoto, Japan"
    assert data["is_shared"] is True
    assert len(data["days"]) == 1
    # Security: Ensure no sensitive user fields exist
    assert "user_id" not in data
    assert "email" not in data


def test_get_shared_trip_invalid_token_returns_404():
    """Verify GET /api/v1/shared/{share_token} returns 404 when token is not found."""
    response = client.get("/api/v1/shared/completely_invalid_token_xyz")
    assert response.status_code == 404


def test_get_shared_trip_revoked_token_returns_410(monkeypatch):
    """Verify GET /api/v1/shared/{share_token} returns 410 Gone when token was revoked."""
    from fastapi import HTTPException
    monkeypatch.setattr(
        share_service,
        "get_shared_trip",
        AsyncMock(side_effect=HTTPException(status_code=410, detail="This trip share link has been revoked by the owner.")),
    )

    response = client.get("/api/v1/shared/revoked_token_123")
    assert response.status_code == 410
    assert "revoked" in response.json()["detail"].lower()


# ── 4. PDF Export Tests ────────────────────────────────────────────────────

def test_export_pdf_endpoint_success(monkeypatch):
    """Verify GET /api/v1/trips/{trip_id}/export/pdf returns PDF binary with correct headers."""
    # Let the real ReportLab PDF builder generate a genuine PDF
    trip = get_mock_trip("trip-test-123")
    itinerary = get_mock_itinerary("trip-test-123")

    monkeypatch.setattr(share_service.trip_service, "get_trip_by_id", MagicMock(return_value=trip))
    monkeypatch.setattr(share_service.itinerary_service, "get_itinerary_by_trip_id", AsyncMock(return_value=itinerary))

    response = client.get("/api/v1/trips/trip-test-123/export/pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment; filename=" in response.headers["content-disposition"]
    # PDF files start with the magic bytes %PDF-
    assert response.content.startswith(b"%PDF-")
    assert len(response.content) > 500  # Genuine PDF payload


def test_export_pdf_missing_trip_returns_404():
    """Verify GET /api/v1/trips/{trip_id}/export/pdf returns 404 if trip not found."""
    response = client.get("/api/v1/trips/non-existent-trip-id/export/pdf")
    assert response.status_code == 404


# ── 5. JSON Export Tests ───────────────────────────────────────────────────

def test_export_json_endpoint_success(monkeypatch):
    """Verify GET /api/v1/trips/{trip_id}/export/json returns structured data matching schemas."""
    trip = get_mock_trip("trip-test-123")
    itinerary = get_mock_itinerary("trip-test-123")

    monkeypatch.setattr(share_service.trip_service, "get_trip_by_id", MagicMock(return_value=trip))
    monkeypatch.setattr(share_service.itinerary_service, "get_itinerary_by_trip_id", AsyncMock(return_value=itinerary))

    response = client.get("/api/v1/trips/trip-test-123/export/json")
    assert response.status_code == 200
    assert "attachment; filename=" in response.headers["content-disposition"]
    data = response.json()
    assert "export_metadata" in data
    assert "trip" in data
    assert "itinerary" in data
    assert data["trip"]["destination"] == "Kyoto, Japan"
    assert len(data["itinerary"]["days"]) == 1


def test_export_json_missing_trip_returns_404():
    """Verify GET /api/v1/trips/{trip_id}/export/json returns 404 for unknown trip."""
    response = client.get("/api/v1/trips/00000000-0000-0000-0000-000000000000/export/json")
    assert response.status_code == 404


# ── 6. Trip Summary Tests ──────────────────────────────────────────────────

def test_trip_summary_endpoint_success(monkeypatch):
    """Verify POST /api/v1/trips/{trip_id}/summary returns formatted clipboard text."""
    trip = get_mock_trip("trip-test-123")
    itinerary = get_mock_itinerary("trip-test-123")

    monkeypatch.setattr(share_service.trip_service, "get_trip_by_id", MagicMock(return_value=trip))
    monkeypatch.setattr(share_service.itinerary_service, "get_itinerary_by_trip_id", AsyncMock(return_value=itinerary))

    response = client.post("/api/v1/trips/trip-test-123/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["destination"] == "Kyoto, Japan"
    assert "TRIP ITINERARY: KYOTO, JAPAN" in data["summary_text"]
    assert "Fushimi Inari Shrine" in data["summary_text"]
    assert len(data["daily_highlights"]) == 1
    assert data["daily_highlights"][0]["morning"] == "Fushimi Inari Shrine"


def test_trip_summary_missing_trip_returns_404():
    """Verify POST /api/v1/trips/{trip_id}/summary returns 404 for unknown trip."""
    response = client.post("/api/v1/trips/00000000-0000-0000-0000-000000000000/summary")
    assert response.status_code == 404
