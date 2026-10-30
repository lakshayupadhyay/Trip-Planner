"""
backend/app/services/routing/__init__.py

Routing and distance calculation abstractions and providers.
"""

from app.services.routing.base import RoutingProvider
from app.services.routing.haversine_provider import (
    HaversineRoutingProvider,
    validate_coordinates,
    DEFAULT_URBAN_CIRCUITY_FACTOR,
)
from app.services.routing.osrm_provider import OSRMRoutingProvider
from app.services.routing.factory import get_routing_provider

__all__ = [
    "RoutingProvider",
    "HaversineRoutingProvider",
    "OSRMRoutingProvider",
    "get_routing_provider",
    "validate_coordinates",
    "DEFAULT_URBAN_CIRCUITY_FACTOR",
]

