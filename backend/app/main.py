"""
Personalized Travel Itinerary Planner - FastAPI Backend
Entry point for the backend application.
"""

import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Personalized Travel Itinerary Planner API",
    description="Backend API for generating personalized travel itineraries",
    version="0.1.0",
    debug=settings.DEBUG,
)

# Allow requests from the React frontend during development and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Measure server processing time and attach X-Process-Time-Ms header."""
    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start_time) * 1000.0
    response.headers["X-Process-Time-Ms"] = f"{duration_ms:.2f}"
    return response


@app.get("/")
def root():
    """Health check endpoint."""
    return {"message": "Travel Planner API is running!", "status": "ok"}


@app.get("/health")
def health_check():
    """Detailed health check."""
    return {"status": "healthy", "version": "0.1.0"}


@app.get("/health/db")
def db_health_check():
    """
    Tests whether the Supabase connection is alive.

    SAFETY: Returns only a pass/fail status.
             Never exposes credentials, keys, or row data.

    HOW IT WORKS:
        Attempts a lightweight query against Supabase.
        If the client was not configured (missing env vars), the import
        itself raises an EnvironmentError — caught and returned as a
        clear error message.
    """
    try:
        from app.utils.supabase_client import supabase

        # Run a minimal query — fetches 1 row from the first available table.
        # Change "users" to any table name that exists in your Supabase project.
        response = supabase.table("users").select("id").limit(1).execute()

        return {
            "status": "connected",
            "message": "Supabase connection is healthy.",
            "rows_returned": len(response.data),
        }

    except EnvironmentError as env_err:
        # Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env
        return {
            "status": "misconfigured",
            "message": str(env_err),
        }

    except Exception as err:
        # Connection failed (wrong URL, wrong key, network error, etc.)
        return {
            "status": "error",
            "message": f"Database connection failed ({type(err).__name__}).",
        }


# ── API Routers ────────────────────────────────────────────────────────────
from app.api import trips, itinerary, recommendations, share

app.include_router(trips.router, prefix="/api/v1/trips", tags=["trips"])
app.include_router(itinerary.router, prefix="/api/v1/itinerary", tags=["itinerary"])
app.include_router(recommendations.router, prefix="/api/v1/recommendations", tags=["recommendations"])
app.include_router(share.router, prefix="/api/v1", tags=["share-export"])


# Future routers will be included here:
# from app.api import users
# app.include_router(users.router,     prefix="/api/v1")

