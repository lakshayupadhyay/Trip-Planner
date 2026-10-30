"""
api/__init__.py
Registers all API routers for the FastAPI application.
"""

from app.api import trips, itinerary, recommendations, share

__all__ = ["trips", "itinerary", "recommendations", "share"]
