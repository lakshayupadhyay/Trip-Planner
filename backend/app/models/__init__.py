"""
models/__init__.py
Exports all Pydantic models for use across the application.
"""

from app.models.trip import (
    TravelPreferences,
    TripCreateRequest,
    TripResponse,
    TripUpdateRequest,
    TripDeleteResponse,
    TravelStyle,
    TravelPace,
)
from app.models.user import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse
from app.models.itinerary import (
    PromptPreviewResponse,
    Activity,
    ActivitySchedule,
    RouteLeg,
    DiningRecommendation,
    Transportation,
    DailyBudget,
    DayItinerary,
    ItineraryResponse,
    ItineraryGenerateRequest,
    RouteOptimizationRequest,
    DayOptimizationRequest,
    ItineraryRefineRequest,
    DayRefineRequest,
    RefineResponse,
)
from app.models.recommendations import (
    ActivityRecommendation,
    ActivityRecommendationRequest,
    ActivitiesRecommendationResponse,
    DestinationRecommendation,
    DestinationRecommendationRequest,
    DestinationsRecommendationResponse,
)
from app.models.share import (
    TripShareResponse,
    TripRevokeResponse,
    SharedTripPublicResponse,
    TripSummaryResponse,
)

__all__ = [
    # Trip & Preference models
    "TravelPreferences",
    "TripCreateRequest",
    "TripResponse",
    "TripUpdateRequest",
    "TripDeleteResponse",
    "TravelStyle",
    "TravelPace",
    # User models
    "UserRegisterRequest",
    "UserLoginRequest",
    "TokenResponse",
    "UserResponse",
    # Itinerary models
    "PromptPreviewResponse",
    "Activity",
    "ActivitySchedule",
    "RouteLeg",
    "DiningRecommendation",
    "Transportation",
    "DailyBudget",
    "DayItinerary",
    "ItineraryResponse",
    "ItineraryGenerateRequest",
    "RouteOptimizationRequest",
    "DayOptimizationRequest",
    "ItineraryRefineRequest",
    "DayRefineRequest",
    "RefineResponse",
    # Recommendation models
    "ActivityRecommendation",
    "ActivityRecommendationRequest",
    "ActivitiesRecommendationResponse",
    "DestinationRecommendation",
    "DestinationRecommendationRequest",
    "DestinationsRecommendationResponse",
    # Share & Export models
    "TripShareResponse",
    "TripRevokeResponse",
    "SharedTripPublicResponse",
    "TripSummaryResponse",
]
