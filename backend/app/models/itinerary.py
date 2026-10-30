"""
backend/app/models/itinerary.py

Pydantic v2 models for structured daily itinerary generation,
day-wise plans, activities, transport, dining, and daily budgets.
"""

from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

from app.models.trip import TravelPreferences


# ── Activity 3.2 Backward Compatibility ────────────────────────────────────────

class PromptPreviewResponse(BaseModel):
    """
    Response schema for POST /api/v1/itinerary/prompt-preview.
    Maintained for backward compatibility with Activity 3.2.
    """

    model_config = ConfigDict(str_strip_whitespace=True, extra="allow")

    destination: str = Field(
        ...,
        description="Target travel destination",
    )
    duration_days: int = Field(
        ...,
        description="Total trip duration in days (inclusive)",
    )
    prompt: str = Field(
        ...,
        description="Structured natural-language prompt generated for the AI model",
    )


# ── Epic 4 Activity 4.1 & 4.2: Structured Itinerary & Route Optimization Models ─

class ActivitySchedule(BaseModel):
    """Calculated start and end times for scheduled activities."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="allow")

    start_time: str = Field(
        ...,
        description="Scheduled start time formatted e.g. '09:00 AM'",
    )
    end_time: str = Field(
        ...,
        description="Scheduled end time formatted e.g. '11:00 AM'",
    )
    duration_minutes: int = Field(
        ...,
        ge=1,
        description="Duration of activity in minutes",
    )


class RouteLeg(BaseModel):
    """
    Estimated travel leg connecting two consecutive stops/activities in a day.
    Explicitly marked as an estimate with calculation methodology.
    """

    model_config = ConfigDict(str_strip_whitespace=True, extra="allow")

    from_name: str = Field(
        ...,
        description="Origin stop name",
    )
    to_name: str = Field(
        ...,
        description="Destination stop name",
    )
    from_location: str | None = Field(
        default=None,
        description="Origin neighborhood, district, or address",
    )
    to_location: str | None = Field(
        default=None,
        description="Destination neighborhood, district, or address",
    )
    distance_km: float = Field(
        ...,
        ge=0.0,
        description="Estimated road distance in kilometers (not straight-line)",
    )
    duration_minutes: int = Field(
        ...,
        ge=0,
        description="Estimated transit time in minutes",
    )
    recommended_mode: Literal["walking", "transit", "driving"] | str = Field(
        default="transit",
        description="Recommended transit mode based on distance and city characteristics",
    )
    distance_display: str = Field(
        ...,
        description="User-facing distance string (e.g. 'Estimated ~2.4 km road distance')",
    )
    duration_display: str = Field(
        ...,
        description="User-facing duration string (e.g. 'Estimated ~18 mins transit')",
    )
    is_estimated: bool = Field(
        default=True,
        description="Always True to identify estimated rather than live GPS-tracked distance",
    )
    estimation_method: str = Field(
        default="haversine_circuity_estimate",
        description="Algorithm/method used to compute estimate (e.g. haversine_circuity_estimate, district_heuristic)",
    )
    from_coordinates: dict[str, float] | None = Field(
        default=None,
        description="Latitude and longitude of origin {'lat': ..., 'lng': ...}",
    )
    to_coordinates: dict[str, float] | None = Field(
        default=None,
        description="Latitude and longitude of destination {'lat': ..., 'lng': ...}",
    )
    directions_summary: str | None = Field(
        default=None,
        description="Transit advice or directions summary",
    )


class Activity(BaseModel):
    """Individual attraction, experience, or activity."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="allow")

    time_slot: Literal["morning", "afternoon", "evening"] | str = Field(
        ...,
        description="Time slot of activity: morning, afternoon, or evening",
    )
    name: str = Field(
        ...,
        description="Name of the attraction, venue, or experience",
    )
    description: str = Field(
        ...,
        description="Engaging and detailed description of the activity",
    )
    location: str | None = Field(
        default=None,
        description="District, neighborhood, or address",
    )
    suggested_duration: str = Field(
        ...,
        description="Estimated duration (e.g., '2 hours', '90 mins')",
    )
    estimated_cost: str = Field(
        ...,
        description="Estimated cost string (e.g., '$25 USD / person', 'Free')",
    )
    best_time_to_visit: str | None = Field(
        default=None,
        description="Recommended time of arrival",
    )
    booking_required: bool = Field(
        default=False,
        description="Whether advance booking or ticket reservation is required",
    )
    practical_tips: str | None = Field(
        default=None,
        description="Helpful tips on lines, photography, dress code, etc.",
    )
    latitude: float | None = Field(
        default=None,
        description="Latitude coordinate if known",
    )
    longitude: float | None = Field(
        default=None,
        description="Longitude coordinate if known",
    )
    schedule: ActivitySchedule | None = Field(
        default=None,
        description="Optimized scheduled arrival and departure time window",
    )
    opening_hours: str | None = Field(
        default=None,
        description="Operating hours e.g. '09:00 - 17:00' if known",
    )


class DiningRecommendation(BaseModel):
    """Restaurant or food recommendation honoring dietary preferences."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="allow")

    meal_type: Literal["Lunch", "Dinner", "Breakfast"] | str = Field(
        ...,
        description="Meal type (Lunch or Dinner)",
    )
    name: str = Field(
        ...,
        description="Restaurant, bistro, or food market name",
    )
    cuisine: str = Field(
        ...,
        description="Type of cuisine or regional specialty",
    )
    description: str = Field(
        ...,
        description="Description of the dining experience and atmosphere",
    )
    estimated_cost: str = Field(
        ...,
        description="Estimated cost per person (e.g., '$20 - $35 USD')",
    )
    dietary_compliance: str | None = Field(
        default=None,
        description="How it accommodates specified dietary preferences (e.g. vegetarian options)",
    )
    location: str | None = Field(
        default=None,
        description="Neighborhood or district",
    )
    practical_tips: str | None = Field(
        default=None,
        description="Reservation advice or must-order dish",
    )
    latitude: float | None = Field(
        default=None,
        description="Latitude coordinate if known",
    )
    longitude: float | None = Field(
        default=None,
        description="Longitude coordinate if known",
    )
    schedule: ActivitySchedule | None = Field(
        default=None,
        description="Optimized scheduled meal time window",
    )
    opening_hours: str | None = Field(
        default=None,
        description="Meal hours e.g. '11:30 - 14:30' if known",
    )


class Transportation(BaseModel):
    """Local transportation logistics between sights."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="allow")

    mode: str = Field(
        ...,
        description="Recommended transit mode (e.g., 'Metro Line 1', 'Walking', 'Bus 42')",
    )
    estimated_time: str = Field(
        ...,
        description="Estimated transit time (e.g., '20 mins')",
    )
    estimated_cost: str = Field(
        ...,
        description="Estimated transit cost (e.g., '$2.50 USD', 'Free (walking)')",
    )
    route_details: str | None = Field(
        default=None,
        description="Specific route directions or transfer stops",
    )
    tips: str | None = Field(
        default=None,
        description="Transit advice (e.g., buy a 24h metro pass)",
    )


class DailyBudget(BaseModel):
    """Breakdown of estimated costs for a single travel day."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="allow")

    activities_cost: str = Field(
        ...,
        description="Estimated spend on attractions and entry tickets",
    )
    dining_cost: str = Field(
        ...,
        description="Estimated spend on meals, drinks, and snacks",
    )
    transportation_cost: str = Field(
        ...,
        description="Estimated spend on local transit",
    )
    total_daily_estimated: str = Field(
        ...,
        description="Total estimated expenditure for the day",
    )
    currency: str = Field(
        default="USD",
        description="Currency symbol or code",
    )


class DayItinerary(BaseModel):
    """Complete day plan with morning, afternoon, evening activities and logistics."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="allow")

    day_number: int = Field(
        ...,
        ge=1,
        description="Day sequence number (1, 2, ...)",
    )
    date: str | None = Field(
        default=None,
        description="Calendar date for this day (YYYY-MM-DD)",
    )
    theme: str = Field(
        ...,
        description="Theme or focus area of the day (e.g., 'Historic Old Town & Imperial Shrines')",
    )
    morning_activity: Activity = Field(
        ...,
        description="Primary morning activity or sightseeing",
    )
    lunch: DiningRecommendation | None = Field(
        default=None,
        description="Recommended lunch spot",
    )
    afternoon_activity: Activity = Field(
        ...,
        description="Afternoon attraction or cultural experience",
    )
    dinner: DiningRecommendation | None = Field(
        default=None,
        description="Recommended dinner dining venue",
    )
    evening_activity: Activity | None = Field(
        default=None,
        description="Evening stroll, viewpoint, or cultural show",
    )
    transportation: Transportation = Field(
        ...,
        description="Daily local transportation logistics",
    )
    daily_budget: DailyBudget = Field(
        ...,
        description="Estimated financial breakdown for the day",
    )
    practical_tips: str = Field(
        ...,
        description="Actionable daily tip (ticket booking, opening hours, local customs)",
    )
    # ── Activity 4.2 Route & Time Optimization Fields ──
    route_legs: list[RouteLeg] = Field(
        default_factory=list,
        description="Ordered sequence of transit legs connecting consecutive stops",
    )
    optimized_sequence: list[str] = Field(
        default_factory=list,
        description="Optimized geographical order of stops for the day",
    )
    total_travel_distance_km: float | None = Field(
        default=None,
        ge=0.0,
        description="Total estimated travel distance across all legs in km",
    )
    total_travel_time_minutes: int | None = Field(
        default=None,
        ge=0,
        description="Total estimated transit duration across all legs in minutes",
    )
    route_optimization_status: str | None = Field(
        default=None,
        description="Optimization status flag e.g. 'optimized', 'heuristic', 'fallback'",
    )


class ItineraryResponse(BaseModel):
    """Full multi-day itinerary response returned by API and persisted in database."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="allow")

    trip_id: str | None = Field(
        default=None,
        description="Associated Supabase trip UUID if saved",
    )
    destination: str = Field(
        ...,
        description="Destination name",
    )
    start_date: str = Field(
        ...,
        description="Start date (YYYY-MM-DD)",
    )
    end_date: str = Field(
        ...,
        description="End date (YYYY-MM-DD)",
    )
    duration_days: int = Field(
        ...,
        ge=1,
        description="Total duration in days",
    )
    total_budget: float = Field(
        ...,
        description="Traveler total budget in USD",
    )
    travel_style: str = Field(
        ...,
        description="Travel style used for personalization",
    )
    travel_pace: str = Field(
        ...,
        description="Travel pace used for activity density",
    )
    days: list[DayItinerary] = Field(
        ...,
        min_length=1,
        description="Chronological list of daily plans",
    )
    trip_summary: str = Field(
        ...,
        description="Comprehensive executive summary of the customized itinerary",
    )
    total_estimated_cost: str = Field(
        ...,
        description="Summary of overall estimated trip expenditure vs budget",
    )
    packing_and_prep_tips: list[str] = Field(
        default_factory=list,
        description="Practical destination prep, packing, and seasonal guidance",
    )
    provider_used: str | None = Field(
        default=None,
        description="AI Model provider utilized (e.g. 'gemini', 'groq')",
    )
    # ── Activity 4.2 Route & Time Optimization Fields ──
    route_optimized: bool = Field(
        default=False,
        description="Whether route and time optimization has been applied",
    )
    optimization_summary: str | None = Field(
        default=None,
        description="Summary of route sequence and time optimization results",
    )
    # ── Activity 4.3 Vibe-Based Personalization Fields ──
    primary_vibe: str | None = Field(
        default=None,
        description="Primary travel vibe (e.g. Romantic, Adventure, Luxury, Relaxed, Budget, Cultural, Family, Nightlife, Nature & Exploration, Food & Culinary)",
    )
    secondary_vibes: list[str] = Field(
        default_factory=list,
        description="Secondary travel vibes blended into the itinerary",
    )


class ItineraryGenerateRequest(TravelPreferences):
    """
    Request body for POST /api/v1/itinerary/generate.
    Reuses all validation rules from TravelPreferences and optionally accepts
    an existing trip_id, provider override, and route optimization flag.
    """

    trip_id: str | None = Field(
        default=None,
        description="Optional existing Supabase trip UUID to link and store itinerary",
    )
    provider: str | None = Field(
        default=None,
        description="Optional provider override ('gemini' or 'groq')",
    )
    optimize_route: bool = Field(
        default=True,
        description="Whether to run intelligent route & time optimization on the generated itinerary",
    )


class RouteOptimizationRequest(BaseModel):
    """
    Request body for POST /api/v1/itinerary/optimize-route.
    Accepts an existing ItineraryResponse and optionally overrides travel pace or preferred transit mode.
    """

    model_config = ConfigDict(str_strip_whitespace=True, extra="allow")

    itinerary: ItineraryResponse = Field(
        ...,
        description="Full itinerary object to optimize",
    )
    travel_pace: str | None = Field(
        default=None,
        description="Optional pace override ('relaxed', 'moderate', 'fast')",
    )
    preferred_mode: Literal["walking", "transit", "driving"] | str | None = Field(
        default=None,
        description="Optional preferred transit mode",
    )


class DayOptimizationRequest(BaseModel):
    """
    Request body for optimizing a single travel day.
    """

    model_config = ConfigDict(str_strip_whitespace=True, extra="allow")

    destination: str = Field(
        ...,
        description="Destination city or region for geographic reference",
    )
    day: DayItinerary = Field(
        ...,
        description="Single day itinerary to optimize",
    )
    travel_pace: str = Field(
        default="moderate",
        description="Travel pace ('relaxed', 'moderate', 'fast')",
    )
    preferred_mode: str | None = Field(
        default=None,
        description="Optional preferred transit mode",
    )


# ── Activity 4.3: Conversational Itinerary Refinement Models ─────────────────

class ItineraryRefineRequest(BaseModel):
    """
    Request body for POST /api/v1/itinerary/refine.
    Accepts the full current itinerary, natural-language modification instruction,
    optional target day number, and optional provider override.
    """

    model_config = ConfigDict(str_strip_whitespace=True, extra="allow")

    itinerary: ItineraryResponse = Field(
        ...,
        description="Existing full ItineraryResponse object to be refined",
    )
    instruction: str = Field(
        ...,
        min_length=2,
        max_length=1000,
        description="Natural language instruction (e.g. 'Make Day 2 more adventurous', 'Reduce budget on Day 3')",
    )
    target_day_number: int | None = Field(
        default=None,
        ge=1,
        description="Optional specific day number to modify (if omitted, auto-detected from instruction)",
    )
    provider: str | None = Field(
        default=None,
        description="Optional AI provider override ('gemini' or 'groq')",
    )
    preferred_mode: str | None = Field(
        default=None,
        description="Optional transit mode preference",
    )


class DayRefineRequest(BaseModel):
    """
    Request body for POST /api/v1/itinerary/refine-day.
    Refines a single day with natural language instructions while preserving context.
    """

    model_config = ConfigDict(str_strip_whitespace=True, extra="allow")

    destination: str = Field(
        ...,
        description="Target destination name",
    )
    day: DayItinerary = Field(
        ...,
        description="Existing day itinerary object to modify",
    )
    instruction: str = Field(
        ...,
        min_length=2,
        max_length=1000,
        description="Natural language modification request for this day",
    )
    travel_pace: str = Field(
        default="moderate",
        description="Travel pace for schedule generation",
    )
    primary_vibe: str | None = Field(
        default=None,
        description="Primary travel vibe",
    )
    secondary_vibes: list[str] = Field(
        default_factory=list,
        description="Secondary travel vibes",
    )
    dietary_preferences: list[str] = Field(
        default_factory=list,
        description="Dietary requirements to maintain",
    )
    provider: str | None = Field(
        default=None,
        description="Optional AI provider override",
    )
    preferred_mode: str | None = Field(
        default=None,
        description="Optional preferred transit mode",
    )


class RefineResponse(BaseModel):
    """
    Response shape returned by POST /api/v1/itinerary/refine.
    Contains the updated full itinerary, explanation of modifications, and affected days.
    """

    model_config = ConfigDict(str_strip_whitespace=True, extra="allow")

    itinerary: ItineraryResponse = Field(
        ...,
        description="Updated full itinerary with refined activities, recalculated routes, and schedules",
    )
    explanation: str = Field(
        ...,
        description="Concise description of the modifications made according to the user instruction",
    )
    affected_day_numbers: list[int] = Field(
        ...,
        description="Day sequence numbers that were regenerated or modified",
    )
    scope: Literal["day", "full"] | str = Field(
        ...,
        description="Whether modification was scoped to a single day ('day') or full trip ('full')",
    )
