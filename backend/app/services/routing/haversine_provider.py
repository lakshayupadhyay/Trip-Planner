"""
backend/app/services/routing/haversine_provider.py

Self-contained Haversine routing provider with realistic urban circuity factor
and multi-modal travel time estimation (walking, public transit, driving).
Zero paid external API dependencies.
"""

from __future__ import annotations

import math
from typing import Any

from app.services.routing.base import RoutingProvider

# Earth radius in kilometers (WGS-84 mean radius)
EARTH_RADIUS_KM = 6371.0088

# Average urban circuity / detour factor (road distance vs straight-line)
# Empirical urban studies (Levinson & El-Geneidy, Ballou et al.) establish 1.25 to 1.41
DEFAULT_URBAN_CIRCUITY_FACTOR = 1.30

# Multi-modal travel speeds (km/h) and initial boarding/wait buffers (minutes)
MODAL_PROFILES = {
    "walking": {
        "speed_kmh": 4.8,
        "buffer_mins": 2,
        "max_recommended_km": 1.5,
    },
    "transit": {
        "speed_kmh": 22.0,
        "buffer_mins": 6,
        "max_recommended_km": 25.0,
    },
    "driving": {
        "speed_kmh": 28.0,
        "buffer_mins": 4,
        "max_recommended_km": 100.0,
    },
}


def validate_coordinates(coords: tuple[float, float]) -> tuple[float, float]:
    """Validate latitude [-90, 90] and longitude [-180, 180]."""
    lat, lng = coords
    if not (isinstance(lat, (int, float)) and isinstance(lng, (int, float))):
        raise ValueError(f"Coordinates must be numeric, got ({type(lat)}, {type(lng)})")
    if math.isnan(lat) or math.isnan(lng) or math.isinf(lat) or math.isinf(lng):
        raise ValueError(f"Coordinates cannot be NaN or infinite: ({lat}, {lng})")
    if not (-90.0 <= lat <= 90.0):
        raise ValueError(f"Latitude {lat} out of range [-90, 90]")
    if not (-180.0 <= lng <= 180.0):
        raise ValueError(f"Longitude {lng} out of range [-180, 180]")
    return float(lat), float(lng)


class HaversineRoutingProvider(RoutingProvider):
    """
    Standard mathematical routing provider calculating great-circle distance
    adjusted by urban circuity factors for accurate road distance modeling.
    """

    def __init__(self, circuity_factor: float = DEFAULT_URBAN_CIRCUITY_FACTOR) -> None:
        if circuity_factor < 1.0:
            raise ValueError("Circuity factor must be >= 1.0 (road distance cannot be shorter than straight-line)")
        self._circuity_factor = circuity_factor

    @property
    def name(self) -> str:
        return "haversine_circuity"

    @property
    def circuity_factor(self) -> float:
        return self._circuity_factor

    def calculate_straight_line_km(
        self,
        origin: tuple[float, float],
        destination: tuple[float, float],
    ) -> float:
        """
        Calculate spherical distance between two coordinates using the Haversine formula.
        """
        lat1, lng1 = validate_coordinates(origin)
        lat2, lng2 = validate_coordinates(destination)

        # Convert decimal degrees to radians
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lng2 - lng1)

        # Haversine formula
        a = (
            math.sin(delta_phi / 2.0) ** 2
            + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2)
        )
        # Avoid potential floating point roundoff outside [0, 1]
        a = min(1.0, max(0.0, a))
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

        distance = EARTH_RADIUS_KM * c
        return round(distance, 4)

    def calculate_road_distance_km(
        self,
        origin: tuple[float, float],
        destination: tuple[float, float],
    ) -> float:
        """
        Calculate realistic estimated road network distance using the urban circuity factor.
        Never presents straight-line distance as road distance.
        """
        straight_km = self.calculate_straight_line_km(origin, destination)
        if straight_km == 0.0:
            return 0.0
        road_km = straight_km * self._circuity_factor
        return round(road_km, 2)

    def select_best_mode(
        self,
        distance_km: float,
        preferred_mode: str | None = None,
    ) -> str:
        """Select recommended transit mode based on distance and preferences."""
        if preferred_mode:
            normalized = preferred_mode.strip().lower()
            if normalized in MODAL_PROFILES:
                return normalized

        if distance_km <= 1.2:
            return "walking"
        elif distance_km <= 8.0:
            return "transit"
        else:
            return "driving"

    def estimate_travel_duration_minutes(
        self,
        distance_km: float,
        mode: str = "transit",
    ) -> int:
        """
        Estimate transit duration in minutes for a given road distance and mode.
        Includes modal acceleration/wait buffers.
        """
        profile = MODAL_PROFILES.get(mode, MODAL_PROFILES["transit"])
        speed = profile["speed_kmh"]
        buffer_mins = profile["buffer_mins"]

        if distance_km <= 0.05:
            return 1

        # Travel time in minutes
        raw_minutes = (distance_km / speed) * 60.0 + buffer_mins
        return max(1, int(round(raw_minutes)))

    def estimate_travel(
        self,
        origin_coords: tuple[float, float] | None,
        dest_coords: tuple[float, float] | None,
        origin_name: str = "",
        dest_name: str = "",
        preferred_mode: str | None = None,
    ) -> dict[str, Any]:
        """
        Calculate complete travel estimation. Gracefully handles missing coordinates
        via district and location heuristic modeling.
        """
        # Case A: Both coordinates available
        if origin_coords is not None and dest_coords is not None:
            try:
                straight_line_km = self.calculate_straight_line_km(origin_coords, dest_coords)
                road_distance_km = self.calculate_road_distance_km(origin_coords, dest_coords)
                mode = self.select_best_mode(road_distance_km, preferred_mode)
                duration_mins = self.estimate_travel_duration_minutes(road_distance_km, mode)

                return {
                    "distance_km": road_distance_km,
                    "straight_line_km": straight_line_km,
                    "duration_minutes": duration_mins,
                    "recommended_mode": mode,
                    "distance_display": f"Estimated ~{road_distance_km:.1f} km road distance",
                    "duration_display": f"Estimated ~{duration_mins} mins {mode}",
                    "is_estimated": True,
                    "estimation_method": "haversine_circuity_estimate",
                    "circuity_factor": self._circuity_factor,
                    "has_coordinates": True,
                }
            except ValueError:
                # If coordinates fail validation, fall back to heuristic
                pass

        # Case B: Heuristic fallback when coordinates are missing or invalid
        # Check if locations appear to be in the same district/neighborhood
        same_district = self._detect_same_district(origin_name, dest_name)

        if same_district:
            road_distance_km = 1.1
            mode = preferred_mode or "walking"
            duration_mins = 14
        else:
            road_distance_km = 4.6
            mode = preferred_mode or "transit"
            duration_mins = 22

        return {
            "distance_km": road_distance_km,
            "straight_line_km": round(road_distance_km / self._circuity_factor, 2),
            "duration_minutes": duration_mins,
            "recommended_mode": mode,
            "distance_display": f"Estimated ~{road_distance_km:.1f} km (district estimate)",
            "duration_display": f"Estimated ~{duration_mins} mins {mode}",
            "is_estimated": True,
            "estimation_method": "district_heuristic",
            "circuity_factor": self._circuity_factor,
            "has_coordinates": False,
        }

    def _detect_same_district(self, name_a: str, name_b: str) -> bool:
        """Determine if two location strings likely share the same neighborhood or area."""
        if not name_a or not name_b:
            return False
        tokens_a = set(name_a.lower().replace(",", " ").replace("-", " ").split())
        tokens_b = set(name_b.lower().replace(",", " ").replace("-", " ").split())
        common = tokens_a.intersection(tokens_b)
        # Filter out trivial stop words
        stop_words = {"the", "and", "or", "in", "at", "of", "to", "st", "ave", "road", "street", "city", "park"}
        meaningful = {w for w in common if w not in stop_words and len(w) > 2}
        return len(meaningful) > 0

