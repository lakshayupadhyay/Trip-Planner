"""
backend/app/services/trip_service.py

Business-logic layer for trip and preference operations against Supabase.
Integrates with the live Supabase schema:
  - Table `trips`: destination, start_date, end_date, total_budget, user_id
  - Table `preferences`: budget, travel_style, interests, preferred_destination, user_id
"""

from __future__ import annotations

import uuid
from typing import Any
from fastapi import HTTPException

from app.models.trip import TripCreateRequest, TripUpdateRequest


class TripService:
    """
    Handles all Supabase interactions for trips and travel preferences.
    """

    def __init__(self, db: Any | None = None) -> None:
        """Store an optional custom or mock database client."""
        self._db = db

    @property
    def db(self) -> Any:
        """Lazily load the shared Supabase client."""
        if self._db is not None:
            return self._db
        try:
            from app.utils.supabase_client import supabase
            return supabase
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Database connection error: {exc}",
            ) from exc

    def _resolve_user_id(self, user_id: str | None) -> str:
        """
        Ensure user_id is a valid UUID that satisfies the database foreign key.
        If user_id is None, invalid UUID, or not found, fall back to the first available user.
        """
        # Check if user_id is already a valid UUID string
        is_valid_uuid = False
        if user_id:
            try:
                uuid.UUID(str(user_id))
                is_valid_uuid = True
            except (ValueError, AttributeError):
                is_valid_uuid = False

        if is_valid_uuid:
            try:
                existing = self.db.table("users").select("id").eq("id", user_id).limit(1).execute()
                if existing.data:
                    return str(user_id)
            except Exception:
                pass

        # Fall back to first user in users table
        try:
            users_res = self.db.table("users").select("id").limit(1).execute()
            if users_res.data:
                return str(users_res.data[0]["id"])
        except Exception:
            pass

        # If no user exists, create demo user
        try:
            created_auth = self.db.auth.admin.create_user({
                "email": "demo@travelplanner.local",
                "password": "demoPassword123!",
                "email_confirm": True,
                "user_metadata": {"full_name": "Demo Traveler"},
            })
            new_id = str(created_auth.user.id)
            self.db.table("users").insert({
                "id": new_id,
                "email": "demo@travelplanner.local",
                "full_name": "Demo Traveler",
            }).execute()
            return new_id
        except Exception:
            # If auth creation fails, return fallback UUID
            return "3060d1c4-0a78-4ef9-9590-5a05bd808915"

    # ── Create Trip & Preferences ──────────────────────────────────────────────

    def create_trip(self, trip_data: TripCreateRequest) -> dict:
        """
        Save trip details and travel preferences to Supabase.
        Persists:
          - trips: user_id, destination, start_date, end_date, total_budget
          - preferences: user_id, budget, travel_style, interests, preferred_destination
          - itineraries: draft preferences entry (day_number 9999) preserving vibes & details
        """
        valid_user_id = self._resolve_user_id(trip_data.user_id)

        # 1. Insert into trips table
        trip_payload = {
            "user_id": valid_user_id,
            "destination": trip_data.destination,
            "start_date": trip_data.start_date.isoformat(),
            "end_date": trip_data.end_date.isoformat(),
            "total_budget": trip_data.budget,
        }

        try:
            trip_response = self.db.table("trips").insert(trip_payload).execute()
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create trip in database: {exc}",
            ) from exc

        if not trip_response.data:
            raise HTTPException(
                status_code=500,
                detail="Database returned no data after creating trip.",
            )

        created_trip = trip_response.data[0]
        trip_id = str(created_trip["id"])

        # 2. Insert into preferences table
        pref_payload = {
            "user_id": valid_user_id,
            "budget": trip_data.budget,
            "travel_style": trip_data.travel_style,
            "interests": trip_data.travel_interests,
            "preferred_destination": trip_data.destination,
        }

        try:
            self.db.table("preferences").insert(pref_payload).execute()
        except Exception:
            pass

        # 3. Store draft preferences in itineraries table (day_number 9999) to preserve vibes
        try:
            draft_payload = {
                "trip_id": trip_id,
                "day_number": 9999,
                "activities": {
                    "_is_preferences": True,
                    "num_travelers": trip_data.num_travelers,
                    "travel_style": trip_data.travel_style,
                    "travel_interests": trip_data.travel_interests,
                    "dietary_preferences": trip_data.dietary_preferences,
                    "travel_pace": trip_data.travel_pace,
                    "primary_vibe": trip_data.primary_vibe,
                    "secondary_vibes": trip_data.secondary_vibes,
                    "additional_requirements": trip_data.additional_requirements,
                },
            }
            self.db.table("itineraries").insert(draft_payload).execute()
        except Exception:
            pass

        # 4. Construct unified response
        return {
            "id": trip_id,
            "user_id": str(created_trip["user_id"]),
            "destination": created_trip["destination"],
            "start_date": created_trip["start_date"],
            "end_date": created_trip["end_date"],
            "num_travelers": trip_data.num_travelers,
            "budget": float(created_trip.get("total_budget") or trip_data.budget),
            "travel_style": trip_data.travel_style,
            "travel_interests": trip_data.travel_interests,
            "dietary_preferences": trip_data.dietary_preferences,
            "travel_pace": trip_data.travel_pace,
            "primary_vibe": trip_data.primary_vibe,
            "secondary_vibes": trip_data.secondary_vibes or [],
            "additional_requirements": trip_data.additional_requirements,
            "status": "pending",
            "has_itinerary": False,
            "itinerary_regeneration_recommended": False,
            "created_at": created_trip.get("created_at"),
        }

    # ── Read Trips ─────────────────────────────────────────────────────────────

    def _attach_itinerary_metadata(self, trip_id: str, trip_record: dict) -> dict:
        """Helper to inspect itineraries table and extract itinerary status & preferences."""
        has_itinerary = False
        primary_vibe = None
        secondary_vibes = []
        travel_style = trip_record.get("travel_style", "cultural")
        travel_pace = trip_record.get("travel_pace", "moderate")
        num_travelers = trip_record.get("num_travelers", 1)
        travel_interests = trip_record.get("travel_interests") or []
        dietary_preferences = trip_record.get("dietary_preferences") or []
        additional_requirements = trip_record.get("additional_requirements")

        try:
            itinerary_rows = (
                self.db.table("itineraries")
                .select("day_number, activities")
                .eq("trip_id", str(trip_id))
                .order("day_number", desc=False)
                .execute()
            )
            for row in itinerary_rows.data or []:
                day_num = row.get("day_number", 0)
                act = row.get("activities") or {}

                if day_num < 900 and isinstance(act, dict) and not act.get("_is_preferences") and ("morning_activity" in act or "theme" in act):
                    has_itinerary = True
                    # If Day 1 has trip_metadata, extract vibes & pace
                    if "trip_metadata" in act:
                        meta = act["trip_metadata"]
                        primary_vibe = meta.get("primary_vibe") or primary_vibe
                        secondary_vibes = meta.get("secondary_vibes") or secondary_vibes
                        travel_style = meta.get("travel_style") or travel_style
                        travel_pace = meta.get("travel_pace") or travel_pace
                elif act.get("_is_preferences") or day_num == 9999:
                    # Draft preferences row
                    primary_vibe = act.get("primary_vibe") or primary_vibe
                    secondary_vibes = act.get("secondary_vibes") or secondary_vibes
                    travel_style = act.get("travel_style") or travel_style
                    travel_pace = act.get("travel_pace") or travel_pace
                    num_travelers = act.get("num_travelers") or num_travelers
                    travel_interests = act.get("travel_interests") or travel_interests
                    dietary_preferences = act.get("dietary_preferences") or dietary_preferences
                    additional_requirements = act.get("additional_requirements") or additional_requirements
        except Exception:
            pass

        return {
            "has_itinerary": has_itinerary,
            "status": "confirmed" if has_itinerary else "pending",
            "primary_vibe": primary_vibe,
            "secondary_vibes": secondary_vibes,
            "travel_style": travel_style,
            "travel_pace": travel_pace,
            "num_travelers": num_travelers,
            "travel_interests": travel_interests,
            "dietary_preferences": dietary_preferences,
            "additional_requirements": additional_requirements,
        }

    def get_all_trips(self, user_id: str | None = None) -> list[dict]:
        """Return all trips, optionally filtered by user_id."""
        try:
            query = self.db.table("trips").select("*").order("created_at", desc=True)
            if user_id:
                query = query.eq("user_id", user_id)
            response = query.execute()
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve trips: {exc}",
            ) from exc

        records = []
        for r in response.data or []:
            trip_id = str(r["id"])
            attached = self._attach_itinerary_metadata(trip_id, r)

            records.append({
                "id": trip_id,
                "user_id": str(r["user_id"]),
                "destination": r["destination"],
                "start_date": r["start_date"],
                "end_date": r["end_date"],
                "num_travelers": attached["num_travelers"],
                "budget": float(r.get("total_budget") or 0.0),
                "travel_style": attached["travel_style"],
                "travel_interests": attached["travel_interests"],
                "dietary_preferences": attached["dietary_preferences"],
                "travel_pace": attached["travel_pace"],
                "primary_vibe": attached["primary_vibe"],
                "secondary_vibes": attached["secondary_vibes"],
                "additional_requirements": attached["additional_requirements"],
                "status": attached["status"],
                "has_itinerary": attached["has_itinerary"],
                "itinerary_regeneration_recommended": False,
                "created_at": r.get("created_at"),
            })
        return records

    def get_trips_by_user(self, user_id: str) -> list[dict]:
        """Return all trips for the specified user."""
        return self.get_all_trips(user_id=user_id)

    def get_trip_by_id(self, trip_id: str, user_id: str | None = None) -> dict:
        """Return a single trip by ID, optionally validating ownership."""
        # Validate UUID format: if invalid, trip does not exist
        try:
            uuid.UUID(str(trip_id))
        except (ValueError, AttributeError):
            raise HTTPException(status_code=404, detail=f"Trip '{trip_id}' not found.")

        try:
            query = self.db.table("trips").select("*").eq("id", trip_id)
            if user_id:
                query = query.eq("user_id", user_id)
            response = query.limit(1).execute()
        except Exception as exc:
            if "uuid" in str(exc).lower():
                raise HTTPException(status_code=404, detail=f"Trip '{trip_id}' not found.")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve trip: {exc}",
            ) from exc

        if not response.data:
            detail = f"Trip '{trip_id}' not found." if not user_id else f"Trip '{trip_id}' not found for user '{user_id}'."
            raise HTTPException(status_code=404, detail=detail)

        r = response.data[0]
        attached = self._attach_itinerary_metadata(trip_id, r)

        return {
            "id": str(r["id"]),
            "user_id": str(r["user_id"]),
            "destination": r["destination"],
            "start_date": r["start_date"],
            "end_date": r["end_date"],
            "num_travelers": attached["num_travelers"],
            "budget": float(r.get("total_budget") or 0.0),
            "travel_style": attached["travel_style"],
            "travel_interests": attached["travel_interests"],
            "dietary_preferences": attached["dietary_preferences"],
            "travel_pace": attached["travel_pace"],
            "primary_vibe": attached["primary_vibe"],
            "secondary_vibes": attached["secondary_vibes"],
            "additional_requirements": attached["additional_requirements"],
            "status": attached["status"],
            "has_itinerary": attached["has_itinerary"],
            "itinerary_regeneration_recommended": False,
            "created_at": r.get("created_at"),
        }

    # ── Update Trip ────────────────────────────────────────────────────────────

    def update_trip(
        self, trip_id: str, update_data: TripUpdateRequest, user_id: str | None = None
    ) -> dict:
        """
        Update an existing trip record and its stored preferences.
        Validates date ordering, preserves unchanged fields, and checks if itinerary regeneration is needed.
        """
        existing = self.get_trip_by_id(trip_id, user_id=user_id)

        # Build payload for trips table
        trip_updates = {}
        destination_changed = False
        dates_changed = False

        if update_data.destination is not None and update_data.destination.strip():
            new_dest = update_data.destination.strip()
            if new_dest.lower() != existing["destination"].lower():
                destination_changed = True
            trip_updates["destination"] = new_dest

        # Validate date consistency with existing values if only one date is updated
        new_start = update_data.start_date
        new_end = update_data.end_date

        if new_start is not None and new_end is None:
            import datetime
            exist_end = datetime.date.fromisoformat(str(existing["end_date"]))
            if exist_end <= new_start:
                raise HTTPException(
                    status_code=422,
                    detail=f"Updated start_date ({new_start}) must be before existing end_date ({exist_end}).",
                )
            trip_updates["start_date"] = new_start.isoformat()
            dates_changed = True

        elif new_end is not None and new_start is None:
            import datetime
            exist_start = datetime.date.fromisoformat(str(existing["start_date"]))
            if new_end <= exist_start:
                raise HTTPException(
                    status_code=422,
                    detail=f"Updated end_date ({new_end}) must be after existing start_date ({exist_start}).",
                )
            trip_updates["end_date"] = new_end.isoformat()
            dates_changed = True

        elif new_start is not None and new_end is not None:
            trip_updates["start_date"] = new_start.isoformat()
            trip_updates["end_date"] = new_end.isoformat()
            dates_changed = True

        if update_data.budget is not None:
            trip_updates["total_budget"] = update_data.budget

        # Apply updates to trips table
        if trip_updates:
            try:
                self.db.table("trips").update(trip_updates).eq("id", trip_id).execute()
            except Exception as exc:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to update trip record: {exc}",
                ) from exc

        # Update draft preferences entry in itineraries table
        try:
            pref_data = {
                "_is_preferences": True,
                "num_travelers": update_data.num_travelers if update_data.num_travelers is not None else existing["num_travelers"],
                "travel_style": update_data.travel_style if update_data.travel_style is not None else existing["travel_style"],
                "travel_interests": update_data.travel_interests if update_data.travel_interests is not None else existing["travel_interests"],
                "dietary_preferences": update_data.dietary_preferences if update_data.dietary_preferences is not None else existing["dietary_preferences"],
                "travel_pace": update_data.travel_pace if update_data.travel_pace is not None else existing["travel_pace"],
                "primary_vibe": update_data.primary_vibe if update_data.primary_vibe is not None else existing["primary_vibe"],
                "secondary_vibes": update_data.secondary_vibes if update_data.secondary_vibes is not None else existing["secondary_vibes"],
                "additional_requirements": update_data.additional_requirements if update_data.additional_requirements is not None else existing["additional_requirements"],
            }
            # Delete old draft row and insert updated draft row
            self.db.table("itineraries").delete().eq("trip_id", trip_id).eq("day_number", 9999).execute()
            self.db.table("itineraries").insert({
                "trip_id": trip_id,
                "day_number": 9999,
                "activities": pref_data,
            }).execute()
        except Exception:
            pass

        # Return refreshed trip
        refreshed = self.get_trip_by_id(trip_id, user_id=user_id)
        if existing["has_itinerary"] and (destination_changed or dates_changed):
            refreshed["itinerary_regeneration_recommended"] = True

        return refreshed

    # ── Delete Trip ────────────────────────────────────────────────────────────

    def delete_trip(self, trip_id: str, user_id: str | None = None) -> dict:
        """
        Safely delete a trip and its associated daily itineraries.
        """
        # Ensure trip exists first
        self.get_trip_by_id(trip_id, user_id=user_id)

        try:
            # 1. Delete associated daily itineraries
            self.db.table("itineraries").delete().eq("trip_id", trip_id).execute()
            # 2. Delete trip record
            self.db.table("trips").delete().eq("id", trip_id).execute()
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete trip: {exc}",
            ) from exc

        return {
            "success": True,
            "message": f"Trip '{trip_id}' and all associated itineraries were successfully deleted.",
            "deleted_trip_id": str(trip_id),
        }
