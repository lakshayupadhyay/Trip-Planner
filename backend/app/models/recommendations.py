"""
backend/app/models/recommendations.py

Pydantic schemas for AI-powered destination and activity recommendations.
"""

from __future__ import annotations

from datetime import date
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

RecommendationCategory = Literal[
    "Attractions",
    "Activities",
    "Dining",
    "Cultural Experiences",
    "Nature and Adventure",
]


# ── Activity Recommendation Models ──────────────────────────────────────────

class ActivityRecommendation(BaseModel):
    """Individual activity, dining, or attraction recommendation."""
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., description="Name of the attraction, venue, or activity")
    category: str = Field(..., description="Category (Attractions, Activities, Dining, Cultural Experiences, Nature and Adventure)")
    description: str = Field(..., description="Rich description of the experience")
    reason_for_recommendation: str = Field(..., description="Why this matches the user's specific preferences")
    estimated_cost: str = Field(default="Estimated cost varies", description="Estimated cost (e.g. '~$20 USD / person' or 'Free')")
    suggested_duration: str = Field(default="2-3 hours", description="Suggested time to spend")
    best_time_to_visit: str = Field(default="Morning or early afternoon", description="Optimal time of day or conditions")
    location: str = Field(default="Central area", description="Neighborhood or area within destination")
    practical_tips: str = Field(default="Check current opening hours before visiting", description="Actionable visitor tips")


class ActivityRecommendationRequest(BaseModel):
    """Request payload for fetching activity & dining recommendations for a specific destination."""
    model_config = ConfigDict(str_strip_whitespace=True)

    destination: str = Field(..., min_length=2, max_length=200, description="Target destination city or region")
    start_date: date | None = Field(default=None, description="Start date of travel")
    end_date: date | None = Field(default=None, description="End date of travel")
    budget: float | None = Field(default=None, gt=0, description="Total budget in USD")
    num_travelers: int = Field(default=1, ge=1, le=20, description="Number of travelers")
    travel_style: str = Field(default="cultural", description="Travel style (cultural, adventure, relaxation, etc.)")
    travel_interests: list[str] = Field(default_factory=list, description="Specific travel interests")
    travel_pace: str = Field(default="moderate", description="Travel pace (slow, moderate, fast)")
    dietary_preferences: list[str] = Field(default_factory=list, description="Dietary restrictions or preferences")
    additional_requirements: str | None = Field(default=None, max_length=500, description="Custom notes or accessibility needs")


class ActivitiesRecommendationResponse(BaseModel):
    """Response containing activity and dining recommendations for a destination."""
    model_config = ConfigDict(str_strip_whitespace=True)

    destination: str
    recommendations: list[ActivityRecommendation] = Field(default_factory=list)
    notes: str | None = None


# ── Destination Recommendation Models ───────────────────────────────────────

class DestinationRecommendation(BaseModel):
    """Suggested destination matching user preferences and budget."""
    model_config = ConfigDict(str_strip_whitespace=True)

    destination: str = Field(..., description="City and country name (e.g. 'Kyoto, Japan')")
    country: str = Field(..., description="Country name")
    description: str = Field(..., description="Overview of the destination and why it is appealing")
    why_it_matches: str = Field(..., description="How this destination aligns with user style, budget, and interests")
    estimated_budget_range: str = Field(..., description="Typical budget range (e.g. '$1,200 - $1,800 USD')")
    best_time_to_visit: str = Field(..., description="Peak or recommended season to travel")
    highlight_attractions: list[str] = Field(default_factory=list, description="Top 3 to 5 highlight sights or experiences")
    practical_tips: str | None = Field(default=None, description="Key advice on transit, safety, or currency")


class DestinationRecommendationRequest(BaseModel):
    """Request payload when the user has not chosen a destination yet."""
    model_config = ConfigDict(str_strip_whitespace=True)

    preferred_region: str | None = Field(default=None, description="Optional continent or region (e.g. 'Europe', 'Asia')")
    start_date: date | None = Field(default=None, description="Start date of travel")
    end_date: date | None = Field(default=None, description="End date of travel")
    budget: float | None = Field(default=None, gt=0, description="Total budget in USD")
    num_travelers: int = Field(default=1, ge=1, le=20, description="Number of travelers")
    travel_style: str = Field(default="cultural", description="Travel style")
    travel_interests: list[str] = Field(default_factory=list, description="Specific travel interests")
    travel_pace: str = Field(default="moderate", description="Travel pace")
    dietary_preferences: list[str] = Field(default_factory=list, description="Dietary preferences")
    additional_requirements: str | None = Field(default=None, max_length=500, description="Custom requirements")


class DestinationsRecommendationResponse(BaseModel):
    """Response containing destination suggestions."""
    model_config = ConfigDict(str_strip_whitespace=True)

    recommendations: list[DestinationRecommendation] = Field(default_factory=list)
    notes: str | None = None

