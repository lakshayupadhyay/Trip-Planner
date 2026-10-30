"""
backend/app/services/recommendation_service.py

Intelligent Destination & Activity Recommendation Engine powered by Google Gemini API.
Translates traveler preferences into validated, highly-personalized recommendations.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any
from dotenv import load_dotenv
from fastapi import HTTPException

from app.models.recommendations import (
    ActivitiesRecommendationResponse,
    ActivityRecommendation,
    ActivityRecommendationRequest,
    DestinationRecommendation,
    DestinationRecommendationRequest,
    DestinationsRecommendationResponse,
)

load_dotenv()


def _clean_json_text(text: str) -> str:
    """Extract and clean raw JSON from LLM output, stripping markdown codeblocks."""
    cleaned = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned, re.IGNORECASE)
    if match:
        cleaned = match.group(1).strip()
    return cleaned


class RecommendationService:
    """
    Service for generating structured recommendations via Google Gemini API.
    Supports dependency injection for automated testing without live API calls.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str | None = None,
        client: Any | None = None,
    ) -> None:
        self._api_key = api_key or os.getenv("GEMINI_API_KEY")
        self._model_name = model_name or os.getenv("GEMINI_MODEL") or "gemini-3.8-flash"
        self._client = client

    @property
    def client(self) -> Any:
        """Lazily initialize Google GenAI client."""
        if self._client is not None:
            return self._client

        if not self._api_key or self._api_key == "your-gemini-api-key" or self._api_key.startswith("your_"):
            raise HTTPException(
                status_code=500,
                detail="Gemini API key is not configured. Please set GEMINI_API_KEY in your backend .env file.",
            )

        try:
            from google import genai
            self._client = genai.Client(api_key=self._api_key)
            return self._client
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize Google GenAI client: {exc}",
            ) from exc

    # ── Activity & Dining Recommendations ──────────────────────────────────────

    def get_activity_recommendations(
        self, request: ActivityRecommendationRequest
    ) -> ActivitiesRecommendationResponse:
        """
        Generate recommendations for attractions, activities, and dining within a chosen destination.
        """
        interests_str = ", ".join(request.travel_interests) if request.travel_interests else "general sightseeing, local highlights"
        dietary_str = ", ".join(request.dietary_preferences) if request.dietary_preferences else "None specified"
        budget_str = f"${request.budget:,.2f} USD" if request.budget else "Standard mid-range budget"
        reqs_str = request.additional_requirements or "None"

        prompt = f"""You are an elite travel concierge. Generate 5 to 7 high-quality, personalized recommendations for travelers visiting {request.destination}.

TRAVELER PROFILE:
- Destination: {request.destination}
- Number of Travelers: {request.num_travelers}
- Total Budget: {budget_str}
- Travel Style: {request.travel_style}
- Travel Interests: {interests_str}
- Pace: {request.travel_pace}
- Dietary Preferences: {dietary_str}
- Additional Requirements: {reqs_str}

REQUIREMENTS:
1. Provide a diverse mix across categories: Attractions, Activities, Dining, Cultural Experiences, Nature and Adventure.
2. For Dining: STRICTLY honor the dietary restrictions ({dietary_str}) with known, real restaurants or food markets.
3. For Activities: Align with the '{request.travel_style}' style and interests: {interests_str}.
4. Provide estimated costs, suggested durations, optimal visit times, and actionable practical tips.
5. Do NOT invent confirmed bookings, ticket availability, or guaranteed table reservations.
6. Return valid JSON only, matching the exact schema below.

JSON SCHEMA:
{{
  "destination": "{request.destination}",
  "recommendations": [
    {{
      "name": "Attraction or Venue Name",
      "category": "Attractions | Activities | Dining | Cultural Experiences | Nature and Adventure",
      "description": "Engaging description of the spot",
      "reason_for_recommendation": "Why this specifically fits the traveler's preferences",
      "estimated_cost": "Estimated cost string (e.g. '~$20 USD / person' or 'Free')",
      "suggested_duration": "Estimated time (e.g. '2-3 hours')",
      "best_time_to_visit": "Best time (e.g. 'Morning, 9:00 AM')",
      "location": "Neighborhood or district",
      "practical_tips": "Helpful tip for visitors"
    }}
  ],
  "notes": "Brief overview note on making the most of these recommendations"
}}
"""

        try:
            response = self.client.models.generate_content(
                model=self._model_name,
                contents=prompt,
            )
            raw_text = response.text or ""
            cleaned = _clean_json_text(raw_text)
            data = json.loads(cleaned)
            return ActivitiesRecommendationResponse(**data)

        except HTTPException:
            raise
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to parse AI response into structured JSON: {exc}",
            ) from exc
        except Exception as exc:
            err_name = type(exc).__name__
            msg = str(exc)
            if "RESOURCE_EXHAUSTED" in msg or "429" in msg or "quota" in msg.lower():
                raise HTTPException(
                    status_code=429,
                    detail="Gemini API rate limit exceeded. Please retry in a few moments.",
                ) from exc
            if "DEADLINE_EXCEEDED" in msg or "timeout" in msg.lower():
                raise HTTPException(
                    status_code=504,
                    detail="Gemini API request timed out. Please retry.",
                ) from exc
            raise HTTPException(
                status_code=502,
                detail=f"AI Recommendation service error ({err_name}): {msg}",
            ) from exc

    # ── Destination Recommendations ────────────────────────────────────────────

    def get_destination_recommendations(
        self, request: DestinationRecommendationRequest
    ) -> DestinationsRecommendationResponse:
        """
        Suggest destinations when the user has not finalized a destination yet.
        """
        interests_str = ", ".join(request.travel_interests) if request.travel_interests else "general sightseeing, diverse experiences"
        budget_str = f"${request.budget:,.2f} USD" if request.budget else "Flexible / standard budget"
        region_str = request.preferred_region or "Worldwide / open to anywhere"
        reqs_str = request.additional_requirements or "None"

        prompt = f"""You are an expert destination discovery guide. Recommend 3 to 5 premier travel destinations tailored specifically to the user's travel style, budget, and interests.

TRAVELER PREFERENCES:
- Preferred Region: {region_str}
- Number of Travelers: {request.num_travelers}
- Total Budget: {budget_str}
- Travel Style: {request.travel_style}
- Travel Interests: {interests_str}
- Pace: {request.travel_pace}
- Additional Requirements: {reqs_str}

REQUIREMENTS:
1. Recommend destinations that authentically match the travel style ({request.travel_style}) and interests ({interests_str}).
2. Provide a realistic budget range that fits within the stated financial capacity ({budget_str}).
3. List 3 to 4 top highlight attractions for each destination.
4. Give actionable practical tips (best season, transit, currency).
5. Return valid JSON only, matching the exact schema below.

JSON SCHEMA:
{{
  "recommendations": [
    {{
      "destination": "City, Country",
      "country": "Country Name",
      "description": "Compelling summary of the destination",
      "why_it_matches": "Clear explanation of how it aligns with the traveler's style, interests, and budget",
      "estimated_budget_range": "e.g. '$1,200 - $1,800 USD per person'",
      "best_time_to_visit": "e.g. 'April to June, September to October'",
      "highlight_attractions": ["Highlight 1", "Highlight 2", "Highlight 3"],
      "practical_tips": "Key advice on getting around or saving money"
    }}
  ],
  "notes": "Helpful guidance on comparing and choosing among these destinations"
}}
"""

        try:
            response = self.client.models.generate_content(
                model=self._model_name,
                contents=prompt,
            )
            raw_text = response.text or ""
            cleaned = _clean_json_text(raw_text)
            data = json.loads(cleaned)
            return DestinationsRecommendationResponse(**data)

        except HTTPException:
            raise
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to parse AI response into structured JSON: {exc}",
            ) from exc
        except Exception as exc:
            err_name = type(exc).__name__
            msg = str(exc)
            if "RESOURCE_EXHAUSTED" in msg or "429" in msg or "quota" in msg.lower():
                raise HTTPException(
                    status_code=429,
                    detail="Gemini API rate limit exceeded. Please retry in a few moments.",
                ) from exc
            if "DEADLINE_EXCEEDED" in msg or "timeout" in msg.lower():
                raise HTTPException(
                    status_code=504,
                    detail="Gemini API request timed out. Please retry.",
                ) from exc
            raise HTTPException(
                status_code=502,
                detail=f"AI Recommendation service error ({err_name}): {msg}",
            ) from exc

