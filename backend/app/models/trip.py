"""
backend/app/models/trip.py

Pydantic v2 data models for trip/travel-preferences requests and responses.

Models
------
TravelPreferences   – Embedded validator for travel input fields (reusable).
TripCreateRequest   – Request body for POST /api/v1/trips.
TripResponse        – Response shape returned from all trip endpoints.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Literal
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


# ── Allowed literals ───────────────────────────────────────────────────────────

TravelStyle = Literal["adventure", "cultural", "relaxation", "family", "luxury", "budget", "romantic", "leisure"]
TravelPace  = Literal["slow", "relaxed", "moderate", "fast"]


# ── Embedded preference validator (not used as a standalone request body) ─────

class TravelPreferences(BaseModel):
    """
    Shared validation rules for travel preference fields.

    Embedded directly into TripCreateRequest so that all validation
    logic lives in one place and is not duplicated.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    destination: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Name of the travel destination (at least 2 characters).",
    )
    start_date: date = Field(..., description="Trip start date (YYYY-MM-DD).")
    end_date:   date = Field(..., description="Trip end date (YYYY-MM-DD). Must be after start_date.")

    num_travelers: int = Field(
        default=1,
        ge=1,
        le=20,
        description="Number of travellers (1–20).",
    )
    budget: float = Field(
        ...,
        gt=0,
        description="Total trip budget in USD (must be positive).",
    )
    travel_style: TravelStyle = Field(
        ...,
        description="Overall style of travel.",
    )
    travel_interests: list[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="List of traveller interests (1–10 items).",
    )
    dietary_preferences: list[str] = Field(
        default_factory=list,
        description="Optional dietary preferences (e.g. vegetarian, halal).",
    )
    travel_pace: TravelPace = Field(
        default="moderate",
        description="Preferred pace of the trip.",
    )
    primary_vibe: str | None = Field(
        default=None,
        description="Primary travel vibe (e.g. Romantic, Adventure, Luxury, Relaxed, Budget, Cultural, Family, Nightlife, Nature & Exploration, Food & Culinary).",
    )
    secondary_vibes: list[str] = Field(
        default_factory=list,
        description="Optional secondary travel vibes to blend into the experience.",
    )
    additional_requirements: str | None = Field(
        default=None,
        max_length=500,
        description="Any extra requirements or notes (max 500 characters).",
    )

    # ── Field-level sanitisation & normalisation ───────────────────────────────

    @field_validator("travel_style", mode="before")
    @classmethod
    def normalize_travel_style(cls, v: Any) -> Any:
        """Allow case-insensitive input for travel_style."""
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("travel_pace", mode="before")
    @classmethod
    def normalize_travel_pace(cls, v: Any) -> Any:
        """Allow case-insensitive input for travel_pace."""
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("budget", mode="before")
    @classmethod
    def clean_budget(cls, v: Any) -> Any:
        """Strip currency signs or commas if passed as string."""
        if isinstance(v, str):
            cleaned = v.replace("$", "").replace(",", "").strip()
            return float(cleaned)
        return v

    @field_validator("travel_interests", mode="before")
    @classmethod
    def interests_must_not_be_empty_strings(cls, v: list) -> list:
        """Strip whitespace from each interest and reject blank entries."""
        if not isinstance(v, list):
            return v
        cleaned = [item.strip().lower() for item in v if isinstance(item, str)]
        if any(i == "" for i in cleaned):
            raise ValueError("Each travel interest must be a non-empty string.")
        return cleaned

    # ── Cross-field validation ─────────────────────────────────────────────────

    @model_validator(mode="after")
    def end_date_must_be_after_start_date(self) -> "TravelPreferences":
        """Ensure end_date is strictly after start_date."""
        if self.end_date <= self.start_date:
            raise ValueError(
                f"end_date ({self.end_date}) must be strictly after start_date ({self.start_date})."
            )
        return self


# ── Trip creation request ──────────────────────────────────────────────────────

class TripCreateRequest(TravelPreferences):
    """
    Request body for ``POST /api/v1/trips``.

    Inherits all TravelPreferences fields and validation.
    user_id is optional so that form submissions without explicit auth tokens
    succeed and are associated with the active or default demo user.
    """

    user_id: str | None = Field(
        default=None,
        description="UUID of the authenticated user (optional; auto-assigned if omitted).",
    )


# ── Trip update request ───────────────────────────────────────────────────────

class TripUpdateRequest(BaseModel):
    """
    Request body for updating an existing trip (PUT / PATCH /api/v1/trips/{trip_id}).
    All fields are optional; provided fields replace existing values.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    destination: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
        description="Updated destination name.",
    )
    start_date: date | None = Field(default=None, description="Updated start date.")
    end_date: date | None = Field(default=None, description="Updated end date.")
    num_travelers: int | None = Field(default=None, ge=1, le=20, description="Updated travelers count.")
    budget: float | None = Field(default=None, gt=0, description="Updated total budget in USD.")
    travel_style: TravelStyle | None = Field(default=None, description="Updated travel style.")
    travel_interests: list[str] | None = Field(default=None, description="Updated list of interests.")
    dietary_preferences: list[str] | None = Field(default=None, description="Updated dietary preferences.")
    travel_pace: TravelPace | None = Field(default=None, description="Updated travel pace.")
    primary_vibe: str | None = Field(default=None, description="Updated primary travel vibe.")
    secondary_vibes: list[str] | None = Field(default=None, description="Updated secondary travel vibes.")
    additional_requirements: str | None = Field(default=None, max_length=500, description="Updated notes.")

    @field_validator("travel_style", mode="before")
    @classmethod
    def normalize_travel_style(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("travel_pace", mode="before")
    @classmethod
    def normalize_travel_pace(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("budget", mode="before")
    @classmethod
    def clean_budget(cls, v: Any) -> Any:
        if isinstance(v, str):
            cleaned = v.replace("$", "").replace(",", "").strip()
            return float(cleaned)
        return v

    @field_validator("travel_interests", mode="before")
    @classmethod
    def clean_interests(cls, v: Any) -> Any:
        if isinstance(v, list):
            return [item.strip().lower() for item in v if isinstance(item, str) and item.strip()]
        return v

    @model_validator(mode="after")
    def validate_dates_if_both_provided(self) -> "TripUpdateRequest":
        if self.start_date is not None and self.end_date is not None:
            if self.end_date <= self.start_date:
                raise ValueError("end_date must be strictly after start_date.")
        return self


# ── Trip response schema ───────────────────────────────────────────────────────

class TripResponse(BaseModel):
    """
    Response body returned from all trip endpoints.
    """

    model_config = ConfigDict(from_attributes=True)

    id:                                  str
    user_id:                             str
    destination:                         str
    start_date:                          date
    end_date:                            date
    num_travelers:                       int = 1
    budget:                              float
    travel_style:                        str = "cultural"
    travel_interests:                    list[str] = Field(default_factory=list)
    dietary_preferences:                 list[str] = Field(default_factory=list)
    travel_pace:                         str = "moderate"
    primary_vibe:                        str | None = None
    secondary_vibes:                     list[str] = Field(default_factory=list)
    additional_requirements:             str | None = None
    status:                              str = "pending"
    created_at:                          str | None = None
    has_itinerary:                       bool = False
    itinerary_regeneration_recommended:  bool = False


class TripDeleteResponse(BaseModel):
    """
    Response body returned on successful trip deletion.
    """

    success:         bool = True
    message:         str
    deleted_trip_id: str
