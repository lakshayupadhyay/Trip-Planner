"""
backend/app/services/itinerary_service.py

Modular Itinerary Generation Service.
Generates comprehensive day-wise travel itineraries using pluggable LLM providers
(Gemini, Groq) and stores generated daily plans into Supabase.
"""

from __future__ import annotations

import json
import re
import uuid
from typing import Any
from fastapi import HTTPException

from app.models.itinerary import (
    DayItinerary,
    ItineraryGenerateRequest,
    ItineraryResponse,
)
from app.services.prompt_service import build_structured_itinerary_prompt
from app.services.providers import LLMProvider, get_llm_provider


def _clean_json_text(text: str) -> str:
    """Extract and clean raw JSON from LLM output, stripping markdown code fences."""
    cleaned = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned, re.IGNORECASE)
    if match:
        cleaned = match.group(1).strip()
    return cleaned


class ItineraryService:
    """
    Business logic service for generating and storing AI travel itineraries.
    Supports dependency injection of custom LLMProvider and database client for tests.
    """

    def __init__(
        self,
        provider: LLMProvider | None = None,
        db: Any | None = None,
    ) -> None:
        self._provider = provider
        self._db = db

    @property
    def db(self) -> Any:
        """Lazily load the shared Supabase client."""
        if self._db is not None:
            return self._db
        try:
            from app.utils.supabase_client import supabase
            return supabase
        except Exception:
            return None

    def _get_provider(self, provider_name: str | None = None) -> LLMProvider:
        """Resolve LLM provider, preferring injected provider if present."""
        if self._provider is not None:
            return self._provider
        return get_llm_provider(provider_type=provider_name)

    async def generate_itinerary(
        self, request: ItineraryGenerateRequest
    ) -> ItineraryResponse:
        """
        Generate a comprehensive day-by-day itinerary using configured AI provider
        and persist daily schedules into the Supabase 'itineraries' table.
        """
        provider = self._get_provider(request.provider)

        # 1. Build structured prompt
        prompt = build_structured_itinerary_prompt(
            destination=request.destination,
            start_date=request.start_date,
            end_date=request.end_date,
            travel_style=request.travel_style,
            travel_interests=request.travel_interests,
            num_travelers=request.num_travelers,
            budget=request.budget,
            travel_pace=request.travel_pace,
            dietary_preferences=request.dietary_preferences,
            additional_requirements=request.additional_requirements,
            primary_vibe=getattr(request, "primary_vibe", None),
            secondary_vibes=getattr(request, "secondary_vibes", []),
        )

        system_prompt = (
            "You are an expert, meticulous travel planner. "
            "You must generate an inspiring, highly practical, day-by-day itinerary "
            "strictly adhering to the specified user preferences, budget, pace, and dietary constraints. "
            "Return valid JSON matching the exact schema provided."
        )

        # 2. Invoke AI Provider asynchronously
        try:
            raw_output = await provider.generate(prompt=prompt, system_prompt=system_prompt)
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to generate itinerary with provider '{provider.name}': {exc}",
            ) from exc

        # 3. Clean and parse JSON response
        cleaned_json = _clean_json_text(raw_output)
        try:
            parsed_data = json.loads(cleaned_json)
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"AI model did not return valid JSON. Error: {exc}. Output preview: {cleaned_json[:200]}",
            ) from exc

        # Ensure top-level fields match request if model omitted or altered them
        if "destination" not in parsed_data or not parsed_data["destination"]:
            parsed_data["destination"] = request.destination
        if "start_date" not in parsed_data or not parsed_data["start_date"]:
            parsed_data["start_date"] = str(request.start_date)
        if "end_date" not in parsed_data or not parsed_data["end_date"]:
            parsed_data["end_date"] = str(request.end_date)
        if "total_budget" not in parsed_data:
            parsed_data["total_budget"] = request.budget
        if "travel_style" not in parsed_data:
            parsed_data["travel_style"] = request.travel_style
        if "travel_pace" not in parsed_data:
            parsed_data["travel_pace"] = request.travel_pace
        if "primary_vibe" not in parsed_data or not parsed_data["primary_vibe"]:
            parsed_data["primary_vibe"] = getattr(request, "primary_vibe", None)
        if "secondary_vibes" not in parsed_data or not parsed_data["secondary_vibes"]:
            parsed_data["secondary_vibes"] = getattr(request, "secondary_vibes", [])
        if "duration_days" not in parsed_data or not parsed_data["duration_days"]:
            from app.services.prompt_service import calculate_trip_duration
            parsed_data["duration_days"] = calculate_trip_duration(request.start_date, request.end_date)["days"]

        # Validate into ItineraryResponse
        try:
            itinerary = ItineraryResponse(**parsed_data)
        except Exception as val_err:
            raise HTTPException(
                status_code=502,
                detail=f"Structured itinerary validation failed: {val_err}",
            ) from val_err

        itinerary.provider_used = provider.name

        # 4. Apply Activity 4.2: Route & Time Optimization
        if getattr(request, "optimize_route", True):
            try:
                from app.services.route_optimization_service import RouteOptimizationService
                route_optimizer = RouteOptimizationService()
                itinerary = route_optimizer.optimize_itinerary(
                    itinerary=itinerary,
                    travel_pace=request.travel_pace,
                )
            except Exception:
                # Optimization failure must never break overall itinerary generation
                pass

        # 5. Persist to Supabase if database connection is available
        resolved_trip_id = self._save_to_supabase(itinerary, request)
        if resolved_trip_id:
            itinerary.trip_id = str(resolved_trip_id)

        return itinerary

    def _save_to_supabase(
        self, itinerary: ItineraryResponse, request: ItineraryGenerateRequest
    ) -> str | None:
        """
        Store generated daily itinerary rows in Supabase 'itineraries' table:
        columns: trip_id (uuid), day_number (int), activities (jsonb).
        """
        if self.db is None:
            return None

        trip_id = request.trip_id

        # If no trip_id provided, attempt to look up or create a trip record
        if not trip_id:
            try:
                from app.services.trip_service import TripService
                trip_service = TripService(db=self.db)
                from app.models.trip import TripCreateRequest

                trip_create = TripCreateRequest(
                    destination=request.destination,
                    start_date=request.start_date,
                    end_date=request.end_date,
                    num_travelers=request.num_travelers,
                    budget=request.budget,
                    travel_style=request.travel_style,
                    travel_interests=request.travel_interests,
                    dietary_preferences=request.dietary_preferences,
                    travel_pace=request.travel_pace,
                    additional_requirements=request.additional_requirements,
                )
                created_trip = trip_service.create_trip(trip_create)
                trip_id = created_trip.get("id")
            except Exception:
                # If trip creation fails, fallback to new UUID
                trip_id = str(uuid.uuid4())

        if not trip_id:
            return None

        # Clean existing days for this trip if updating
        try:
            self.db.table("itineraries").delete().eq("trip_id", str(trip_id)).execute()
        except Exception:
            pass

        # Insert each day into itineraries table with metadata on Day 1
        try:
            for day in itinerary.days:
                day_payload = day.model_dump()
                if day.day_number == 1:
                    day_payload["trip_metadata"] = {
                        "primary_vibe": itinerary.primary_vibe,
                        "secondary_vibes": itinerary.secondary_vibes,
                        "travel_style": itinerary.travel_style,
                        "travel_pace": itinerary.travel_pace,
                        "trip_summary": itinerary.trip_summary,
                        "total_estimated_cost": itinerary.total_estimated_cost,
                        "packing_and_prep_tips": itinerary.packing_and_prep_tips,
                        "optimization_summary": itinerary.optimization_summary,
                        "route_optimized": itinerary.route_optimized,
                        "provider_used": itinerary.provider_used,
                        "total_budget": itinerary.total_budget,
                        "destination": itinerary.destination,
                    }
                row_payload = {
                    "trip_id": str(trip_id),
                    "day_number": day.day_number,
                    "activities": day_payload,
                }
                self.db.table("itineraries").insert(row_payload).execute()
        except Exception as exc:
            # Database storage failures shouldn't crash the generated response
            pass

        return str(trip_id)

    def get_itinerary_by_trip_id(self, trip_id: str) -> ItineraryResponse:
        """
        Retrieve saved itinerary for a trip from Supabase without invoking AI generation.
        Restores full daily itinerary, route optimization data, schedules, transit, and vibes.
        """
        if self.db is None:
            raise HTTPException(
                status_code=503,
                detail="Database client is not available.",
            )

        try:
            itinerary_rows = (
                self.db.table("itineraries")
                .select("*")
                .eq("trip_id", str(trip_id))
                .lt("day_number", 900)
                .order("day_number", desc=False)
                .execute()
            )
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to query saved itinerary from database: {exc}",
            ) from exc

        if not itinerary_rows.data:
            raise HTTPException(
                status_code=404,
                detail=f"No saved itinerary found for trip '{trip_id}'.",
            )

        # Retrieve trip details from trips table if available
        trip_record = None
        try:
            trip_res = (
                self.db.table("trips")
                .select("*")
                .eq("id", str(trip_id))
                .limit(1)
                .execute()
            )
            if trip_res.data:
                trip_record = trip_res.data[0]
        except Exception:
            pass

        # Reconstruct DayItinerary objects
        days: list[DayItinerary] = []
        trip_metadata: dict[str, Any] = {}

        for row in itinerary_rows.data:
            act_data = row.get("activities") or {}
            if "trip_metadata" in act_data and not trip_metadata:
                trip_metadata = act_data.get("trip_metadata") or {}
            try:
                days.append(DayItinerary(**act_data))
            except Exception as err:
                raise HTTPException(
                    status_code=502,
                    detail=f"Failed to deserialize saved day itinerary {row.get('day_number')}: {err}",
                ) from err

        destination = (
            (trip_record.get("destination") if trip_record else None)
            or trip_metadata.get("destination")
            or (days[0].morning_activity.location if days and days[0].morning_activity else "Saved Destination")
        )
        start_date = (
            (trip_record.get("start_date") if trip_record else None)
            or (days[0].date if days and days[0].date else "2027-01-01")
        )
        end_date = (
            (trip_record.get("end_date") if trip_record else None)
            or (days[-1].date if days and days[-1].date else start_date)
        )
        total_budget = (
            float(trip_record.get("total_budget") or 0.0) if trip_record
            else float(trip_metadata.get("total_budget") or 2000.0)
        )
        travel_style = trip_metadata.get("travel_style") or "cultural"
        travel_pace = trip_metadata.get("travel_pace") or "moderate"
        primary_vibe = trip_metadata.get("primary_vibe")
        secondary_vibes = trip_metadata.get("secondary_vibes") or []
        trip_summary = trip_metadata.get("trip_summary") or f"Personalized {len(days)}-day itinerary for {destination}."
        total_estimated_cost = trip_metadata.get("total_estimated_cost") or "Balanced across sights, dining and transit"
        packing_tips = trip_metadata.get("packing_and_prep_tips") or []
        provider_used = trip_metadata.get("provider_used") or "gemini"
        route_optimized = trip_metadata.get("route_optimized", True)
        optimization_summary = trip_metadata.get("optimization_summary")

        return ItineraryResponse(
            trip_id=str(trip_id),
            destination=destination,
            start_date=str(start_date),
            end_date=str(end_date),
            duration_days=len(days),
            total_budget=total_budget,
            travel_style=travel_style,
            travel_pace=travel_pace,
            days=days,
            trip_summary=trip_summary,
            total_estimated_cost=total_estimated_cost,
            packing_and_prep_tips=packing_tips,
            provider_used=provider_used,
            route_optimized=route_optimized,
            optimization_summary=optimization_summary,
            primary_vibe=primary_vibe,
            secondary_vibes=secondary_vibes,
        )

