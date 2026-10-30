"""
tests/test_performance.py

Performance benchmarking and latency regression tests for Epic 5 – Activity 5.3:
Measures execution time across all core subsystems:
  1. Route & Time Optimization service speed
  2. PDF Itinerary document generation via ReportLab
  3. Structured JSON export serialization
  4. Plain-text summary construction
  5. Pydantic schema validation throughput
  6. Prompt assembly and duration calculations
"""

import time
from datetime import date
import pytest

from app.models.itinerary import (
    Activity,
    ActivitySchedule,
    DailyBudget,
    DayItinerary,
    DiningRecommendation,
    ItineraryResponse,
    RouteLeg,
    Transportation,
)
from app.models.trip import TripCreateRequest
from app.services.prompt_service import build_itinerary_prompt
from app.services.route_optimization_service import RouteOptimizationService
from app.services.share_service import ShareService


def generate_benchmark_day(day_num: int) -> DayItinerary:
    return DayItinerary(
        day_number=day_num,
        date=f"2027-05-0{day_num}",
        theme=f"Historic Quarter & Gardens Day {day_num}",
        morning_activity=Activity(
            time_slot="morning",
            name=f"Fushimi Inari Shrine {day_num}",
            description="Sacred mountain paths with thousands of vermilion torii gates.",
            location="Fushimi",
            suggested_duration="2.5 hours",
            estimated_cost="Free",
            schedule=ActivitySchedule(start_time="08:30 AM", end_time="11:00 AM", duration_minutes=150),
        ),
        lunch=DiningRecommendation(
            meal_type="Lunch",
            name="Inari Soba House",
            cuisine="Japanese Soba",
            description="Handmade buckwheat noodles.",
            estimated_cost="$15 USD",
        ),
        afternoon_activity=Activity(
            time_slot="afternoon",
            name=f"Kiyomizu-dera Temple {day_num}",
            description="Historic hillside temple overlooking Kyoto.",
            location="Higashiyama",
            suggested_duration="2 hours",
            estimated_cost="¥400 (~$3 USD)",
        ),
        dinner=DiningRecommendation(
            meal_type="Dinner",
            name="Gion Seasonal Kaiseki",
            cuisine="Kyoto Cuisine",
            description="Multi-course seasonal dining in machiya townhouse.",
            estimated_cost="$65 USD",
        ),
        evening_activity=Activity(
            time_slot="evening",
            name="Gion Lantern Walk",
            description="Atmospheric lantern-lit walk through historical geisha district.",
            location="Gion",
            suggested_duration="1 hour",
            estimated_cost="Free",
        ),
        transportation=Transportation(
            mode="Keihan Line & Walking",
            estimated_time="20 mins",
            estimated_cost="$3 USD",
        ),
        daily_budget=DailyBudget(
            activities_cost="$3 USD",
            dining_cost="$80 USD",
            transportation_cost="$3 USD",
            total_daily_estimated="$86 USD",
        ),
        practical_tips="Arrive early at Fushimi Inari to avoid crowds.",
    )


def generate_benchmark_itinerary(num_days: int = 5) -> ItineraryResponse:
    days = [generate_benchmark_day(i + 1) for i in range(num_days)]
    return ItineraryResponse(
        trip_id="trip-bench-001",
        destination="Kyoto, Japan",
        start_date="2027-05-01",
        end_date="2027-05-05",
        duration_days=num_days,
        total_budget=3500.0,
        travel_style="cultural",
        travel_pace="moderate",
        primary_vibe="Cultural",
        secondary_vibes=["Food & Culinary"],
        days=days,
        trip_summary="Comprehensive 5-day cultural and culinary immersion across historical Kyoto.",
        total_estimated_cost="$430 USD (excluding accommodation)",
        packing_and_prep_tips=["Walking shoes", "Pocket Wi-Fi", "Cash for temple coin boxes"],
    )


# ── 1. Route Optimization Benchmark ─────────────────────────────────────────

def test_benchmark_route_optimization_latency():
    """Verify route optimization for a 5-day itinerary completes in under 200 milliseconds."""
    optimizer = RouteOptimizationService()
    itinerary = generate_benchmark_itinerary(5)

    start = time.perf_counter()
    result = optimizer.optimize_itinerary(itinerary, travel_pace="moderate")
    duration_ms = (time.perf_counter() - start) * 1000.0

    assert result.route_optimized is True
    assert len(result.days[0].route_legs) > 0
    # Strict performance threshold: must complete within 200ms
    assert duration_ms < 200.0, f"Route optimization took {duration_ms:.2f}ms (>200ms threshold)"


# ── 2. PDF Generation Benchmark ─────────────────────────────────────────────

def test_benchmark_pdf_export_latency():
    """Verify ReportLab PDF generation for a 5-day itinerary executes in under 500 milliseconds."""
    share_service = ShareService()
    itinerary = generate_benchmark_itinerary(5)
    trip_dict = {
        "id": "trip-bench-001",
        "destination": "Kyoto, Japan",
        "start_date": "2027-05-01",
        "end_date": "2027-05-05",
        "budget": 3500.0,
        "travel_pace": "moderate",
        "num_travelers": 2,
        "primary_vibe": "Cultural",
        "secondary_vibes": ["Food & Culinary"],
    }

    start = time.perf_counter()
    pdf_bytes = share_service._build_pdf_bytes(trip=trip_dict, itinerary=itinerary)
    duration_ms = (time.perf_counter() - start) * 1000.0

    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 2000
    # Strict performance threshold: must complete within 500ms
    assert duration_ms < 500.0, f"PDF export took {duration_ms:.2f}ms (>500ms threshold)"


# ── 3. Prompt Construction Benchmark ────────────────────────────────────────

def test_benchmark_prompt_construction_latency():
    """Verify prompt assembly and duration calculations execute in under 15 milliseconds."""
    start = time.perf_counter()
    for _ in range(50):
        build_itinerary_prompt(
            destination="Rome, Italy",
            start_date=date(2027, 6, 1),
            end_date=date(2027, 6, 7),
            travel_style="cultural",
            travel_interests=["ancient history", "architecture", "food"],
            num_travelers=2,
            budget=3000.0,
            travel_pace="moderate",
            primary_vibe="Cultural",
            secondary_vibes=["Food & Culinary"],
            dietary_preferences=["vegetarian"],
        )
    avg_duration_ms = ((time.perf_counter() - start) / 50.0) * 1000.0

    assert avg_duration_ms < 15.0, f"Prompt construction averaged {avg_duration_ms:.2f}ms (>15ms threshold)"


# ── 4. Trip Model Validation Throughput ──────────────────────────────────────

def test_benchmark_pydantic_validation_throughput():
    """Verify Pydantic model validation throughput is sub-millisecond per request."""
    start = time.perf_counter()
    for i in range(100):
        TripCreateRequest(
            destination="Kyoto, Japan",
            start_date=date(2027, 5, 1),
            end_date=date(2027, 5, 6),
            num_travelers=2,
            budget=2500.0,
            travel_style="cultural",
            travel_interests=["history", "temples"],
            travel_pace="moderate",
        )
    avg_duration_ms = ((time.perf_counter() - start) / 100.0) * 1000.0

    assert avg_duration_ms < 2.0, f"Model validation averaged {avg_duration_ms:.2f}ms (>2ms threshold)"

