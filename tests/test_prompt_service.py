"""
tests/test_prompt_service.py

Unit tests for Activity 3.2: Prompt Structuring Logic in prompt_service.py:
- Valid prompt construction
- Inclusion of destination, start/end dates, duration
- Budget calculation and traveler breakdown
- Style and interest customization
- Pacing adaptation (slow/relaxed, moderate, fast)
- Dietary preferences and additional requirements
- Empty optional preferences handling
- Duration calculation and invalid date error handling
"""

from datetime import date
import pytest

from app.services.prompt_service import (
    build_itinerary_prompt,
    calculate_trip_duration,
)


def test_calculate_trip_duration_valid():
    """Verify duration calculation in days (inclusive) and nights."""
    res = calculate_trip_duration(date(2027, 5, 1), date(2027, 5, 7))
    assert res["days"] == 7
    assert res["nights"] == 6


def test_calculate_trip_duration_invalid_dates():
    """Verify error raised when end_date <= start_date."""
    with pytest.raises(ValueError) as exc:
        calculate_trip_duration(date(2027, 5, 10), date(2027, 5, 5))
    assert "end_date" in str(exc.value)

    with pytest.raises(ValueError):
        calculate_trip_duration(date(2027, 5, 5), date(2027, 5, 5))


def test_build_itinerary_prompt_all_sections_present():
    """Verify that all 10 required prompt sections are generated."""
    prompt = build_itinerary_prompt(
        destination="Kyoto, Japan",
        start_date=date(2027, 4, 1),
        end_date=date(2027, 4, 8),
        travel_style="cultural",
        travel_interests=["history", "food", "temples"],
        num_travelers=2,
        budget=3500.0,
        travel_pace="moderate",
        dietary_preferences=["vegetarian"],
        additional_requirements="Prefer staying close to transit hubs",
    )

    required_sections = [
        "1. AI Role and Instructions",
        "2. Destination and Travel Dates",
        "3. Traveler Information",
        "4. Budget Constraints",
        "5. Travel Style and Interests",
        "6. Daily Activity Pace",
        "7. Dietary Preferences",
        "8. Additional Requirements",
        "9. Expected Output Format",
        "10. Accuracy and Safety Constraints",
    ]

    for section in required_sections:
        assert section in prompt, f"Missing section: {section}"

    assert "Kyoto, Japan" in prompt
    assert "2027-04-01" in prompt
    assert "2027-04-08" in prompt
    assert "8 Days (7 Nights)" in prompt
    assert "2 people" in prompt
    assert "$3,500.00 USD" in prompt
    assert "$1,750.00 USD" in prompt  # per person
    assert "Cultural" in prompt
    assert "history, food, temples" in prompt
    assert "vegetarian" in prompt
    assert "transit hubs" in prompt


def test_prompt_pacing_adaptation():
    """Verify that slow/relaxed, moderate, and fast paces produce distinct, targeted instructions."""
    prompt_slow = build_itinerary_prompt(
        destination="Rome, Italy",
        start_date=date(2027, 6, 1),
        end_date=date(2027, 6, 5),
        travel_style="relaxation",
        travel_interests=["art"],
        num_travelers=1,
        budget=1500.0,
        travel_pace="slow",
    )
    assert "RELAXED / SLOW" in prompt_slow
    assert "1 to 2 key activities" in prompt_slow

    prompt_fast = build_itinerary_prompt(
        destination="Rome, Italy",
        start_date=date(2027, 6, 1),
        end_date=date(2027, 6, 5),
        travel_style="adventure",
        travel_interests=["sports"],
        num_travelers=1,
        budget=1500.0,
        travel_pace="fast",
    )
    assert "FAST / HIGH-ENERGY" in prompt_fast
    assert "3 to 4 major sights" in prompt_fast

    prompt_mod = build_itinerary_prompt(
        destination="Rome, Italy",
        start_date=date(2027, 6, 1),
        end_date=date(2027, 6, 5),
        travel_style="cultural",
        travel_interests=["history"],
        num_travelers=1,
        budget=1500.0,
        travel_pace="moderate",
    )
    assert "MODERATE / BALANCED" in prompt_mod
    assert "2 to 3 well-spaced activities" in prompt_mod


def test_prompt_empty_optional_preferences():
    """Verify prompt generation succeeds when dietary preferences and additional requirements are empty or None."""
    prompt = build_itinerary_prompt(
        destination="Barcelona, Spain",
        start_date="2027-07-10",
        end_date="2027-07-15",
        travel_style="leisure",
        travel_interests=["beaches"],
        num_travelers=1,
        budget=2000.0,
        travel_pace="moderate",
        dietary_preferences=None,
        additional_requirements=None,
    )
    assert "No special dietary restrictions specified." in prompt
    assert "No additional special requirements specified." in prompt
    assert "Solo Traveler" in prompt


def test_prompt_string_date_inputs():
    """Verify that ISO date strings are parsed and accepted cleanly."""
    prompt = build_itinerary_prompt(
        destination="Berlin, Germany",
        start_date="2027-08-01",
        end_date="2027-08-05",
        travel_style="cultural",
        travel_interests=["history", "museums"],
        num_travelers=3,
        budget=3000.0,
        travel_pace="moderate",
    )
    assert "Berlin, Germany" in prompt
    assert "5 Days (4 Nights)" in prompt
    assert "Group of 3" in prompt

