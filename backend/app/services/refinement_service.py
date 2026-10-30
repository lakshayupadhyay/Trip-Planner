"""
backend/app/services/refinement_service.py

Conversational Itinerary Refinement Service.
Processes natural language user modification instructions (e.g., 'Make Day 2 more adventurous',
'Make the entire trip more relaxing', 'Replace evening activities with nightlife'),
preserves existing trip context, regenerates only requested days when applicable,
re-runs Activity 4.2 Route & Time Optimization, and persists updates to Supabase.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any
from fastapi import HTTPException

from app.models.itinerary import (
    DayItinerary,
    DayRefineRequest,
    ItineraryRefineRequest,
    ItineraryResponse,
    RefineResponse,
)
from app.services.itinerary_service import _clean_json_text
from app.services.providers import LLMProvider, get_llm_provider
from app.services.route_optimization_service import RouteOptimizationService

logger = logging.getLogger(__name__)

ORDINAL_DAY_MAP = {
    "first day": 1,
    "day one": 1,
    "second day": 2,
    "day two": 2,
    "third day": 3,
    "day three": 3,
    "fourth day": 4,
    "day four": 4,
    "fifth day": 5,
    "day five": 5,
    "sixth day": 6,
    "day six": 6,
    "seventh day": 7,
    "day seven": 7,
}


def detect_target_day_number(instruction: str, max_days: int) -> int | None:
    """
    Detect if an instruction targets a specific day sequence number (1, 2, ...).
    Returns None if the instruction targets the entire trip.
    """
    cleaned = instruction.lower().strip()

    # Direct match: "day 2", "day #3", "day-1"
    match = re.search(r"\bday\s*#?\s*(\d+)\b", cleaned)
    if match:
        val = int(match.group(1))
        if 1 <= val <= max_days:
            return val

    # Ordinal match: "second day", "day two"
    for phrase, num in ORDINAL_DAY_MAP.items():
        if phrase in cleaned and num <= max_days:
            return num

    # "last day"
    if "last day" in cleaned and max_days >= 1:
        return max_days

    return None


class RefinementService:
    """
    Business logic service for conversational natural-language itinerary refinements.
    Supports dependency injection for LLM providers and database clients.
    """

    def __init__(
        self,
        provider: LLMProvider | None = None,
        route_optimizer: RouteOptimizationService | None = None,
        db: Any | None = None,
    ) -> None:
        self._provider = provider
        self._router = route_optimizer or RouteOptimizationService()
        self._db = db

    @property
    def db(self) -> Any:
        """Lazily load shared Supabase client."""
        if self._db is not None:
            return self._db
        try:
            from app.utils.supabase_client import supabase
            return supabase
        except Exception:
            return None

    def _get_provider(self, provider_name: str | None = None) -> LLMProvider:
        """Resolve LLM provider, preferring injected provider if set."""
        if self._provider is not None:
            return self._provider
        return get_llm_provider(provider_type=provider_name)

    async def refine_day(self, request: DayRefineRequest) -> DayItinerary:
        """
        Refine a single travel day according to user instructions while maintaining
        the destination, date, pace, dietary preferences, and financial scope.
        """
        provider = self._get_provider(request.provider)
        day = request.day
        destination = request.destination

        prompt = f"""# SINGLE-DAY ITINERARY REFINEMENT REQUEST

## 1. Destination & Context
- Destination: {destination}
- Day Number: {day.day_number}
- Date: {day.date or 'Scheduled Day'}
- Current Day Theme: {day.theme}
- Travel Pace: {request.travel_pace}
- Primary Vibe: {request.primary_vibe or 'Balanced'}
- Dietary Restrictions: {', '.join(request.dietary_preferences) if request.dietary_preferences else 'None specified'}

## 2. User Modification Request
"{request.instruction.strip()}"

## 3. Current Day Activities to Revise
- Morning: {day.morning_activity.name if day.morning_activity else 'None'} ({day.morning_activity.description if day.morning_activity else ''})
- Lunch: {day.lunch.name if day.lunch else 'None'} ({day.lunch.cuisine if day.lunch else ''})
- Afternoon: {day.afternoon_activity.name if day.afternoon_activity else 'None'} ({day.afternoon_activity.description if day.afternoon_activity else ''})
- Dinner: {day.dinner.name if day.dinner else 'None'} ({day.dinner.cuisine if day.dinner else ''})
- Evening: {day.evening_activity.name if day.evening_activity else 'None'} ({day.evening_activity.description if day.evening_activity else ''})

## 4. Instructions
Revise this day's plan to genuinely fulfill the user's modification request.
Preserve the day sequence number ({day.day_number}) and date ({day.date or ''}).
Select realistic venues and experiences in {destination} that reflect the requested modification.
Ensure reasonable estimated costs and practical travel tips.

Return ONLY a valid JSON object matching the DayItinerary schema below with no markdown commentary:

JSON SCHEMA:
{{
  "day_number": {day.day_number},
  "date": "{day.date or ''}",
  "theme": "Updated theme reflecting the new activities",
  "morning_activity": {{
    "time_slot": "morning",
    "name": "Attraction Name",
    "description": "Engaging description",
    "location": "Neighborhood",
    "suggested_duration": "2 hours",
    "estimated_cost": "Cost e.g. Free or $15 USD",
    "best_time_to_visit": "9:00 AM",
    "booking_required": false,
    "practical_tips": "Visitor tip"
  }},
  "lunch": {{
    "meal_type": "Lunch",
    "name": "Eatery Name",
    "cuisine": "Cuisine type",
    "description": "Atmosphere and food details",
    "estimated_cost": "~$20 USD / person",
    "dietary_compliance": "Compliance note",
    "location": "Neighborhood",
    "practical_tips": "Dining tip"
  }},
  "afternoon_activity": {{
    "time_slot": "afternoon",
    "name": "Afternoon Attraction Name",
    "description": "Detailed afternoon activity description",
    "location": "Neighborhood",
    "suggested_duration": "2 hours",
    "estimated_cost": "Cost e.g. Free or $20 USD",
    "best_time_to_visit": "2:00 PM",
    "booking_required": false,
    "practical_tips": "Afternoon tip"
  }},
  "dinner": {{
    "meal_type": "Dinner",
    "name": "Dinner Restaurant Name",
    "cuisine": "Cuisine type",
    "description": "Atmosphere and dinner dining details",
    "estimated_cost": "~$35 USD / person",
    "dietary_compliance": "Dietary compatibility note",
    "location": "Neighborhood",
    "practical_tips": "Advance booking advice"
  }},
  "evening_activity": {{
    "time_slot": "evening",
    "name": "Evening Experience Name",
    "description": "Description of evening activity",
    "location": "Neighborhood",
    "suggested_duration": "1.5 hours",
    "estimated_cost": "Cost e.g. Free",
    "best_time_to_visit": "7:30 PM",
    "booking_required": false,
    "practical_tips": "Evening tip"
  }},
  "transportation": {{
    "mode": "Metro / Walking",
    "estimated_time": "15-20 mins",
    "estimated_cost": "~$3.00 USD",
    "route_details": "Transit directions",
    "tips": "Transit tip"
  }},
  "daily_budget": {{
    "activities_cost": "Cost estimate",
    "dining_cost": "Cost estimate",
    "transportation_cost": "Cost estimate",
    "total_daily_estimated": "Total estimate",
    "currency": "USD"
  }},
  "practical_tips": "Daily actionable tip"
}}
"""
        system_prompt = (
            "You are an expert travel itinerary refinement specialist. "
            "Modify the specific travel day strictly fulfilling user instructions while maintaining "
            "practicality, pacing, and dietary compliance. Return valid JSON only."
        )

        try:
            raw_output = await provider.generate(prompt=prompt, system_prompt=system_prompt)
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Refinement with provider '{provider.name}' failed: {exc}",
            ) from exc

        cleaned = _clean_json_text(raw_output)
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"AI model did not return valid JSON for day refinement. Output preview: {cleaned[:150]}",
            ) from exc

        # Ensure day sequence number and date are preserved
        parsed["day_number"] = day.day_number
        if day.date and ("date" not in parsed or not parsed["date"]):
            parsed["date"] = day.date

        try:
            refined_day = DayItinerary(**parsed)
        except Exception as val_err:
            raise HTTPException(
                status_code=502,
                detail=f"Day itinerary validation failed during refinement: {val_err}",
            ) from val_err

        # Re-run Activity 4.2 Route & Time Optimization on the refined day
        refined_day = self._router.optimize_day(
            day=refined_day,
            destination=destination,
            travel_pace=request.travel_pace,
            preferred_mode=request.preferred_mode,
        )

        return refined_day

    async def refine_itinerary(self, request: ItineraryRefineRequest) -> RefineResponse:
        """
        Process a conversational modification request:
        1. Determines if the request is scoped to a single day or the entire trip.
        2. Preserves unaffected days and core trip context.
        3. Regenerates the targeted day(s).
        4. Re-runs Activity 4.2 Route Optimization on affected days.
        5. Persists modifications to Supabase.
        """
        itinerary = request.itinerary
        instruction = request.instruction.strip()
        provider = self._get_provider(request.provider)

        # 1. Determine Scope
        target_day_num = request.target_day_number or detect_target_day_number(
            instruction=instruction,
            max_days=itinerary.duration_days,
        )

        # Case A: Scoped to a specific single day
        if target_day_num is not None:
            target_idx = None
            for idx, d in enumerate(itinerary.days):
                if d.day_number == target_day_num:
                    target_idx = idx
                    break

            if target_idx is not None:
                day_req = DayRefineRequest(
                    destination=itinerary.destination,
                    day=itinerary.days[target_idx],
                    instruction=instruction,
                    travel_pace=itinerary.travel_pace,
                    primary_vibe=itinerary.primary_vibe,
                    secondary_vibes=itinerary.secondary_vibes,
                    dietary_preferences=[],
                    provider=request.provider,
                    preferred_mode=request.preferred_mode,
                )
                refined_day = await self.refine_day(day_req)

                # Replace modified day in itinerary
                itinerary.days[target_idx] = refined_day

                # Update summary and save to Supabase
                explanation = (
                    f"Refined Day {target_day_num} according to your instruction: '{instruction}'. "
                    f"All other {len(itinerary.days) - 1} days remain preserved."
                )
                itinerary.optimization_summary = (
                    f"Day {target_day_num} re-optimized (~{refined_day.total_travel_distance_km} km road transit, "
                    f"~{refined_day.total_travel_time_minutes} mins). Remaining days preserved."
                )

                self._save_day_to_supabase(itinerary.trip_id, refined_day)

                return RefineResponse(
                    itinerary=itinerary,
                    explanation=explanation,
                    affected_day_numbers=[target_day_num],
                    scope="day",
                )

        # Case B: Full Itinerary Refinement
        from app.services.prompt_service import build_structured_itinerary_prompt

        full_prompt = (
            build_structured_itinerary_prompt(
                destination=itinerary.destination,
                start_date=itinerary.start_date,
                end_date=itinerary.end_date,
                travel_style=itinerary.travel_style,
                travel_interests=[],
                num_travelers=1,
                budget=itinerary.total_budget,
                travel_pace=itinerary.travel_pace,
                primary_vibe=itinerary.primary_vibe,
                secondary_vibes=itinerary.secondary_vibes,
            )
            + f"\n\n# USER CONVERSATIONAL MODIFICATION DIRECTIVE\n"
            f"The traveler has instructed: '{instruction}'.\n"
            f"Apply this change across all days of the itinerary while preserving destination ({itinerary.destination}), "
            f"dates ({itinerary.start_date} to {itinerary.end_date}), and budget (${itinerary.total_budget})."
        )

        system_prompt = (
            "You are a master travel planner refining a complete multi-day itinerary. "
            "Incorporate user modifications while preserving destinations, dates, and realistic logistics. "
            "Return valid JSON only matching the schema."
        )

        try:
            raw_output = await provider.generate(prompt=full_prompt, system_prompt=system_prompt)
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Full itinerary refinement failed: {exc}",
            ) from exc

        cleaned = _clean_json_text(raw_output)
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"AI model did not return valid JSON for full refinement: {exc}",
            ) from exc

        # Keep primary trip metadata
        parsed["destination"] = itinerary.destination
        parsed["start_date"] = itinerary.start_date
        parsed["end_date"] = itinerary.end_date
        parsed["duration_days"] = itinerary.duration_days
        parsed["total_budget"] = itinerary.total_budget
        parsed["travel_style"] = itinerary.travel_style
        parsed["travel_pace"] = itinerary.travel_pace
        parsed["primary_vibe"] = itinerary.primary_vibe
        parsed["secondary_vibes"] = itinerary.secondary_vibes
        if itinerary.trip_id:
            parsed["trip_id"] = itinerary.trip_id

        try:
            refined_itinerary = ItineraryResponse(**parsed)
        except Exception as val_err:
            raise HTTPException(
                status_code=502,
                detail=f"Refined itinerary validation failed: {val_err}",
            ) from val_err

        # Re-run Route & Time Optimization across all days
        refined_itinerary = self._router.optimize_itinerary(
            itinerary=refined_itinerary,
            travel_pace=itinerary.travel_pace,
            preferred_mode=request.preferred_mode,
        )

        # Persist to Supabase if connected
        if refined_itinerary.trip_id and self.db is not None:
            try:
                for day in refined_itinerary.days:
                    self._save_day_to_supabase(refined_itinerary.trip_id, day)
            except Exception:
                pass

        affected_days = [d.day_number for d in refined_itinerary.days]
        explanation = (
            f"Updated all {len(affected_days)} days of your itinerary to reflect: '{instruction}'. "
            f"Routes and schedules have been completely recalculated."
        )

        return RefineResponse(
            itinerary=refined_itinerary,
            explanation=explanation,
            affected_day_numbers=affected_days,
            scope="full",
        )

    def _save_day_to_supabase(self, trip_id: str | None, day: DayItinerary) -> None:
        """Persist or update a single day in the Supabase 'itineraries' table."""
        if not trip_id or self.db is None:
            return

        try:
            # Upsert day into itineraries table
            payload = {
                "trip_id": str(trip_id),
                "day_number": day.day_number,
                "activities": day.model_dump(),
            }
            # Delete existing day row first then insert to avoid duplicate day records
            self.db.table("itineraries").delete().eq("trip_id", str(trip_id)).eq("day_number", day.day_number).execute()
            self.db.table("itineraries").insert(payload).execute()
        except Exception as exc:
            logger.debug("Failed to persist refined day to Supabase: %s", exc)

