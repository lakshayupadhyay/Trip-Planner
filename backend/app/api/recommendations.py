"""
backend/app/api/recommendations.py

FastAPI router for AI-powered destination and activity recommendations.
Endpoints:
- POST /api/v1/recommendations/destinations
- POST /api/v1/recommendations/activities
"""

from __future__ import annotations

from fastapi import APIRouter

from app.models.recommendations import (
    ActivitiesRecommendationResponse,
    ActivityRecommendationRequest,
    DestinationRecommendationRequest,
    DestinationsRecommendationResponse,
)
from app.services.recommendation_service import RecommendationService

router = APIRouter()
recommendation_service = RecommendationService()


@router.post(
    "/destinations",
    response_model=DestinationsRecommendationResponse,
    summary="Recommend Travel Destinations",
    description="Generates personalized destination suggestions using Google Gemini based on travel style, budget, and interests.",
)
@router.post(
    "/destinations/",
    response_model=DestinationsRecommendationResponse,
    include_in_schema=False,
)
def recommend_destinations(
    request: DestinationRecommendationRequest,
) -> DestinationsRecommendationResponse:
    """Return AI-generated destination recommendations matching user criteria."""
    return recommendation_service.get_destination_recommendations(request)


@router.post(
    "/activities",
    response_model=ActivitiesRecommendationResponse,
    summary="Recommend Attractions, Activities & Dining",
    description="Generates personalized attraction, activity, and dining recommendations for a selected destination.",
)
@router.post(
    "/activities/",
    response_model=ActivitiesRecommendationResponse,
    include_in_schema=False,
)
def recommend_activities(
    request: ActivityRecommendationRequest,
) -> ActivitiesRecommendationResponse:
    """Return AI-generated attraction, activity, and dining recommendations for a destination."""
    return recommendation_service.get_activity_recommendations(request)

