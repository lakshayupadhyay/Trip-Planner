"""
tests/test_trip_models.py

Unit tests for Epic 3, Activity 3.1 Pydantic models:
- TripCreateRequest validation (dates, travelers, budget, style, interests)
- TripResponse serialization
- UserRegisterRequest (email, password length, full name)
- UserLoginRequest
- TokenResponse
"""

from datetime import date
import pytest
from pydantic import ValidationError

from app.models.trip import TripCreateRequest, TripResponse
from app.models.user import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
)


def test_valid_trip_create_request():
    """Verify that a well-formed trip payload validates successfully."""
    payload = {
        "user_id": "123e4567-e89b-12d3-a456-426614174000",
        "destination": "Kyoto, Japan",
        "start_date": date(2027, 4, 1),
        "end_date": date(2027, 4, 10),
        "num_travelers": 2,
        "budget": 3500.0,
        "travel_style": "cultural",
        "travel_interests": ["history", "food", "art"],
        "dietary_preferences": ["vegetarian"],
        "travel_pace": "moderate",
        "additional_requirements": "Near public transit",
    }
    trip = TripCreateRequest(**payload)
    assert trip.destination == "Kyoto, Japan"
    assert trip.num_travelers == 2
    assert trip.budget == 3500.0
    assert trip.travel_style == "cultural"
    assert trip.travel_pace == "moderate"


def test_invalid_dates_end_before_start():
    """Verify that end_date <= start_date raises a validation error."""
    payload = {
        "user_id": "test-user-id",
        "destination": "Paris, France",
        "start_date": date(2027, 6, 15),
        "end_date": date(2027, 6, 10),  # Before start date
        "num_travelers": 1,
        "budget": 2000.0,
        "travel_style": "relaxation",
        "travel_interests": ["beaches"],
        "travel_pace": "slow",
    }
    with pytest.raises(ValidationError) as exc_info:
        TripCreateRequest(**payload)
    assert "end_date" in str(exc_info.value)


def test_invalid_num_travelers():
    """Verify that num_travelers outside 1-20 is rejected."""
    payload = {
        "user_id": "test-user-id",
        "destination": "Rome, Italy",
        "start_date": date(2027, 5, 1),
        "end_date": date(2027, 5, 7),
        "num_travelers": 0,  # Invalid: below 1
        "budget": 1500.0,
        "travel_style": "cultural",
        "travel_interests": ["history"],
        "travel_pace": "moderate",
    }
    with pytest.raises(ValidationError):
        TripCreateRequest(**payload)

    payload["num_travelers"] = 25  # Invalid: above 20
    with pytest.raises(ValidationError):
        TripCreateRequest(**payload)


def test_invalid_budget():
    """Verify that budget <= 0 is rejected."""
    payload = {
        "user_id": "test-user-id",
        "destination": "Rome, Italy",
        "start_date": date(2027, 5, 1),
        "end_date": date(2027, 5, 7),
        "num_travelers": 2,
        "budget": 0.0,  # Invalid: must be > 0
        "travel_style": "cultural",
        "travel_interests": ["history"],
        "travel_pace": "moderate",
    }
    with pytest.raises(ValidationError):
        TripCreateRequest(**payload)


def test_invalid_travel_style():
    """Verify that unsupported travel_style literals are rejected."""
    payload = {
        "user_id": "test-user-id",
        "destination": "Tokyo, Japan",
        "start_date": date(2027, 7, 1),
        "end_date": date(2027, 7, 10),
        "num_travelers": 1,
        "budget": 2500.0,
        "travel_style": "extreme_sports",  # Not in allowed literals
        "travel_interests": ["sports"],
        "travel_pace": "fast",
    }
    with pytest.raises(ValidationError):
        TripCreateRequest(**payload)


def test_invalid_travel_interests_empty():
    """Verify that an empty list of travel interests is rejected."""
    payload = {
        "user_id": "test-user-id",
        "destination": "London, UK",
        "start_date": date(2027, 8, 1),
        "end_date": date(2027, 8, 5),
        "num_travelers": 1,
        "budget": 1800.0,
        "travel_style": "cultural",
        "travel_interests": [],  # Invalid: min 1 item
        "travel_pace": "moderate",
    }
    with pytest.raises(ValidationError):
        TripCreateRequest(**payload)


def test_valid_user_registration():
    """Verify user registration request validation."""
    user = UserRegisterRequest(
        email="traveler@example.com",
        password="securePassword123",
        full_name="Jane Doe",
    )
    assert user.email == "traveler@example.com"
    assert user.full_name == "Jane Doe"


def test_invalid_user_registration():
    """Verify weak passwords and invalid emails are rejected."""
    # Short password (< 8 chars)
    with pytest.raises(ValidationError):
        UserRegisterRequest(
            email="traveler@example.com",
            password="short",
            full_name="Jane Doe",
        )

    # Invalid email format
    with pytest.raises(ValidationError):
        UserRegisterRequest(
            email="not-an-email",
            password="securePassword123",
            full_name="Jane Doe",
        )


def test_trip_create_request_without_user_id():
    """Verify that user_id is optional in TripCreateRequest."""
    payload = {
        "destination": "Rome, Italy",
        "start_date": date(2027, 5, 1),
        "end_date": date(2027, 5, 7),
        "num_travelers": 2,
        "budget": 2000.0,
        "travel_style": "cultural",
        "travel_interests": ["history"],
        "travel_pace": "moderate",
    }
    trip = TripCreateRequest(**payload)
    assert trip.user_id is None
    assert trip.destination == "Rome, Italy"


def test_trip_create_request_normalization():
    """Verify travel_style and travel_pace case insensitivity and budget string cleaning."""
    payload = {
        "destination": "Sydney, Australia",
        "start_date": date(2027, 9, 1),
        "end_date": date(2027, 9, 10),
        "budget": "$4,500",  # String with $ and comma
        "travel_style": "ADVENTURE",  # Uppercase
        "travel_interests": ["nature", "beaches"],
        "travel_pace": "FAST",  # Uppercase
    }
    trip = TripCreateRequest(**payload)
    assert trip.travel_style == "adventure"
    assert trip.travel_pace == "fast"
    assert trip.budget == 4500.0


def test_token_response():
    """Verify TokenResponse serialization."""
    token = TokenResponse(
        access_token="sample-jwt-token",
        token_type="bearer",
        user_id="user-uuid-123",
    )
    assert token.token_type == "bearer"
    assert token.access_token == "sample-jwt-token"

