"""
backend/app/services/routing/base.py

Abstract base class for routing and travel distance/time providers.
Defines standard interfaces for distance calculation, travel time estimation,
and multi-modal transit analysis.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class RoutingProvider(ABC):
    """
    Abstract interface for routing, road distance calculation,
    and travel-time estimation.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the routing provider."""
        raise NotImplementedError

    @abstractmethod
    def calculate_straight_line_km(
        self,
        origin: tuple[float, float],
        destination: tuple[float, float],
    ) -> float:
        """
        Calculate the great-circle (Haversine) straight-line distance in kilometers
        between two (latitude, longitude) coordinate pairs.
        """
        raise NotImplementedError

    @abstractmethod
    def calculate_road_distance_km(
        self,
        origin: tuple[float, float],
        destination: tuple[float, float],
    ) -> float:
        """
        Calculate the realistic road distance in kilometers between two points,
        applying an urban road circuity/detour index.
        Never returns straight-line distance as road distance.
        """
        raise NotImplementedError

    @abstractmethod
    def estimate_travel(
        self,
        origin_coords: tuple[float, float] | None,
        dest_coords: tuple[float, float] | None,
        origin_name: str = "",
        dest_name: str = "",
        preferred_mode: str | None = None,
    ) -> dict[str, Any]:
        """
        Estimate distance, transit duration, and recommended mode between two locations.
        Must handle None coordinates gracefully via heuristic estimation.
        Always returns is_estimated=True and explicit estimation_method.
        """
        raise NotImplementedError

