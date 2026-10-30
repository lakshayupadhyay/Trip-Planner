"""
backend/app/services/routing/osrm_provider.py

OpenStreetMap (OSRM) Routing Provider with seamless fallback to Haversine circuity.
Designed to query public or self-hosted OSRM instances if available,
with strict timeouts and automatic graceful fallback.
"""

from __future__ import annotations

import logging
from typing import Any
import httpx

from app.services.routing.base import RoutingProvider
from app.services.routing.haversine_provider import HaversineRoutingProvider

logger = logging.getLogger(__name__)


class OSRMRoutingProvider(RoutingProvider):
    """
    OSRM-backed routing provider. Queries OSRM road geometry when available;
    falls back cleanly to HaversineRoutingProvider on any timeout or network error.
    """

    def __init__(
        self,
        base_url: str = "https://router.project-osrm.org",
        timeout_seconds: float = 2.5,
        fallback_provider: HaversineRoutingProvider | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds
        self._fallback = fallback_provider or HaversineRoutingProvider()

    @property
    def name(self) -> str:
        return "osrm"

    def calculate_straight_line_km(
        self,
        origin: tuple[float, float],
        destination: tuple[float, float],
    ) -> float:
        return self._fallback.calculate_straight_line_km(origin, destination)

    def calculate_road_distance_km(
        self,
        origin: tuple[float, float],
        destination: tuple[float, float],
    ) -> float:
        return self._fallback.calculate_road_distance_km(origin, destination)

    def estimate_travel(
        self,
        origin_coords: tuple[float, float] | None,
        dest_coords: tuple[float, float] | None,
        origin_name: str = "",
        dest_name: str = "",
        preferred_mode: str | None = None,
    ) -> dict[str, Any]:
        """
        Attempt OSRM route calculation. Falls back gracefully to Haversine
        if coordinates are missing, network is unavailable, or request times out.
        """
        if origin_coords is None or dest_coords is None:
            return self._fallback.estimate_travel(
                origin_coords, dest_coords, origin_name, dest_name, preferred_mode
            )

        lat1, lng1 = origin_coords
        lat2, lng2 = dest_coords

        # OSRM expects coordinates in {longitude},{latitude} format
        mode_profile = "driving" if preferred_mode == "driving" else "walking" if preferred_mode == "walking" else "driving"
        url = f"{self._base_url}/route/v1/{mode_profile}/{lng1},{lat1};{lng2},{lat2}?overview=false"

        try:
            with httpx.Client(timeout=self._timeout) as client:
                resp = client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    routes = data.get("routes", [])
                    if routes:
                        primary = routes[0]
                        distance_meters = primary.get("distance", 0.0)
                        duration_seconds = primary.get("duration", 0.0)

                        dist_km = round(distance_meters / 1000.0, 2)
                        dur_mins = max(1, int(round(duration_seconds / 60.0)))
                        mode = preferred_mode or ("walking" if dist_km <= 1.2 else "transit")

                        return {
                            "distance_km": dist_km,
                            "straight_line_km": self.calculate_straight_line_km(origin_coords, dest_coords),
                            "duration_minutes": dur_mins,
                            "recommended_mode": mode,
                            "distance_display": f"Estimated ~{dist_km:.1f} km (OSRM road network)",
                            "duration_display": f"Estimated ~{dur_mins} mins {mode}",
                            "is_estimated": True,
                            "estimation_method": "osrm_road_network",
                            "circuity_factor": self._fallback.circuity_factor,
                            "has_coordinates": True,
                        }
        except Exception as exc:
            logger.debug("OSRM lookup failed (%s); using Haversine fallback.", exc)

        # Fallback to Haversine calculation
        result = self._fallback.estimate_travel(
            origin_coords, dest_coords, origin_name, dest_name, preferred_mode
        )
        result["estimation_method"] = "haversine_circuity_estimate (osrm_fallback)"
        return result

