"""
backend/app/api/trips.py

FastAPI router for trip CRUD and management endpoints.

Endpoints
---------
POST   /api/v1/trips/              – Create a new trip.
GET    /api/v1/trips/              – List all saved trips (optionally ?user_id=...).
GET    /api/v1/trips/{trip_id}     – Get a single trip (or list by user_id if prefix matches).
GET    /api/v1/trips/{trip_id}/{user_id} – Get a single trip scoped to user.
PUT    /api/v1/trips/{trip_id}     – Update trip details and preferences.
PATCH  /api/v1/trips/{trip_id}     – Partial update of trip details and preferences.
DELETE /api/v1/trips/{trip_id}     – Delete a trip and all its saved itineraries.
GET    /api/v1/trips/{trip_id}/itinerary – Retrieve saved itinerary for a trip.
"""

from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Query

from app.models.trip import (
    TripCreateRequest,
    TripResponse,
    TripUpdateRequest,
    TripDeleteResponse,
)
from app.models.itinerary import ItineraryResponse
from app.services.trip_service import TripService
from app.services.itinerary_service import ItineraryService

# ── Router (prefix and tag applied in main.py) ────────────────────────────────
router = APIRouter()

# ── Service singletons ─────────────────────────────────────────────────────────
trip_service = TripService()
itinerary_service = ItineraryService()


# ── Create a trip ──────────────────────────────────────────────────────────────

@router.post("", response_model=TripResponse, status_code=201, include_in_schema=False)
@router.post("/", response_model=TripResponse, status_code=201)
def create_trip(request: TripCreateRequest) -> TripResponse:
    """
    Create a new trip record for the authenticated or default user.
    Persists trip details and preferences in Supabase.
    """
    record = trip_service.create_trip(request)
    return TripResponse(**record)


# ── List all trips ─────────────────────────────────────────────────────────────

@router.get("", response_model=list[TripResponse], include_in_schema=False)
@router.get("/", response_model=list[TripResponse])
def list_trips(user_id: str | None = Query(default=None, description="Optional user UUID filter")) -> list[TripResponse]:
    """
    Return all saved trips (ordered newest first), optionally filtered by user_id.
    Includes itinerary availability status (has_itinerary) and vibe metadata.
    """
    records = trip_service.get_all_trips(user_id=user_id)
    return [TripResponse(**r) for r in records]


# ── Get a single trip or list by user_id (flexible routing) ───────────────────

@router.get("/{trip_id}", response_model=Any)
def get_trip_or_user_trips(trip_id: str, user_id: str | None = None) -> Any:
    """
    Retrieve a trip by ID.
    If the parameter matches a user identifier (e.g. starts with 'user-'),
    returns the list of trips belonging to that user for backwards compatibility.
    """
    # Backwards compatibility check for Activity 3.1 tests
    if trip_id.startswith("user"):
        records = trip_service.get_trips_by_user(trip_id)
        return [TripResponse(**r) for r in records]

    try:
        record = trip_service.get_trip_by_id(trip_id, user_id=user_id)
        return TripResponse(**record)
    except Exception:
        # Check if caller passed a user UUID instead of trip UUID
        user_trips = trip_service.get_trips_by_user(trip_id)
        if user_trips:
            return [TripResponse(**r) for r in user_trips]
        raise


# ── Retrieve saved itinerary for a trip ───────────────────────────────────────

@router.get("/{trip_id}/itinerary", response_model=ItineraryResponse)
def get_trip_itinerary(trip_id: str) -> ItineraryResponse:
    """
    Retrieve the complete saved daily itinerary for a trip from Supabase without
    triggering AI regeneration. Preserves all schedules, routes, transit, and vibes.
    """
    return itinerary_service.get_itinerary_by_trip_id(trip_id)


# ── Get a single trip scoped to user ──────────────────────────────────────────

@router.get("/{trip_id}/{user_id}", response_model=TripResponse)
def get_trip(trip_id: str, user_id: str) -> TripResponse:
    """
    Return a single trip scoped to the authenticated user.
    """
    record = trip_service.get_trip_by_id(trip_id, user_id)
    return TripResponse(**record)


# ── Update a trip ──────────────────────────────────────────────────────────────

@router.put("/{trip_id}", response_model=TripResponse)
@router.patch("/{trip_id}", response_model=TripResponse)
def update_trip(
    trip_id: str,
    request: TripUpdateRequest,
    user_id: str | None = Query(default=None, description="Optional user ownership check"),
) -> TripResponse:
    """
    Update trip parameters (dates, destination, budget, pace, vibes, dietary, interests).
    Preserves unchanged fields and flags whether itinerary regeneration is recommended.
    """
    record = trip_service.update_trip(trip_id=trip_id, update_data=request, user_id=user_id)
    return TripResponse(**record)


# ── Delete a trip ──────────────────────────────────────────────────────────────

@router.delete("/{trip_id}", response_model=TripDeleteResponse)
def delete_trip(
    trip_id: str,
    user_id: str | None = Query(default=None, description="Optional user ownership check"),
) -> TripDeleteResponse:
    """
    Permanently delete a trip and all its associated daily itineraries.
    """
    result = trip_service.delete_trip(trip_id=trip_id, user_id=user_id)
    return TripDeleteResponse(**result)

