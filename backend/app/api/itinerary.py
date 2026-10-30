"""
backend/app/api/itinerary.py

FastAPI router for itinerary planning and prompt preview endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.models.trip import TravelPreferences
from app.models.itinerary import (
    PromptPreviewResponse,
    ItineraryGenerateRequest,
    ItineraryResponse,
    RouteOptimizationRequest,
    DayOptimizationRequest,
    DayItinerary,
    ItineraryRefineRequest,
    DayRefineRequest,
    RefineResponse,
)
from app.services.prompt_service import (
    build_itinerary_prompt,
    calculate_trip_duration,
)
from app.services.itinerary_service import ItineraryService
from app.services.route_optimization_service import RouteOptimizationService
from app.services.refinement_service import RefinementService

router = APIRouter()
itinerary_service = ItineraryService()
route_optimization_service = RouteOptimizationService()
refinement_service = RefinementService()


@router.post(
    "/generate",
    response_model=ItineraryResponse,
    summary="Generate Full Daily Itinerary",
    description=(
        "Generates a complete, day-by-day travel itinerary personalized to user preferences, "
        "budget, pace, and dietary needs. Powered by pluggable AI providers (Gemini, Groq) "
        "and automatically stored in Supabase."
    ),
)
@router.post(
    "/generate/",
    response_model=ItineraryResponse,
    include_in_schema=False,
)
async def generate_itinerary(
    request: ItineraryGenerateRequest,
) -> ItineraryResponse:
    """
    Generate and persist a complete personalized daily itinerary.
    """
    return await itinerary_service.generate_itinerary(request)


@router.post(
    "/prompt-preview",
    response_model=PromptPreviewResponse,
    summary="Preview Structured Itinerary Prompt",
    description=(
        "Transforms validated user travel preferences into a structured, production-ready "
        "prompt for generative AI models (such as Google Gemini). Does not invoke paid AI APIs."
    ),
)
@router.post(
    "/prompt-preview/",
    response_model=PromptPreviewResponse,
    include_in_schema=False,
)
def preview_itinerary_prompt(preferences: TravelPreferences) -> PromptPreviewResponse:
    """
    Accept validated travel preferences and return the generated prompt along with trip duration.
    """
    duration = calculate_trip_duration(preferences.start_date, preferences.end_date)
    prompt = build_itinerary_prompt(
        destination=preferences.destination,
        start_date=preferences.start_date,
        end_date=preferences.end_date,
        travel_style=preferences.travel_style,
        travel_interests=preferences.travel_interests,
        num_travelers=preferences.num_travelers,
        budget=preferences.budget,
        travel_pace=preferences.travel_pace,
        dietary_preferences=preferences.dietary_preferences,
        additional_requirements=preferences.additional_requirements,
    )

    return PromptPreviewResponse(
        destination=preferences.destination,
        duration_days=duration["days"],
        prompt=prompt,
    )


@router.post(
    "/optimize-route",
    response_model=ItineraryResponse,
    summary="Optimize Route & Time Schedule for Full Itinerary",
    description=(
        "Optimizes activity sequences, minimizes transit distances and backtracking, "
        "computes realistic road distances using urban circuity factors, and establishes "
        "conflict-free schedules matching traveler pace."
    ),
)
@router.post(
    "/optimize-route/",
    response_model=ItineraryResponse,
    include_in_schema=False,
)
def optimize_itinerary_route(
    request: RouteOptimizationRequest,
) -> ItineraryResponse:
    """
    Optimize activity order and generate transit legs and schedules for an entire itinerary.
    """
    return route_optimization_service.optimize_itinerary(
        itinerary=request.itinerary,
        travel_pace=request.travel_pace,
        preferred_mode=request.preferred_mode,
    )


@router.post(
    "/optimize-day",
    response_model=DayItinerary,
    summary="Optimize Route & Schedule for a Single Travel Day",
    description=(
        "Calculates optimal activity sequence, estimated transit distances/times, and "
        "conflict-free timetable for a single day."
    ),
)
@router.post(
    "/optimize-day/",
    response_model=DayItinerary,
    include_in_schema=False,
)
def optimize_single_day(
    request: DayOptimizationRequest,
) -> DayItinerary:
    """
    Optimize a single travel day's route, transit legs, and schedule.
    """
    return route_optimization_service.optimize_day(
        day=request.day,
        destination=request.destination,
        travel_pace=request.travel_pace,
        preferred_mode=request.preferred_mode,
    )


# ── Activity 4.3: Conversational Refinement Endpoints ─────────────────────────

@router.post(
    "/refine",
    response_model=RefineResponse,
    summary="Refine Itinerary via Conversational Instruction",
    description=(
        "Processes natural-language modification instructions (e.g. 'Make Day 2 more adventurous', "
        "'Make the entire trip more relaxing'). Preserves unaffected days and core trip context, "
        "re-runs Activity 4.2 Route & Time Optimization, and returns structured updates."
    ),
)
@router.post(
    "/refine/",
    response_model=RefineResponse,
    include_in_schema=False,
)
async def refine_itinerary(
    request: ItineraryRefineRequest,
) -> RefineResponse:
    """
    Refine an existing itinerary using conversational natural language instructions.
    """
    return await refinement_service.refine_itinerary(request)


@router.post(
    "/refine-day",
    response_model=DayItinerary,
    summary="Refine a Single Travel Day via Conversational Instruction",
    description=(
        "Regenerates a single specific day's activities, dining, and transit according to "
        "natural language instructions while preserving the date, destination, pace, and dietary constraints."
    ),
)
@router.post(
    "/refine-day/",
    response_model=DayItinerary,
    include_in_schema=False,
)
async def refine_single_day(
    request: DayRefineRequest,
) -> DayItinerary:
    """
    Refine a single travel day using natural language instructions.
    """
    return await refinement_service.refine_day(request)


# ── Activity 5.1: Saved Itinerary Retrieval ────────────────────────────────────

@router.get(
    "/{trip_id}",
    response_model=ItineraryResponse,
    summary="Get Saved Itinerary for a Trip",
    description="Retrieve the complete saved daily itinerary for a trip without AI generation.",
)
@router.get(
    "/trip/{trip_id}",
    response_model=ItineraryResponse,
    include_in_schema=False,
)
def get_saved_itinerary(trip_id: str) -> ItineraryResponse:
    """
    Retrieve saved itinerary by trip_id from Supabase.
    """
    return itinerary_service.get_itinerary_by_trip_id(trip_id)


