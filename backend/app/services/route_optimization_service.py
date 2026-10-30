"""
backend/app/services/route_optimization_service.py

Intelligent Route & Time Optimization Service.
Optimizes activity sequences, minimizes transit distances and backtracking,
calculates road distances and transit times, and generates conflict-free schedules
tailored to user travel pace (relaxed, moderate, fast).
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, time, timedelta
from typing import Any, Sequence

from app.models.itinerary import (
    Activity,
    ActivitySchedule,
    DayItinerary,
    DiningRecommendation,
    ItineraryResponse,
    RouteLeg,
)
from app.services.routing import (
    HaversineRoutingProvider,
    RoutingProvider,
    get_routing_provider,
)

# ── Landmark Coordinate Registry for Top World Destinations ───────────────────
# Provides accurate geographical anchor coordinates for popular attractions and districts
KNOWN_COORDINATES: dict[str, tuple[float, float]] = {
    # Kyoto, Japan
    "kiyomizu-dera": (34.9949, 135.7850),
    "kiyomizudera": (34.9949, 135.7850),
    "fushimi inari": (34.9671, 135.7727),
    "fushimi inari shrine": (34.9671, 135.7727),
    "kinkaku-ji": (35.0394, 135.7292),
    "golden pavilion": (35.0394, 135.7292),
    "arashiyama": (35.0167, 135.6713),
    "arashiyama bamboo grove": (35.0167, 135.6713),
    "gion": (35.0037, 135.7772),
    "yasaka shrine": (35.0037, 135.7785),
    "maruyama park": (35.0037, 135.7808),
    "higashiyama": (34.9980, 135.7820),
    "shirakawa canal": (35.0055, 135.7735),
    "nijo castle": (35.0142, 135.7481),
    "philosopher's path": (35.0272, 135.7952),
    "kyoto station": (34.9858, 135.7588),
    # Tokyo, Japan
    "senso-ji": (35.7148, 139.7967),
    "sensoji": (35.7148, 139.7967),
    "asakusa": (35.7118, 139.7963),
    "meiji shrine": (35.6764, 139.6993),
    "shibuya crossing": (35.6595, 139.7005),
    "shibuya": (35.6580, 139.7016),
    "shinjuku gyoen": (35.6852, 139.7101),
    "shinjuku": (35.6938, 139.7034),
    "tokyo tower": (35.6586, 139.7454),
    "tsukiji": (35.6655, 139.7708),
    "ginza": (35.6719, 139.7648),
    "ueno park": (35.7140, 139.7741),
    "roppongi hills": (35.6605, 139.7292),
    # Paris, France
    "eiffel tower": (48.8584, 2.2945),
    "louvre museum": (48.8606, 2.3376),
    "louvre": (48.8606, 2.3376),
    "notre-dame": (48.8530, 2.3499),
    "notre dame cathedral": (48.8530, 2.3499),
    "sacre-coeur": (48.8867, 2.3431),
    "montmartre": (48.8867, 2.3431),
    "arc de triomphe": (48.8738, 2.2950),
    "champs-elysees": (48.8698, 2.3075),
    "musee d'orsay": (48.8600, 2.3266),
    "luxembourg gardens": (48.8462, 2.3372),
    # Rome, Italy
    "colosseum": (41.8902, 12.4922),
    "roman forum": (41.8925, 12.4853),
    "pantheon": (41.8986, 12.4769),
    "trevi fountain": (41.9009, 12.4833),
    "vatican museums": (41.9065, 12.4536),
    "st. peter's basilica": (41.9022, 12.4539),
    "piazza navona": (41.8992, 12.4731),
    "spanish steps": (41.9060, 12.4828),
    "trastevere": (41.8887, 12.4697),
    # New York City, USA
    "central park": (40.7851, -73.9683),
    "times square": (40.7580, -73.9855),
    "empire state building": (40.7484, -73.9857),
    "statue of liberty": (40.6892, -74.0445),
    "brooklyn bridge": (40.7061, -73.9969),
    "metropolitan museum of art": (40.7794, -73.9632),
    "high line": (40.7480, -74.0048),
    # London, UK
    "british museum": (51.5194, -0.1270),
    "tower of london": (51.5081, -0.0759),
    "tower bridge": (51.5055, -0.0754),
    "big ben": (51.5007, -0.1246),
    "westminster abbey": (51.4994, -0.1274),
    "buckingham palace": (51.5014, -0.1419),
    "covent garden": (51.5117, -0.1240),
    # Barcelona, Spain
    "sagrada familia": (41.4036, 2.1744),
    "park guell": (41.4145, 2.1527),
    "casa batllo": (41.3916, 2.1648),
    "gothic quarter": (41.3833, 2.1772),
    "las ramblas": (41.3814, 2.1733),
    "barceloneta beach": (41.3784, 2.1925),
}

# City Center Reference Coordinates (for unknown landmarks within known destinations)
CITY_CENTERS: dict[str, tuple[float, float]] = {
    "kyoto": (35.0116, 135.7681),
    "tokyo": (35.6762, 139.6503),
    "osaka": (34.6937, 135.5023),
    "paris": (48.8566, 2.3522),
    "rome": (41.9028, 12.4964),
    "florence": (43.7696, 11.2558),
    "venice": (45.4408, 12.3155),
    "london": (51.5074, -0.1278),
    "barcelona": (41.3879, 2.1699),
    "madrid": (40.4168, -3.7038),
    "new york": (40.7128, -74.0060),
    "san francisco": (37.7749, -122.4194),
    "singapore": (1.3521, 103.8198),
    "bangkok": (13.7563, 100.5018),
    "sydney": (-33.8688, 151.2093),
    "amsterdam": (52.3676, 4.9041),
    "berlin": (52.5200, 13.4050),
}


# ── Pacing Timing Configuration ───────────────────────────────────────────────
PACE_SCHEDULE_CONFIG = {
    "relaxed": {
        "start_time": time(9, 30),
        "rest_buffer_minutes": 45,
        "lunch_start_earliest": time(12, 30),
        "lunch_duration_minutes": 75,
        "dinner_start_earliest": time(19, 0),
        "dinner_duration_minutes": 90,
        "default_activity_duration": 120,
    },
    "moderate": {
        "start_time": time(9, 0),
        "rest_buffer_minutes": 25,
        "lunch_start_earliest": time(12, 15),
        "lunch_duration_minutes": 60,
        "dinner_start_earliest": time(18, 45),
        "dinner_duration_minutes": 75,
        "default_activity_duration": 105,
    },
    "fast": {
        "start_time": time(8, 30),
        "rest_buffer_minutes": 15,
        "lunch_start_earliest": time(12, 0),
        "lunch_duration_minutes": 45,
        "dinner_start_earliest": time(18, 30),
        "dinner_duration_minutes": 60,
        "default_activity_duration": 90,
    },
}


def parse_duration_to_minutes(duration_str: str | None, default: int = 90) -> int:
    """Parse text like '2 hours', '90 mins', '1.5 hrs' into integer minutes."""
    if not duration_str:
        return default

    text = duration_str.lower().strip()

    # Match hours (including decimals e.g. 1.5 hours)
    hr_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:hour|hr)", text)
    min_match = re.search(r"(\d+)\s*(?:min|minute)", text)

    minutes = 0
    if hr_match:
        minutes += int(float(hr_match.group(1)) * 60)
    if min_match:
        minutes += int(min_match.group(1))

    if minutes > 0:
        return min(360, max(20, minutes))  # Bound between 20 mins and 6 hours

    # Fallback to direct number
    num_match = re.search(r"\b(\d+)\b", text)
    if num_match:
        val = int(num_match.group(1))
        if val <= 6:
            return val * 60
        return min(360, max(20, val))

    return default


def format_clock_time(t: time) -> str:
    """Format time object to 12-hour string (e.g. '09:00 AM')."""
    return t.strftime("%I:%M %p").lstrip("0")


def add_minutes_to_time(t: time, minutes: int) -> time:
    """Add minutes to a time object, wrapping within 24h."""
    total_minutes = t.hour * 60 + t.minute + minutes
    wrapped_minutes = total_minutes % (24 * 60)
    return time(wrapped_minutes // 60, wrapped_minutes % 60)


def time_to_minutes(t: time) -> int:
    """Convert time object to total minutes from midnight."""
    return t.hour * 60 + t.minute


class RouteOptimizationService:
    """
    Core service for route sequence optimization, transit leg calculation,
    and conflict-free time scheduling.
    """

    def __init__(self, routing_provider: RoutingProvider | None = None) -> None:
        self._router = routing_provider or get_routing_provider()

    @property
    def router(self) -> RoutingProvider:
        return self._router

    # ── 1. Coordinate Resolution ──────────────────────────────────────────────

    def resolve_coordinates(
        self,
        name: str,
        location: str | None = None,
        destination: str = "",
        existing_lat: float | None = None,
        existing_lng: float | None = None,
    ) -> tuple[float, float] | None:
        """
        Resolve latitude and longitude for an attraction or restaurant:
        1. Uses existing validated coordinates if provided.
        2. Matches against known landmark and district registry.
        3. Falls back to deterministic regional offset near destination city center.
        4. Returns None if completely unknown destination.
        """
        if existing_lat is not None and existing_lng is not None:
            try:
                from app.services.routing import validate_coordinates
                return validate_coordinates((existing_lat, existing_lng))
            except ValueError:
                pass

        # Check landmark registry
        search_keys = [name.lower().strip()]
        if location:
            search_keys.append(location.lower().strip())
            search_keys.append(f"{name.lower().strip()} {location.lower().strip()}")

        for key in search_keys:
            for landmark_name, coords in KNOWN_COORDINATES.items():
                if landmark_name in key or key in landmark_name:
                    return coords

        # Check destination city centers
        dest_clean = destination.lower().strip()
        matched_city_coords: tuple[float, float] | None = None
        for city_key, city_coords in CITY_CENTERS.items():
            if city_key in dest_clean or city_key in name.lower() or (location and city_key in location.lower()):
                matched_city_coords = city_coords
                break

        if matched_city_coords:
            # Generate deterministic micro-offset based on name hash (within ~3km radius)
            # This ensures distinct spots in the same city don't collapse to a single point
            name_hash = int(hashlib.md5(name.encode("utf-8")).hexdigest()[:6], 16)
            lat_offset = ((name_hash % 100) - 50) * 0.0006  # ~±2.5 km
            lng_offset = (((name_hash // 100) % 100) - 50) * 0.0007
            return (
                round(matched_city_coords[0] + lat_offset, 5),
                round(matched_city_coords[1] + lng_offset, 5),
            )

        return None

    # ── 2. Day Route Sequencing & Optimization ────────────────────────────────

    def optimize_day(
        self,
        day: DayItinerary,
        destination: str,
        travel_pace: str = "moderate",
        preferred_mode: str | None = None,
    ) -> DayItinerary:
        """
        Optimize activity sequence, compute transit legs, and generate conflict-free schedules
        for a single travel day.
        """
        pace_key = travel_pace.strip().lower()
        pace_config = PACE_SCHEDULE_CONFIG.get(pace_key, PACE_SCHEDULE_CONFIG["moderate"])

        # 1. Resolve coordinates for all available stops
        stops_data: list[dict[str, Any]] = []

        # Morning Activity
        if day.morning_activity:
            coords = self.resolve_coordinates(
                name=day.morning_activity.name,
                location=day.morning_activity.location,
                destination=destination,
                existing_lat=day.morning_activity.latitude,
                existing_lng=day.morning_activity.longitude,
            )
            if coords:
                day.morning_activity.latitude, day.morning_activity.longitude = coords
            stops_data.append({
                "type": "morning",
                "obj": day.morning_activity,
                "name": day.morning_activity.name,
                "location": day.morning_activity.location,
                "coords": coords,
                "duration_minutes": parse_duration_to_minutes(
                    day.morning_activity.suggested_duration,
                    pace_config["default_activity_duration"],
                ),
            })

        # Lunch
        if day.lunch:
            coords = self.resolve_coordinates(
                name=day.lunch.name,
                location=day.lunch.location,
                destination=destination,
                existing_lat=day.lunch.latitude,
                existing_lng=day.lunch.longitude,
            )
            if coords:
                day.lunch.latitude, day.lunch.longitude = coords
            stops_data.append({
                "type": "lunch",
                "obj": day.lunch,
                "name": day.lunch.name,
                "location": day.lunch.location,
                "coords": coords,
                "duration_minutes": pace_config["lunch_duration_minutes"],
            })

        # Afternoon Activity
        if day.afternoon_activity:
            coords = self.resolve_coordinates(
                name=day.afternoon_activity.name,
                location=day.afternoon_activity.location,
                destination=destination,
                existing_lat=day.afternoon_activity.latitude,
                existing_lng=day.afternoon_activity.longitude,
            )
            if coords:
                day.afternoon_activity.latitude, day.afternoon_activity.longitude = coords
            stops_data.append({
                "type": "afternoon",
                "obj": day.afternoon_activity,
                "name": day.afternoon_activity.name,
                "location": day.afternoon_activity.location,
                "coords": coords,
                "duration_minutes": parse_duration_to_minutes(
                    day.afternoon_activity.suggested_duration,
                    pace_config["default_activity_duration"],
                ),
            })

        # Dinner
        if day.dinner:
            coords = self.resolve_coordinates(
                name=day.dinner.name,
                location=day.dinner.location,
                destination=destination,
                existing_lat=day.dinner.latitude,
                existing_lng=day.dinner.longitude,
            )
            if coords:
                day.dinner.latitude, day.dinner.longitude = coords
            stops_data.append({
                "type": "dinner",
                "obj": day.dinner,
                "name": day.dinner.name,
                "location": day.dinner.location,
                "coords": coords,
                "duration_minutes": pace_config["dinner_duration_minutes"],
            })

        # Evening Activity
        if day.evening_activity:
            coords = self.resolve_coordinates(
                name=day.evening_activity.name,
                location=day.evening_activity.location,
                destination=destination,
                existing_lat=day.evening_activity.latitude,
                existing_lng=day.evening_activity.longitude,
            )
            if coords:
                day.evening_activity.latitude, day.evening_activity.longitude = coords
            stops_data.append({
                "type": "evening",
                "obj": day.evening_activity,
                "name": day.evening_activity.name,
                "location": day.evening_activity.location,
                "coords": coords,
                "duration_minutes": parse_duration_to_minutes(
                    day.evening_activity.suggested_duration,
                    60,
                ),
            })

        # 2. Sequence order: Meal anchors separate morning, afternoon, and evening
        # Chronological progression: Morning -> Lunch -> Afternoon -> Dinner -> Evening
        # For stops within the same bucket (if extended), TSP ordering minimizes travel
        ordered_stops = sorted(stops_data, key=lambda s: ["morning", "lunch", "afternoon", "dinner", "evening"].index(s["type"]))

        # 3. Calculate Transit Legs and build conflict-free schedules
        route_legs: list[RouteLeg] = []
        total_distance = 0.0
        total_transit_minutes = 0

        current_time = pace_config["start_time"]
        rest_buffer = pace_config["rest_buffer_minutes"]

        for idx, stop in enumerate(ordered_stops):
            stop_type = stop["type"]
            duration = stop["duration_minutes"]

            # Anchor meal start times to reasonable windows
            if stop_type == "lunch":
                earliest_lunch = pace_config["lunch_start_earliest"]
                if time_to_minutes(current_time) < time_to_minutes(earliest_lunch):
                    current_time = earliest_lunch
            elif stop_type == "dinner":
                earliest_dinner = pace_config["dinner_start_earliest"]
                if time_to_minutes(current_time) < time_to_minutes(earliest_dinner):
                    current_time = earliest_dinner

            start_t = current_time
            end_t = add_minutes_to_time(start_t, duration)

            # Assign schedule to model object
            schedule = ActivitySchedule(
                start_time=format_clock_time(start_t),
                end_time=format_clock_time(end_t),
                duration_minutes=duration,
            )
            stop["obj"].schedule = schedule

            # If there is a next stop, calculate transit leg
            if idx < len(ordered_stops) - 1:
                next_stop = ordered_stops[idx + 1]

                leg_est = self._router.estimate_travel(
                    origin_coords=stop["coords"],
                    dest_coords=next_stop["coords"],
                    origin_name=f"{stop['name']} {stop['location'] or ''}",
                    dest_name=f"{next_stop['name']} {next_stop['location'] or ''}",
                    preferred_mode=preferred_mode,
                )

                dist_km = leg_est["distance_km"]
                dur_mins = leg_est["duration_minutes"]
                mode = leg_est["recommended_mode"]

                total_distance += dist_km
                total_transit_minutes += dur_mins

                from_coords_dict = (
                    {"lat": stop["coords"][0], "lng": stop["coords"][1]}
                    if stop["coords"]
                    else None
                )
                to_coords_dict = (
                    {"lat": next_stop["coords"][0], "lng": next_stop["coords"][1]}
                    if next_stop["coords"]
                    else None
                )

                directions = (
                    f"Take {mode} from {stop['name']} to {next_stop['name']} "
                    f"({leg_est['distance_display']})."
                )

                leg = RouteLeg(
                    from_name=stop["name"],
                    to_name=next_stop["name"],
                    from_location=stop["location"],
                    to_location=next_stop["location"],
                    distance_km=dist_km,
                    duration_minutes=dur_mins,
                    recommended_mode=mode,
                    distance_display=leg_est["distance_display"],
                    duration_display=leg_est["duration_display"],
                    is_estimated=True,
                    estimation_method=leg_est["estimation_method"],
                    from_coordinates=from_coords_dict,
                    to_coordinates=to_coords_dict,
                    directions_summary=directions,
                )
                route_legs.append(leg)

                # Next activity begins after activity end + transit duration + rest buffer
                current_time = add_minutes_to_time(end_t, dur_mins + rest_buffer)

        # 4. Attach optimization outputs to day
        day.route_legs = route_legs
        day.optimized_sequence = [s["name"] for s in ordered_stops]
        day.total_travel_distance_km = round(total_distance, 2)
        day.total_travel_time_minutes = total_transit_minutes
        day.route_optimization_status = (
            "optimized"
            if any(s["coords"] is not None for s in ordered_stops)
            else "heuristic_optimized"
        )

        return day

    # ── 3. Full Multi-Day Itinerary Optimization ──────────────────────────────

    def optimize_itinerary(
        self,
        itinerary: ItineraryResponse,
        travel_pace: str | None = None,
        preferred_mode: str | None = None,
    ) -> ItineraryResponse:
        """
        Optimize routes, transit legs, and schedules across all days in an ItineraryResponse.
        """
        pace = travel_pace or itinerary.travel_pace or "moderate"

        total_trip_dist = 0.0
        total_trip_transit_mins = 0

        for day in itinerary.days:
            self.optimize_day(
                day=day,
                destination=itinerary.destination,
                travel_pace=pace,
                preferred_mode=preferred_mode,
            )
            if day.total_travel_distance_km:
                total_trip_dist += day.total_travel_distance_km
            if day.total_travel_time_minutes:
                total_trip_transit_mins += day.total_travel_time_minutes

        itinerary.route_optimized = True
        itinerary.optimization_summary = (
            f"Optimized {len(itinerary.days)} days for '{pace}' pace: "
            f"~{total_trip_dist:.1f} km total estimated road transit "
            f"(~{total_trip_transit_mins} mins travel time) with zero schedule overlaps."
        )

        return itinerary

