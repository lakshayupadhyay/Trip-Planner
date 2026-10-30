"""
tests/test_traveler_scenarios.py

Systematic validation of 11 distinct traveler scenarios for Epic 5 – Activity 5.3:
  1. Solo Travelers
  2. Couples
  3. Families with Children
  4. Groups of Travelers
  5. Budget-Conscious Travelers
  6. Luxury Travelers
  7. Adventure Travelers
  8. Relaxed Travelers
  9. Cultural Travelers
 10. Travelers with Dietary Restrictions (Vegan, Halal, Kosher, Gluten-Free)
 11. Travelers with Mobility Requirements (Step-free, Wheelchair accessible)
"""

from datetime import date
import pytest

from app.models.trip import TripCreateRequest
from app.services.prompt_service import (
    build_itinerary_prompt,
    build_structured_itinerary_prompt,
    calculate_trip_duration,
)


# ── Scenario 1: Solo Traveler ───────────────────────────────────────────────

def test_scenario_solo_traveler():
    """Verify Solo Traveler persona (1 person, safety, flexible pacing)."""
    trip_data = TripCreateRequest(
        destination="Tokyo, Japan",
        start_date=date(2027, 4, 1),
        end_date=date(2027, 4, 7),
        num_travelers=1,
        budget=2000.0,
        travel_style="cultural",
        travel_interests=["photography", "local food"],
        travel_pace="moderate",
        primary_vibe="Cultural",
    )
    assert trip_data.num_travelers == 1

    prompt = build_itinerary_prompt(
        destination=trip_data.destination,
        start_date=trip_data.start_date,
        end_date=trip_data.end_date,
        travel_style=trip_data.travel_style,
        travel_interests=trip_data.travel_interests,
        num_travelers=trip_data.num_travelers,
        budget=trip_data.budget,
        travel_pace=trip_data.travel_pace,
        primary_vibe=trip_data.primary_vibe,
    )
    assert "Solo Traveler" in prompt
    assert "Budget per Traveler: $2,000.00 USD" in prompt
    assert "Cultural" in prompt


# ── Scenario 2: Couples ─────────────────────────────────────────────────────

def test_scenario_couple_travelers():
    """Verify Couple persona (2 people, romantic vibe, intimate dining)."""
    trip_data = TripCreateRequest(
        destination="Venice, Italy",
        start_date=date(2027, 5, 10),
        end_date=date(2027, 5, 15),
        num_travelers=2,
        budget=3500.0,
        travel_style="romantic",
        travel_interests=["art", "wine", "sightseeing"],
        travel_pace="slow",
        primary_vibe="Romantic",
        secondary_vibes=["Food & Culinary"],
    )
    assert trip_data.num_travelers == 2
    assert trip_data.travel_style == "romantic"

    prompt = build_itinerary_prompt(
        destination=trip_data.destination,
        start_date=trip_data.start_date,
        end_date=trip_data.end_date,
        travel_style=trip_data.travel_style,
        travel_interests=trip_data.travel_interests,
        num_travelers=trip_data.num_travelers,
        budget=trip_data.budget,
        travel_pace=trip_data.travel_pace,
        primary_vibe=trip_data.primary_vibe,
        secondary_vibes=trip_data.secondary_vibes,
    )
    assert "party of 2" in prompt or "Group of 2" in prompt
    assert "Romantic" in prompt
    assert "Food & culinary" in prompt or "Food & Culinary" in prompt
    assert "RELAXED / SLOW" in prompt


# ── Scenario 3: Families with Children ──────────────────────────────────────

def test_scenario_family_with_children():
    """Verify Family persona (kid-friendly activities, safety, manageable pace)."""
    trip_data = TripCreateRequest(
        destination="Orlando, USA",
        start_date=date(2027, 6, 1),
        end_date=date(2027, 6, 8),
        num_travelers=4,
        budget=5000.0,
        travel_style="family",
        travel_interests=["theme parks", "nature", "aquariums"],
        travel_pace="moderate",
        primary_vibe="Family",
        additional_requirements="Traveling with two children aged 6 and 9. Require kid-friendly meals and rest periods.",
    )
    assert trip_data.num_travelers == 4
    assert trip_data.travel_style == "family"

    prompt = build_itinerary_prompt(
        destination=trip_data.destination,
        start_date=trip_data.start_date,
        end_date=trip_data.end_date,
        travel_style=trip_data.travel_style,
        travel_interests=trip_data.travel_interests,
        num_travelers=trip_data.num_travelers,
        budget=trip_data.budget,
        travel_pace=trip_data.travel_pace,
        primary_vibe=trip_data.primary_vibe,
        additional_requirements=trip_data.additional_requirements,
    )
    assert "kid-friendly" in prompt.lower()
    assert "party of 4" in prompt or "Group of 4" in prompt
    assert "children aged 6 and 9" in prompt


# ── Scenario 4: Groups of Travelers ────────────────────────────────────────

def test_scenario_group_travelers():
    """Verify Group persona (larger party, coordinated logistics, variety)."""
    trip_data = TripCreateRequest(
        destination="Barcelona, Spain",
        start_date=date(2027, 7, 10),
        end_date=date(2027, 7, 17),
        num_travelers=8,
        budget=9600.0,
        travel_style="cultural",
        travel_interests=["architecture", "beaches", "tapas"],
        travel_pace="moderate",
        primary_vibe="Nightlife",
        secondary_vibes=["Food & Culinary"],
    )
    assert trip_data.num_travelers == 8

    prompt = build_itinerary_prompt(
        destination=trip_data.destination,
        start_date=trip_data.start_date,
        end_date=trip_data.end_date,
        travel_style=trip_data.travel_style,
        travel_interests=trip_data.travel_interests,
        num_travelers=trip_data.num_travelers,
        budget=trip_data.budget,
        travel_pace=trip_data.travel_pace,
        primary_vibe=trip_data.primary_vibe,
        secondary_vibes=trip_data.secondary_vibes,
    )
    assert "Group of 8" in prompt
    assert "Budget per Traveler: $1,200.00 USD" in prompt
    assert "party of 8" in prompt


# ── Scenario 5: Budget-Conscious Travelers ─────────────────────────────────

def test_scenario_budget_conscious_traveler():
    """Verify Budget traveler (low daily cost, free attractions, street food)."""
    trip_data = TripCreateRequest(
        destination="Prague, Czech Republic",
        start_date=date(2027, 8, 1),
        end_date=date(2027, 8, 5),
        num_travelers=1,
        budget=400.0,
        travel_style="budget",
        travel_interests=["walking tours", "castles", "viewpoints"],
        travel_pace="moderate",
        primary_vibe="Budget",
    )
    assert trip_data.budget == 400.0

    prompt = build_itinerary_prompt(
        destination=trip_data.destination,
        start_date=trip_data.start_date,
        end_date=trip_data.end_date,
        travel_style=trip_data.travel_style,
        travel_interests=trip_data.travel_interests,
        num_travelers=trip_data.num_travelers,
        budget=trip_data.budget,
        travel_pace=trip_data.travel_pace,
        primary_vibe=trip_data.primary_vibe,
    )
    assert "free or affordable sights" in prompt.lower() or "free-admission" in prompt.lower()
    assert "Total Trip Budget: $400.00 USD" in prompt
    assert "Target Average Daily Spend: ~$80.00 USD/day" in prompt


# ── Scenario 6: Luxury Travelers ──────────────────────────────────────────

def test_scenario_luxury_traveler():
    """Verify Luxury persona (premium dining, VIP access, exclusive ambiance)."""
    trip_data = TripCreateRequest(
        destination="Dubai, UAE",
        start_date=date(2027, 9, 15),
        end_date=date(2027, 9, 20),
        num_travelers=2,
        budget=12000.0,
        travel_style="luxury",
        travel_interests=["fine dining", "desert safari", "skyline"],
        travel_pace="relaxed",
        primary_vibe="Luxury",
    )
    assert trip_data.travel_style == "luxury"
    assert trip_data.budget == 12000.0

    prompt = build_itinerary_prompt(
        destination=trip_data.destination,
        start_date=trip_data.start_date,
        end_date=trip_data.end_date,
        travel_style=trip_data.travel_style,
        travel_interests=trip_data.travel_interests,
        num_travelers=trip_data.num_travelers,
        budget=trip_data.budget,
        travel_pace=trip_data.travel_pace,
        primary_vibe=trip_data.primary_vibe,
    )
    assert "michelin" in prompt.lower() or "fine dining" in prompt.lower() or "vip" in prompt.lower()
    assert "Budget per Traveler: $6,000.00 USD" in prompt


# ── Scenario 7: Adventure Travelers ───────────────────────────────────────

def test_scenario_adventure_traveler():
    """Verify Adventure persona (outdoor expeditions, hikes, fast pace)."""
    trip_data = TripCreateRequest(
        destination="Queenstown, New Zealand",
        start_date=date(2027, 11, 1),
        end_date=date(2027, 11, 8),
        num_travelers=2,
        budget=4500.0,
        travel_style="adventure",
        travel_interests=["bungee jumping", "hiking", "kayaking"],
        travel_pace="fast",
        primary_vibe="Adventure",
        secondary_vibes=["Nature & Exploration"],
    )
    assert trip_data.travel_pace == "fast"

    prompt = build_itinerary_prompt(
        destination=trip_data.destination,
        start_date=trip_data.start_date,
        end_date=trip_data.end_date,
        travel_style=trip_data.travel_style,
        travel_interests=trip_data.travel_interests,
        num_travelers=trip_data.num_travelers,
        budget=trip_data.budget,
        travel_pace=trip_data.travel_pace,
        primary_vibe=trip_data.primary_vibe,
        secondary_vibes=trip_data.secondary_vibes,
    )
    assert "FAST / HIGH-ENERGY" in prompt
    assert "Adventure" in prompt
    assert "Nature & exploration" in prompt or "Nature & Exploration" in prompt


# ── Scenario 8: Relaxed Travelers ─────────────────────────────────────────

def test_scenario_relaxed_traveler():
    """Verify Relaxed persona (spas, cafes, slow leisurely downtime)."""
    trip_data = TripCreateRequest(
        destination="Bali, Indonesia",
        start_date=date(2027, 10, 1),
        end_date=date(2027, 10, 8),
        num_travelers=2,
        budget=2500.0,
        travel_style="relaxation",
        travel_interests=["yoga", "beaches", "wellness"],
        travel_pace="slow",
        primary_vibe="Relaxed",
    )
    assert trip_data.travel_pace == "slow"

    prompt = build_itinerary_prompt(
        destination=trip_data.destination,
        start_date=trip_data.start_date,
        end_date=trip_data.end_date,
        travel_style=trip_data.travel_style,
        travel_interests=trip_data.travel_interests,
        num_travelers=trip_data.num_travelers,
        budget=trip_data.budget,
        travel_pace=trip_data.travel_pace,
        primary_vibe=trip_data.primary_vibe,
    )
    assert "RELAXED / SLOW" in prompt
    assert "Schedule 1 to 2 key activities per day" in prompt
    assert "Relaxed" in prompt


# ── Scenario 9: Cultural Travelers ────────────────────────────────────────

def test_scenario_cultural_traveler():
    """Verify Cultural persona (world heritage, museums, historic architecture)."""
    trip_data = TripCreateRequest(
        destination="Rome, Italy",
        start_date=date(2027, 4, 15),
        end_date=date(2027, 4, 20),
        num_travelers=1,
        budget=1800.0,
        travel_style="cultural",
        travel_interests=["ancient history", "museums", "cathedrals"],
        travel_pace="moderate",
        primary_vibe="Cultural",
    )
    prompt = build_itinerary_prompt(
        destination=trip_data.destination,
        start_date=trip_data.start_date,
        end_date=trip_data.end_date,
        travel_style=trip_data.travel_style,
        travel_interests=trip_data.travel_interests,
        num_travelers=trip_data.num_travelers,
        budget=trip_data.budget,
        travel_pace=trip_data.travel_pace,
        primary_vibe=trip_data.primary_vibe,
    )
    assert "UNESCO" in prompt or "historic" in prompt.lower()
    assert "ancient history" in prompt.lower()


# ── Scenario 10: Dietary Restrictions (Vegan, Halal, Kosher, Gluten-Free) ──

def test_scenario_dietary_restrictions():
    """Verify strict adherence to multiple dietary constraints."""
    trip_data = TripCreateRequest(
        destination="London, UK",
        start_date=date(2027, 5, 1),
        end_date=date(2027, 5, 5),
        num_travelers=2,
        budget=2200.0,
        travel_style="cultural",
        travel_interests=["theatre", "museums"],
        dietary_preferences=["vegan", "gluten-free", "halal"],
        travel_pace="moderate",
    )
    assert "vegan" in trip_data.dietary_preferences
    assert "gluten-free" in trip_data.dietary_preferences
    assert "halal" in trip_data.dietary_preferences

    prompt = build_itinerary_prompt(
        destination=trip_data.destination,
        start_date=trip_data.start_date,
        end_date=trip_data.end_date,
        travel_style=trip_data.travel_style,
        travel_interests=trip_data.travel_interests,
        num_travelers=trip_data.num_travelers,
        budget=trip_data.budget,
        travel_pace=trip_data.travel_pace,
        dietary_preferences=trip_data.dietary_preferences,
    )
    assert "vegan, gluten-free, halal" in prompt
    assert "Dietary Preferences" in prompt


# ── Scenario 11: Mobility Requirements ────────────────────────────────────

def test_scenario_mobility_requirements():
    """Verify special accommodation for travelers with physical mobility needs."""
    trip_data = TripCreateRequest(
        destination="Amsterdam, Netherlands",
        start_date=date(2027, 6, 1),
        end_date=date(2027, 6, 5),
        num_travelers=2,
        budget=2000.0,
        travel_style="relaxation",
        travel_interests=["canals", "art", "parks"],
        travel_pace="slow",
        additional_requirements="Wheelchair user in group. All venues, transit, and dining must be 100% step-free accessible.",
    )
    prompt = build_itinerary_prompt(
        destination=trip_data.destination,
        start_date=trip_data.start_date,
        end_date=trip_data.end_date,
        travel_style=trip_data.travel_style,
        travel_interests=trip_data.travel_interests,
        num_travelers=trip_data.num_travelers,
        budget=trip_data.budget,
        travel_pace=trip_data.travel_pace,
        additional_requirements=trip_data.additional_requirements,
    )
    assert "Wheelchair user in group" in prompt
    assert "step-free accessible" in prompt
