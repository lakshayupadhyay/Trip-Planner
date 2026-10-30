"""
backend/app/services/routing/factory.py

Factory method to obtain configurable routing providers.
"""

from __future__ import annotations

import os
from app.services.routing.base import RoutingProvider
from app.services.routing.haversine_provider import HaversineRoutingProvider
from app.services.routing.osrm_provider import OSRMRoutingProvider


def get_routing_provider(provider_type: str | None = None) -> RoutingProvider:
    """
    Return routing provider based on argument or ROUTING_PROVIDER environment variable.
    Defaults to HaversineRoutingProvider (zero external dependencies).
    """
    resolved_type = (provider_type or os.getenv("ROUTING_PROVIDER", "haversine")).strip().lower()

    if resolved_type in ("osrm", "openstreetmap"):
        return OSRMRoutingProvider()
    return HaversineRoutingProvider()

