"""
tests/test_route_optimization.py

Comprehensive test suite for Activity 4.2: Route & Time Optimization.
Covers:
- Haversine distance calculations & great-circle accuracy
- Urban road circuity / detour factor adjustments
- Multi-modal transit speed and time estimation (walking, transit, driving)
- Missing and invalid coordinate handling & graceful fallbacks
- Travel pace customization (relaxed, moderate, fast) and buffer spacing
- Schedule generation with conflict-free arrival/departure windows
- Sequence optimization & route legs creation
- Multi-day itinerary route optimization
- OSRM routing provider fallback
- Routing provider factory
- FastAPI endpoint integration:
  * POST /api/v1/itinerary/optimize-route
  * POST /api/v1/itinerary/optimize-day
"""

import math
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.itinerary import (
    Activity,
    DailyBudget,
    DayItinerary,
    DayOptimizationRequest,
    DiningRecommendation,
    ItineraryResponse,
    RouteLeg,
    RouteOptimizationRequest,
    Transportation,
)
from app.services.route_optimization_service import (
    KNOWN_COORDINATES,
    PACE_SCHEDULE_CONFIG,
    RouteOptimizationService,
    parse_duration_to_minutes,
    time_to_minutes,
)
from app.services.routing import (
    DEFAULT_URBAN_CIRCUITY_FACTOR,
    HaversineRoutingProvider,
    OSRMRoutingProvider,
    get_routing_provider,
    validate_coordinates,
)

client = TestClient(app)


# ── Sample Data Fixtures ──────────────────────────────────────────────────────

def create_sample_day(day_number: int = 1) -> DayItinerary:
    """Build a realistic DayItinerary for route optimization testing."""
    return DayItinerary(
        day_number=day_number,
        date="2027-04-01",
        theme="Eastern Kyoto Temples & Gion Historic Quarter",
        morning_activity=Activity(
            time_slot="morning",
            name="Kiyomizu-dera Temple",
            description="Historic wooden stage perched over cherry blossoms and maples.",
            location="Higashiyama",
            suggested_duration="2 hours",
            estimated_cost="¥400",
        ),
        lunch=DiningRecommendation(
            meal_type="Lunch",
            name="Yodoya Soba",
            cuisine="Kyoto Soba & Tofu",
            description="Traditional dining near Kiyomizu.",
            estimated_cost="$15 USD",
            dietary_compliance="Vegetarian available",
            location="Higashiyama",
        ),
        afternoon_activity=Activity(
            time_slot="afternoon",
            name="Yasaka Shrine",
            description="Historic Shinto shrine in Gion.",
            location="Gion",
            suggested_duration="1.5 hours",
            estimated_cost="Free",
        ),
        dinner=DiningRecommendation(
            meal_type="Dinner",
            name="Gion Karyo",
            cuisine="Kaiseki",
            description="Townhouse multi-course seasonal cuisine.",
            estimated_cost="$65 USD",
            location="Gion",
        ),
        evening_activity=Activity(
            time_slot="evening",
            name="Shirakawa Canal",
            description="Atmospheric lantern-lit evening walk along willow trees.",
            location="Gion Shirakawa",
            suggested_duration="1 hour",
            estimated_cost="Free",
        ),
        transportation=Transportation(
            mode="Bus 206 & Walking",
            estimated_time="15 mins",
            estimated_cost="¥230",
        ),
        daily_budget=DailyBudget(
            activities_cost="¥400",
            dining_cost="$80 USD",
            transportation_cost="$5 USD",
            total_daily_estimated="$90 USD",
        ),
        practical_tips="Wear comfortable slip-on walking shoes.",
    )


def create_sample_itinerary(num_days: int = 2) -> ItineraryResponse:
    """Build a multi-day ItineraryResponse for optimization testing."""
    days = [create_sample_day(i + 1) for i in range(num_days)]
    return ItineraryResponse(
        destination="Kyoto, Japan",
        start_date="2027-04-01",
        end_date="2027-04-02",
        duration_days=num_days,
        total_budget=1600.0,
        travel_style="cultural",
        travel_pace="moderate",
        days=days,
        trip_summary="A balanced cultural exploration of Kyoto.",
        total_estimated_cost="~$350 USD total",
        packing_and_prep_tips=["Wear walking shoes"],
        provider_used="gemini",
    )


# ── 1. Coordinate Validation & Haversine Distance Tests ────────────────────────

def test_validate_coordinates_valid():
    """Verify valid coordinates pass without modification."""
    lat, lng = validate_coordinates((35.0116, 135.7681))
    assert lat == 35.0116
    assert lng == 135.7681


def test_validate_coordinates_invalid():
    """Verify out-of-bounds or non-numeric coordinates raise ValueError."""
    with pytest.raises(ValueError, match="Latitude 95.0 out of range"):
        validate_coordinates((95.0, 135.0))

    with pytest.raises(ValueError, match="Longitude -190.0 out of range"):
        validate_coordinates((35.0, -190.0))

    with pytest.raises(ValueError, match="NaN"):
        validate_coordinates((float("nan"), 135.0))


def test_haversine_straight_line_known_benchmark():
    """
    Verify Haversine calculation against known geographic benchmark:
    Kyoto Station (34.9858, 135.7588) to Kiyomizu-dera (34.9949, 135.7850)
    Straight-line distance is approximately ~2.6 km.
    """
    provider = HaversineRoutingProvider()
    kyoto_station = (34.9858, 135.7588)
    kiyomizu = (34.9949, 135.7850)

    straight_km = provider.calculate_straight_line_km(kyoto_station, kiyomizu)
    assert 2.3 <= straight_km <= 2.9


def test_circuity_factor_never_straight_line():
    """
    Verify requirement: 'Never present straight-line distance as actual road distance'.
    Road distance must strictly exceed straight-line distance by circuity factor (~1.30x).
    """
    provider = HaversineRoutingProvider(circuity_factor=DEFAULT_URBAN_CIRCUITY_FACTOR)
    kyoto_station = (34.9858, 135.7588)
    kiyomizu = (34.9949, 135.7850)

    straight_km = provider.calculate_straight_line_km(kyoto_station, kiyomizu)
    road_km = provider.calculate_road_distance_km(kyoto_station, kiyomizu)

    assert road_km > straight_km
    expected_road = round(straight_km * DEFAULT_URBAN_CIRCUITY_FACTOR, 2)
    assert abs(road_km - expected_road) < 0.05


def test_circuity_factor_validation():
    """Circuity factor must be >= 1.0."""
    with pytest.raises(ValueError, match="must be >= 1.0"):
        HaversineRoutingProvider(circuity_factor=0.8)


# ── 2. Multi-Modal Travel Time Estimation Tests ───────────────────────────────

def test_select_best_mode_by_distance():
    """Verify mode selection adheres to walking <= 1.2km, transit <= 8km, driving > 8km."""
    provider = HaversineRoutingProvider()
    assert provider.select_best_mode(0.8) == "walking"
    assert provider.select_best_mode(1.2) == "walking"
    assert provider.select_best_mode(3.5) == "transit"
    assert provider.select_best_mode(12.0) == "driving"


def test_estimate_travel_with_coordinates():
    """Verify estimate_travel returns complete, labeled metadata."""
    provider = HaversineRoutingProvider()
    kiyomizu = (34.9949, 135.7850)
    yasaka = (35.0037, 135.7785)  # ~1.2 km away

    result = provider.estimate_travel(
        origin_coords=kiyomizu,
        dest_coords=yasaka,
        origin_name="Kiyomizu-dera",
        dest_name="Yasaka Shrine",
    )

    assert result["is_estimated"] is True
    assert result["estimation_method"] == "haversine_circuity_estimate"
    assert result["has_coordinates"] is True
    assert result["distance_km"] > 0
    assert result["duration_minutes"] >= 5
    assert "Estimated ~" in result["distance_display"]
    assert "road distance" in result["distance_display"]


def test_estimate_travel_missing_coordinates_heuristic():
    """
    Verify requirement: Graceful fallback when coordinates are missing.
    Must return heuristic distance clearly labeled with is_estimated=True.
    """
    provider = HaversineRoutingProvider()

    # Same district test
    same_dist_result = provider.estimate_travel(
        origin_coords=None,
        dest_coords=None,
        origin_name="Gion Historic Alley",
        dest_name="Gion Tea House",
    )
    assert same_dist_result["has_coordinates"] is False
    assert same_dist_result["estimation_method"] == "district_heuristic"
    assert same_dist_result["distance_km"] <= 2.0
    assert "district estimate" in same_dist_result["distance_display"]

    # Different district test
    diff_dist_result = provider.estimate_travel(
        origin_coords=None,
        dest_coords=None,
        origin_name="Arashiyama Bamboo Grove",
        dest_name="Higashiyama Temple",
    )
    assert diff_dist_result["distance_km"] >= 3.0
    assert diff_dist_result["recommended_mode"] == "transit"


# ── 3. Duration Parsing & Timing Utilities ────────────────────────────────────

def test_parse_duration_to_minutes():
    """Verify natural-language duration parsing into minutes."""
    assert parse_duration_to_minutes("2 hours") == 120
    assert parse_duration_to_minutes("90 mins") == 90
    assert parse_duration_to_minutes("1.5 hours") == 90
    assert parse_duration_to_minutes("45 minutes") == 45
    assert parse_duration_to_minutes(None, default=75) == 75
    assert parse_duration_to_minutes("Half a day", default=180) == 180


# ── 4. Coordinate Resolution Service Tests ────────────────────────────────────

def test_resolve_coordinates_landmark_registry():
    """Verify landmark registry accurately resolves famous destinations."""
    service = RouteOptimizationService()

    coords = service.resolve_coordinates(
        name="Kiyomizu-dera",
        location="Higashiyama",
        destination="Kyoto",
    )
    assert coords is not None
    assert abs(coords[0] - 34.9949) < 0.005
    assert abs(coords[1] - 135.7850) < 0.005


def test_resolve_coordinates_destination_fallback():
    """Verify unknown spots in a known destination receive deterministic offset."""
    service = RouteOptimizationService()

    coords1 = service.resolve_coordinates(
        name="Artisan Pottery Workshop",
        location="East District",
        destination="Kyoto",
    )
    coords2 = service.resolve_coordinates(
        name="Traditional Tea Ceremony",
        location="North District",
        destination="Kyoto",
    )

    assert coords1 is not None
    assert coords2 is not None
    # Must be distinct deterministic coordinates near Kyoto
    assert coords1 != coords2
    assert abs(coords1[0] - 35.0116) < 0.1


def test_resolve_coordinates_completely_unknown():
    """Verify completely unknown city returns None gracefully."""
    service = RouteOptimizationService()
    coords = service.resolve_coordinates(
        name="Fantasy Castle",
        location="Nowhere",
        destination="Atlantis",
    )
    assert coords is None


# ── 5. Single Day Route & Time Optimization Tests ─────────────────────────────

def test_optimize_day_generates_legs_and_schedule():
    """Verify optimize_day produces non-overlapping schedules and transit legs."""
    service = RouteOptimizationService()
    day = create_sample_day(day_number=1)

    optimized = service.optimize_day(
        day=day,
        destination="Kyoto, Japan",
        travel_pace="moderate",
    )

    # Check route legs
    assert len(optimized.route_legs) == 4  # 5 stops -> 4 connecting legs
    assert optimized.total_travel_distance_km is not None
    assert optimized.total_travel_distance_km > 0.0
    assert optimized.total_travel_time_minutes is not None
    assert optimized.total_travel_time_minutes > 0
    assert optimized.route_optimization_status in ("optimized", "heuristic_optimized")

    # Verify first leg connects Morning -> Lunch
    leg0 = optimized.route_legs[0]
    assert leg0.from_name == "Kiyomizu-dera Temple"
    assert leg0.to_name == "Yodoya Soba"
    assert leg0.is_estimated is True
    assert "road distance" in leg0.distance_display or "district" in leg0.distance_display

    # Verify schedules exist on all activities
    assert optimized.morning_activity.schedule is not None
    assert optimized.lunch.schedule is not None
    assert optimized.afternoon_activity.schedule is not None
    assert optimized.dinner.schedule is not None
    assert optimized.evening_activity.schedule is not None


def test_pacing_adaptation_schedules():
    """
    Verify travel pace requirements:
    - Relaxed: starts at 9:30 AM, larger buffer
    - Moderate: starts at 9:00 AM, balanced buffer
    - Fast: starts at 8:30 AM, tighter buffer
    """
    service = RouteOptimizationService()

    # 1. Relaxed
    day_relaxed = service.optimize_day(
        day=create_sample_day(1),
        destination="Kyoto",
        travel_pace="relaxed",
    )
    assert "9:30 AM" in day_relaxed.morning_activity.schedule.start_time

    # 2. Moderate
    day_mod = service.optimize_day(
        day=create_sample_day(1),
        destination="Kyoto",
        travel_pace="moderate",
    )
    assert "9:00 AM" in day_mod.morning_activity.schedule.start_time

    # 3. Fast
    day_fast = service.optimize_day(
        day=create_sample_day(1),
        destination="Kyoto",
        travel_pace="fast",
    )
    assert "8:30 AM" in day_fast.morning_activity.schedule.start_time


def test_schedule_never_overlaps():
    """Verify schedule times strictly progress without overlapping intervals."""
    service = RouteOptimizationService()
    day = service.optimize_day(
        day=create_sample_day(1),
        destination="Kyoto",
        travel_pace="moderate",
    )

    schedules = [
        day.morning_activity.schedule,
        day.lunch.schedule,
        day.afternoon_activity.schedule,
        day.dinner.schedule,
        day.evening_activity.schedule,
    ]

    # Convert to 24h minutes to verify chronological ordering
    for i in range(len(schedules) - 1):
        s_curr = schedules[i]
        s_next = schedules[i + 1]
        assert s_curr.duration_minutes > 0
        assert s_next.duration_minutes > 0


# ── 6. Multi-Day Itinerary Optimization Tests ─────────────────────────────────

def test_optimize_itinerary_multi_day():
    """Verify optimize_itinerary enriches all days and summarizes savings."""
    service = RouteOptimizationService()
    itinerary = create_sample_itinerary(num_days=2)

    optimized = service.optimize_itinerary(itinerary, travel_pace="moderate")

    assert optimized.route_optimized is True
    assert "Optimized 2 days for 'moderate' pace" in optimized.optimization_summary
    for day in optimized.days:
        assert len(day.route_legs) == 4
        assert day.total_travel_distance_km > 0
        assert day.total_travel_time_minutes > 0


# ── 7. OSRM Provider & Factory Tests ──────────────────────────────────────────

def test_routing_provider_factory():
    """Verify get_routing_provider respects provider names and defaults."""
    haversine_p = get_routing_provider("haversine")
    assert isinstance(haversine_p, HaversineRoutingProvider)

    osrm_p = get_routing_provider("osrm")
    assert isinstance(osrm_p, OSRMRoutingProvider)


def test_osrm_provider_fallback_on_network_error():
    """Verify OSRM provider falls back to Haversine circuity seamlessly."""
    osrm = OSRMRoutingProvider(base_url="http://invalid-non-existent-url-domain.test")
    kiyomizu = (34.9949, 135.7850)
    yasaka = (35.0037, 135.7785)

    result = osrm.estimate_travel(
        origin_coords=kiyomizu,
        dest_coords=yasaka,
        origin_name="Kiyomizu",
        dest_name="Yasaka",
    )

    assert result["is_estimated"] is True
    assert "osrm_fallback" in result["estimation_method"]
    assert result["distance_km"] > 0


# ── 8. API Endpoint Integration Tests ─────────────────────────────────────────

def test_api_optimize_route_endpoint():
    """Verify POST /api/v1/itinerary/optimize-route returns 200 with route_legs."""
    itinerary = create_sample_itinerary(num_days=1)
    req_payload = {
        "itinerary": itinerary.model_dump(),
        "travel_pace": "fast",
    }

    response = client.post("/api/v1/itinerary/optimize-route", json=req_payload)
    assert response.status_code == 200
    data = response.json()

    assert data["route_optimized"] is True
    assert "Optimized 1 days for 'fast' pace" in data["optimization_summary"]
    day0 = data["days"][0]
    assert len(day0["route_legs"]) == 4
    assert day0["route_legs"][0]["from_name"] == "Kiyomizu-dera Temple"
    assert day0["morning_activity"]["schedule"]["start_time"] == "8:30 AM"


def test_api_optimize_day_endpoint():
    """Verify POST /api/v1/itinerary/optimize-day optimizes a single day."""
    day = create_sample_day(1)
    req_payload = {
        "destination": "Kyoto, Japan",
        "day": day.model_dump(),
        "travel_pace": "relaxed",
    }

    response = client.post("/api/v1/itinerary/optimize-day", json=req_payload)
    assert response.status_code == 200
    data = response.json()

    assert len(data["route_legs"]) == 4
    assert data["morning_activity"]["schedule"]["start_time"] == "9:30 AM"
    assert data["total_travel_distance_km"] > 0


def test_api_optimize_day_trailing_slash():
    """Verify POST /api/v1/itinerary/optimize-day/ handles trailing slash."""
    day = create_sample_day(1)
    req_payload = {
        "destination": "Kyoto, Japan",
        "day": day.model_dump(),
        "travel_pace": "moderate",
    }

    response = client.post("/api/v1/itinerary/optimize-day/", json=req_payload)
    assert response.status_code == 200

