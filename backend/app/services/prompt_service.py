"""
backend/app/services/prompt_service.py

Modular Prompt Engineering Service for Personalized Travel Itineraries.
Transforms validated user preferences into structured, high-quality
prompts for Generative AI models (such as Google Gemini).

Sections:
1. AI Role and Instructions
2. Destination and Travel Dates
3. Traveler Information
4. Budget Constraints
5. Travel Style and Interests
6. Daily Activity Pace
7. Dietary Preferences
8. Additional Requirements
9. Expected Output Format
10. Accuracy and Safety Constraints
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Sequence


def parse_date(d: date | str) -> date:
    """Safely convert a date or ISO string to a datetime.date object."""
    if isinstance(d, date):
        return d
    return datetime.strptime(str(d).strip(), "%Y-%m-%d").date()


def calculate_trip_duration(start_date: date | str, end_date: date | str) -> dict[str, int]:
    """
    Calculate the duration of the trip in days and nights.
    A trip from May 1 to May 7 spans 7 days (inclusive) and 6 nights.
    """
    start = parse_date(start_date)
    end = parse_date(end_date)
    if end <= start:
        raise ValueError(f"end_date ({end}) must be after start_date ({start}).")

    nights = (end - start).days
    days = nights + 1
    return {"days": days, "nights": nights}


def _get_pace_guidelines(pace: str) -> str:
    """Return tailored pacing instructions based on user selection."""
    normalized = pace.strip().lower()
    if normalized in ("slow", "relaxed"):
        return (
            "- Pacing Strategy: RELAXED / SLOW.\n"
            "- Schedule 1 to 2 key activities per day.\n"
            "- Include generous rest intervals, late starts, and unhurried downtime.\n"
            "- Focus on deep immersion rather than checking off multiple sights."
        )
    elif normalized == "fast":
        return (
            "- Pacing Strategy: FAST / HIGH-ENERGY.\n"
            "- Schedule 3 to 4 major sights and activities per day.\n"
            "- Plan efficient routing with early starts to maximize daily coverage.\n"
            "- Minimize idle time between activities while maintaining realistic transit."
        )
    else:  # moderate default
        return (
            "- Pacing Strategy: MODERATE / BALANCED.\n"
            "- Schedule 2 to 3 well-spaced activities per day.\n"
            "- Provide a comfortable rhythm with dedicated meal breaks and moderate walking.\n"
            "- Balance landmark visits with spontaneous neighborhood exploration."
        )


def _get_style_guidelines(style: str) -> str:
    """Return tailored style focus based on travel style."""
    normalized = style.strip().lower()
    style_map = {
        "adventure": "Focus on outdoor exploration, active experiences, nature trails, and energetic activities.",
        "cultural": "Highlight historic landmarks, architectural wonders, world-class museums, and authentic local heritage.",
        "relaxation": "Emphasize scenic viewpoints, peaceful gardens, tranquil walks, and unhurried leisure.",
        "leisure": "Emphasize scenic viewpoints, peaceful gardens, tranquil walks, and unhurried leisure.",
        "family": "Feature kid-friendly attractions, accessible amenities, safe public spaces, and engaging experiences for all ages.",
        "luxury": "Recommend upscale dining, premium experiences, scenic private spots, and high-comfort logistics.",
        "romantic": "Highlight intimate viewpoints, sunset spots, charming bistros, scenic strolls, and couple-friendly ambiance.",
        "budget": "Prioritize free or affordable sights, public transit options, self-guided tours, and local street food/value eateries.",
    }
    return style_map.get(
        normalized,
        f"Tailor the overall tone and activity selection to the '{style}' travel style.",
    )


# ── Activity 4.3: Vibe-Based Personalization Guidelines ─────────────────────────

VIBE_GUIDELINES: dict[str, str] = {
    "romantic": (
        "Focus on intimate ambiance, scenic panoramic viewpoints, serene sunset spots, "
        "atmospheric couples dining (candlelit or waterfront), and relaxed, unhurried pacing."
    ),
    "adventure": (
        "Emphasize thrilling outdoor activities, nature treks, adrenaline-filled experiences, "
        "rugged terrain exploration, and high-energy excursions."
    ),
    "luxury": (
        "Highlight Michelin-starred or acclaimed fine dining, VIP and skip-the-line access, "
        "private scenic charters, exclusive viewpoints, and supreme-comfort logistics."
    ),
    "relaxed": (
        "Prioritize slow mornings, tranquil parks and botanical gardens, sunlit cafe terraces, "
        "thermal baths or waterfront promenades, with generous downtime between sights."
    ),
    "budget": (
        "Feature free-admission landmarks, scenic public plazas, self-guided walking tours, "
        "cost-effective public transit, and vibrant, affordable street-food markets."
    ),
    "cultural": (
        "Deeply immerse in ancient shrines, UNESCO world heritage sites, world-class art museums, "
        "artisan craft workshops, and traditional historic quarters."
    ),
    "family": (
        "Select interactive and kid-friendly attractions, spacious parks, interactive science or wildlife exhibits, "
        "safe pedestrian areas, and welcoming family-friendly dining."
    ),
    "nightlife": (
        "Integrate illuminated night walks, vibrant night markets, rooftop cocktail lounges, "
        "live music or jazz clubs, and atmospheric evening dining districts."
    ),
    "nature & exploration": (
        "Focus on national parks, pristine hiking trails, coastal cliffs, wildlife viewing, "
        "scenic geological wonders, and fresh-air nature reserves."
    ),
    "food & culinary": (
        "Center on iconic local culinary institutions, morning produce/fish markets, food tasting tours, "
        "cooking masterclasses, and regional specialty dining."
    ),
}


def _get_vibe_guidelines(
    primary_vibe: str | None = None,
    secondary_vibes: Sequence[str] | None = None,
) -> str:
    """Return tailored instructions for primary and secondary travel vibes."""
    lines: list[str] = []
    if primary_vibe:
        norm_prim = primary_vibe.strip().lower()
        desc = VIBE_GUIDELINES.get(
            norm_prim,
            f"Tailor activities, dining, and atmosphere to the '{primary_vibe}' travel vibe.",
        )
        lines.append(f"- Primary Travel Vibe: {primary_vibe.capitalize()}\n  {desc}")

    if secondary_vibes:
        sec_bullets: list[str] = []
        for sv in secondary_vibes:
            if not sv:
                continue
            norm_sv = sv.strip().lower()
            sv_desc = VIBE_GUIDELINES.get(norm_sv, f"Incorporate {sv} nuances.")
            sec_bullets.append(f"• {sv.capitalize()}: {sv_desc}")
        if sec_bullets:
            lines.append("- Secondary Travel Vibes to Blend in:\n  " + "\n  ".join(sec_bullets))

    if not lines:
        return ""
    return "\n" + "\n".join(lines)


def build_itinerary_prompt(
    destination: str,
    start_date: date | str,
    end_date: date | str,
    travel_style: str,
    travel_interests: Sequence[str],
    num_travelers: int,
    budget: float,
    travel_pace: str,
    dietary_preferences: Sequence[str] | None = None,
    additional_requirements: str | None = None,
    primary_vibe: str | None = None,
    secondary_vibes: Sequence[str] | None = None,
) -> str:
    """
    Build a comprehensive, structured prompt for generating a personalized
    travel itinerary via a generative AI model.

    Parameters
    ----------
    destination : str
        Target travel destination (e.g. 'Kyoto, Japan').
    start_date : date | str
        First day of travel.
    end_date : date | str
        Last day of travel (must be after start_date).
    travel_style : str
        Travel style (e.g. 'cultural', 'adventure', 'romantic').
    travel_interests : Sequence[str]
        List of user interests (e.g. ['history', 'food', 'art']).
    num_travelers : int
        Number of travelers in the party.
    budget : float
        Total budget in USD.
    travel_pace : str
        Desired pace ('slow'/'relaxed', 'moderate', 'fast').
    dietary_preferences : Sequence[str] | None, optional
        Dietary restrictions (e.g. ['vegetarian', 'halal']).
    additional_requirements : str | None, optional
        Free-form notes, accessibility requests, or special requests.

    Returns
    -------
    str
        Structured, production-ready natural language prompt.
    """
    # 1. Calculate duration
    start = parse_date(start_date)
    end = parse_date(end_date)
    duration = calculate_trip_duration(start, end)
    days = duration["days"]
    nights = duration["nights"]

    # 2. Financial breakdowns
    traveler_count = max(1, int(num_travelers))
    total_budget = float(budget)
    per_person_budget = total_budget / traveler_count
    daily_budget_estimate = total_budget / days

    # 3. Format interests & preferences
    interests_str = ", ".join(travel_interests) if travel_interests else "General sightseeing"
    clean_dietary = [d for d in (dietary_preferences or []) if d.lower() != "none"]
    dietary_str = ", ".join(clean_dietary) if clean_dietary else "No special dietary restrictions specified."

    reqs_str = (
        additional_requirements.strip()
        if additional_requirements and additional_requirements.strip()
        else "No additional special requirements specified."
    )

    pace_instructions = _get_pace_guidelines(travel_pace)
    style_instructions = _get_style_guidelines(travel_style)
    vibe_instructions = _get_vibe_guidelines(primary_vibe, secondary_vibes)

    # 4. Construct the 10-section prompt
    prompt = f"""# TRAVEL ITINERARY GENERATION REQUEST

## 1. AI Role and Instructions
You are an expert, world-class travel planner, certified tour guide, and local cultural concierge.
Your mission is to design a personalized, practical, inspiring, and day-by-day travel itinerary
specifically curated to the traveler's exact preferences, budget, pace, and interests described below.

## 2. Destination and Travel Dates
- Destination: {destination.strip()}
- Start Date: {start.strftime("%Y-%m-%d")} ({start.strftime("%A")})
- End Date: {end.strftime("%Y-%m-%d")} ({end.strftime("%A")})
- Duration: {days} Days ({nights} Nights)

## 3. Traveler Information
- Number of Travelers: {traveler_count} {"person (Solo Traveler)" if traveler_count == 1 else f"people (Group of {traveler_count})"}
- Group Logistics: Ensure all recommended activities, transit methods, and dining venues comfortably accommodate a party of {traveler_count}.

## 4. Budget Constraints
- Total Trip Budget: ${total_budget:,.2f} USD
- Budget per Traveler: ${per_person_budget:,.2f} USD
- Target Average Daily Spend: ~${daily_budget_estimate:,.2f} USD/day (inclusive of activities, local transit, and meals)
- Budget Directive: All recommendations must remain within this financial scope. If the destination's typical costs exceed this budget, clearly explain the limitation and suggest money-saving alternatives (e.g. transit passes, free museum days) rather than inventing unrealistically low prices.

## 5. Travel Style and Interests
- Primary Travel Style: {travel_style.capitalize()}
  {style_instructions}
- Key Interests: {interests_str}
  Directly integrate activities, sights, and cultural spots that center on these specific interests.{vibe_instructions}

## 6. Daily Activity Pace
- Selected Pace: {travel_pace.capitalize()}
{pace_instructions}

## 7. Dietary Preferences
- Dietary Restrictions: {dietary_str}
- Dining Directive: When recommending dining venues, food districts, and local culinary specialties, strictly ensure accessibility for the noted dietary preferences. Provide recommendations of actual well-known dining spots or culinary neighborhoods that cater to these needs.

## 8. Additional Requirements
- Custom Notes / Accessibility: {reqs_str}
- Incorporate these specific requests throughout the itinerary where applicable.

## 9. Expected Output Format
Generate a comprehensive, chronological, day-by-day plan. For each day (Day 1 through Day {days}), include:
1. Day Header: "Day X - [YYYY-MM-DD] ([Day of Week]): [Theme or Focus Area]"
2. Morning Activity: Specific attraction/location, recommended arrival time, estimated duration, and estimated cost.
3. Lunch Recommendation: Specific local eatery, casual cafe, or food market respecting dietary restrictions.
4. Afternoon Activity: Secondary attraction or experience complementing the morning focus, with estimated cost.
5. Evening Activity & Dinner: Dinner recommendation followed by a relaxing evening stroll, viewpoint, or cultural experience.
6. Local Transportation & Travel Times: Estimated transit time and recommended travel mode (metro, bus, walking) between sights.
7. Daily Estimated Expenditure: Summary of estimated costs for activities, food, and transit for the day.
8. Practical Tip of the Day: Actionable local advice (e.g., ticket pre-booking, etiquette, transit pass, dress code).

At the end of the itinerary, provide a "Trip Budget & Logistics Summary" showing estimated total expenditure compared to the ${total_budget:,.2f} USD budget.

## 10. Accuracy and Safety Constraints
- Realistic Estimates Only: Label all prices, ticket costs, and transit times as reasonable estimates based on current local averages.
- No False Reservations: Do not fabricate confirmed booking numbers, guaranteed ticket availability, or hotel confirmations.
- Verification Advisory: Explicitly advise travelers to verify seasonal opening hours, holiday closures, ticket booking windows, and local transit advisories prior to departure.
- Safe & Feasible: Keep geographic routing logical (group nearby sights together on the same day) to avoid unnecessary backtracking.
"""
    return prompt.strip()


def build_structured_itinerary_prompt(
    destination: str,
    start_date: date | str,
    end_date: date | str,
    travel_style: str,
    travel_interests: Sequence[str],
    num_travelers: int,
    budget: float,
    travel_pace: str,
    dietary_preferences: Sequence[str] | None = None,
    additional_requirements: str | None = None,
    primary_vibe: str | None = None,
    secondary_vibes: Sequence[str] | None = None,
) -> str:
    """
    Build a prompt that instructs the LLM to generate a complete day-by-day
    travel itinerary strictly formatted as a valid JSON object matching the
    ItineraryResponse schema.
    """
    # Reuse core prompt sections from build_itinerary_prompt
    base_prompt = build_itinerary_prompt(
        destination=destination,
        start_date=start_date,
        end_date=end_date,
        travel_style=travel_style,
        travel_interests=travel_interests,
        num_travelers=num_travelers,
        budget=budget,
        travel_pace=travel_pace,
        dietary_preferences=dietary_preferences,
        additional_requirements=additional_requirements,
        primary_vibe=primary_vibe,
        secondary_vibes=secondary_vibes,
    )

    json_instructions = f"""

# STRICT JSON OUTPUT REQUIREMENT
You MUST return ONLY a valid, parseable JSON object adhering to the schema below.
Do not include any greeting, preamble, explanations, or commentary outside the JSON.

JSON SCHEMA:
{{
  "destination": "{destination.strip()}",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "duration_days": int,
  "total_budget": {float(budget)},
  "travel_style": "{travel_style}",
  "travel_pace": "{travel_pace}",
  "trip_summary": "Comprehensive executive summary of the customized itinerary and its highlights",
  "total_estimated_cost": "e.g. '~$2,250 USD total across all travelers (well within $3,000 budget)'",
  "packing_and_prep_tips": [
    "Tip 1 regarding seasonal clothing or footwear",
    "Tip 2 regarding local currency, power adapters, or reservations",
    "Tip 3 regarding cultural etiquette or transit apps"
  ],
  "days": [
    {{
      "day_number": 1,
      "date": "YYYY-MM-DD",
      "theme": "Geographic theme or focus of the day",
      "morning_activity": {{
        "time_slot": "morning",
        "name": "Attraction Name",
        "description": "Engaging description of the morning visit",
        "location": "Neighborhood or district",
        "suggested_duration": "2 - 2.5 hours",
        "estimated_cost": "e.g. '$15 USD' or 'Free'",
        "best_time_to_visit": "9:00 AM",
        "booking_required": false,
        "practical_tips": "Helpful visitor advice"
      }},
      "lunch": {{
        "meal_type": "Lunch",
        "name": "Eatery or Market Name",
        "cuisine": "Cuisine type",
        "description": "Description of the meal experience",
        "estimated_cost": "~$20 USD / person",
        "dietary_compliance": "Explicit note on how it satisfies specified dietary needs",
        "location": "Neighborhood",
        "practical_tips": "Reservations or popular specialty dish"
      }},
      "afternoon_activity": {{
        "time_slot": "afternoon",
        "name": "Afternoon Attraction Name",
        "description": "Detailed afternoon activity description",
        "location": "Neighborhood",
        "suggested_duration": "2 hours",
        "estimated_cost": "e.g. '$20 USD' or 'Free'",
        "best_time_to_visit": "2:00 PM",
        "booking_required": false,
        "practical_tips": "Afternoon tips"
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
        "name": "Evening Experience or Stroll",
        "description": "Relaxing viewpoint, historic walk, or night market",
        "location": "Neighborhood",
        "suggested_duration": "1.5 hours",
        "estimated_cost": "Free or estimated cost",
        "best_time_to_visit": "7:30 PM",
        "booking_required": false,
        "practical_tips": "Night-time tips"
      }},
      "transportation": {{
        "mode": "Metro Line 2 / Walking",
        "estimated_time": "15-20 mins between sights",
        "estimated_cost": "~$3.00 USD total",
        "route_details": "Take Metro from central station to district",
        "tips": "Consider day pass for savings"
      }},
      "daily_budget": {{
        "activities_cost": "~$35 USD",
        "dining_cost": "~$55 USD",
        "transportation_cost": "~$5 USD",
        "total_daily_estimated": "~$95 USD / person",
        "currency": "USD"
      }},
      "practical_tips": "Daily actionable tip on attire, ticket skip-the-line, or opening times"
    }}
  ]
}}
"""
    return (base_prompt + json_instructions).strip()


