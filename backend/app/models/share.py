"""
backend/app/models/share.py

Pydantic v2 data models for Trip Sharing, Export (PDF & JSON), and Summary generation.
Ensures zero leakage of sensitive user PII (user_id, email) in public-facing share endpoints.
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, ConfigDict, Field
from app.models.itinerary import DayItinerary


class TripShareResponse(BaseModel):
    """
    Response returned when a shareable link is generated or retrieved for a trip.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    trip_id: str = Field(..., description="ID of the trip being shared")
    share_token: str = Field(..., description="Secure, unpredictable share token")
    share_url: str = Field(..., description="Full frontend shareable URL")
    is_active: bool = Field(default=True, description="Whether the share link is active")
    created_at: str | None = Field(default=None, description="ISO timestamp of share link creation")


class TripRevokeResponse(BaseModel):
    """
    Response returned when trip sharing is disabled/revoked.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    trip_id: str = Field(..., description="ID of the trip whose share was revoked")
    success: bool = Field(default=True, description="Whether revocation succeeded")
    message: str = Field(..., description="Confirmation message")


class SharedTripPublicResponse(BaseModel):
    """
    Public, read-only view of a trip and its itinerary.
    Strictly omits user_id, user email, and internal foreign keys for security.
    """

    model_config = ConfigDict(str_strip_whitespace=True, extra="allow")

    share_token: str = Field(..., description="Active share token")
    trip_id: str = Field(..., description="Public reference ID of the trip")
    destination: str = Field(..., description="Trip destination")
    start_date: str = Field(..., description="Trip start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="Trip end date (YYYY-MM-DD)")
    duration_days: int = Field(..., description="Total trip duration in days")
    total_budget: float = Field(..., description="Trip budget in USD")
    travel_style: str = Field(default="cultural", description="Travel style")
    travel_pace: str = Field(default="moderate", description="Travel pace")
    primary_vibe: str | None = Field(default=None, description="Primary travel vibe")
    secondary_vibes: list[str] = Field(default_factory=list, description="Secondary travel vibes")
    trip_summary: str = Field(..., description="Overall trip overview summary")
    total_estimated_cost: str = Field(default="", description="Estimated cost breakdown summary")
    packing_and_prep_tips: list[str] = Field(default_factory=list, description="Preparation advice")
    days: list[DayItinerary] = Field(default_factory=list, description="Day-by-day itineraries")
    route_optimized: bool = Field(default=False, description="Whether routes were optimized")
    optimization_summary: str | None = Field(default=None, description="Route optimization summary")
    is_shared: bool = Field(default=True, description="Always true for public view")
    created_at: str | None = Field(default=None, description="Creation timestamp")


class TripSummaryResponse(BaseModel):
    """
    Structured summary and clipboard-ready plain text representation of a trip.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    trip_id: str = Field(..., description="Trip ID")
    destination: str = Field(..., description="Destination")
    start_date: str = Field(..., description="Start date")
    end_date: str = Field(..., description="End date")
    duration_days: int = Field(..., description="Total days")
    total_budget: float = Field(..., description="Budget in USD")
    primary_vibe: str | None = Field(default=None, description="Primary vibe")
    secondary_vibes: list[str] = Field(default_factory=list, description="Secondary vibes")
    summary_text: str = Field(..., description="Formatted clipboard-ready text summary of the itinerary")
    daily_highlights: list[dict[str, Any]] = Field(default_factory=list, description="Day-by-day key highlights")

