"""
backend/app/api/share.py

API router for Trip Sharing, Read-only Public Viewing, and Exporting (PDF, JSON, Summary).

Endpoints:
  POST   /api/v1/trips/{trip_id}/share       - Generate or get shareable link
  DELETE /api/v1/trips/{trip_id}/share       - Revoke shareable link
  GET    /api/v1/shared/{share_token}        - Read-only public trip & itinerary
  GET    /api/v1/trips/{trip_id}/export/pdf  - Export itinerary as PDF
  GET    /api/v1/trips/{trip_id}/export/json - Export itinerary as JSON
  POST   /api/v1/trips/{trip_id}/summary     - Generate structured & clipboard summary
"""

from __future__ import annotations

import re
from fastapi import APIRouter, Header, HTTPException, Query, Response
from fastapi.responses import JSONResponse

from app.models.share import (
    TripShareResponse,
    TripRevokeResponse,
    SharedTripPublicResponse,
    TripSummaryResponse,
)
from app.services.share_service import ShareService

router = APIRouter()
share_service = ShareService()


def _sanitize_filename(name: str) -> str:
    """Strip illegal characters for HTTP Content-Disposition filename."""
    return re.sub(r"[^a-zA-Z0-9_\-]", "_", name.strip()) or "trip"


# ── Share Generation & Revocation ──────────────────────────────────────────

@router.post(
    "/trips/{trip_id}/share",
    response_model=TripShareResponse,
    status_code=200,
    summary="Generate or retrieve a secure public share link",
)
@router.post(
    "/trips/{trip_id}/share/",
    response_model=TripShareResponse,
    status_code=200,
    include_in_schema=False,
)
def share_trip(
    trip_id: str,
    user_id: str | None = Query(default=None, description="Optional owner user ID"),
    base_url: str | None = Query(default=None, description="Optional frontend origin URL override"),
    origin: str | None = Header(default=None),
) -> TripShareResponse:
    """
    Generate or retrieve a secure, unpredictable share token for the specified trip.
    Allows read-only access to the trip and its itinerary.
    """
    effective_base = base_url or origin or "http://localhost:5173"
    return share_service.create_or_get_share_link(
        trip_id=trip_id,
        user_id=user_id,
        base_url=effective_base,
    )


@router.delete(
    "/trips/{trip_id}/share",
    response_model=TripRevokeResponse,
    summary="Revoke public sharing for a trip",
)
@router.delete(
    "/trips/{trip_id}/share/",
    response_model=TripRevokeResponse,
    include_in_schema=False,
)
def revoke_share(
    trip_id: str,
    user_id: str | None = Query(default=None, description="Optional owner user ID"),
) -> TripRevokeResponse:
    """
    Revoke public sharing for a trip. Existing share links will immediately return HTTP 410 Gone.
    """
    return share_service.revoke_share_link(trip_id=trip_id, user_id=user_id)


# ── Public Read-Only Access ────────────────────────────────────────────────

@router.get(
    "/shared/{share_token}",
    response_model=SharedTripPublicResponse,
    summary="Retrieve read-only shared trip & itinerary",
)
@router.get(
    "/shared/{share_token}/",
    response_model=SharedTripPublicResponse,
    include_in_schema=False,
)
async def get_shared_trip(share_token: str) -> SharedTripPublicResponse:
    """
    Publicly accessible view of a trip and its itinerary using a secure share token.
    Does not require user authentication. Does not expose user_id or sensitive PII.
    """
    return await share_service.get_shared_trip(share_token=share_token)


# ── PDF & JSON Export ──────────────────────────────────────────────────────

@router.get(
    "/trips/{trip_id}/export/pdf",
    summary="Export trip itinerary as a PDF document",
)
@router.get(
    "/trips/{trip_id}/export/pdf/",
    include_in_schema=False,
)
async def export_trip_pdf(
    trip_id: str,
    user_id: str | None = Query(default=None, description="Optional owner user ID"),
) -> Response:
    """
    Generate and stream a professional PDF document containing the trip details,
    day-by-day activities, schedules, transit info, and preparation tips.
    """
    pdf_bytes = await share_service.export_trip_pdf(trip_id=trip_id, user_id=user_id)
    trip = share_service.trip_service.get_trip_by_id(trip_id, user_id=user_id)
    safe_dest = _sanitize_filename(trip.get("destination", "itinerary"))

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="itinerary-{safe_dest}.pdf"',
            "Content-Type": "application/pdf",
        },
    )


@router.get(
    "/trips/{trip_id}/export/json",
    summary="Export trip itinerary as structured JSON",
)
@router.get(
    "/trips/{trip_id}/export/json/",
    include_in_schema=False,
)
async def export_trip_json(
    trip_id: str,
    user_id: str | None = Query(default=None, description="Optional owner user ID"),
) -> JSONResponse:
    """
    Export the complete trip and saved itinerary as structured JSON conforming to the Pydantic schema.
    """
    json_data = await share_service.export_trip_json(trip_id=trip_id, user_id=user_id)
    trip = share_service.trip_service.get_trip_by_id(trip_id, user_id=user_id)
    safe_dest = _sanitize_filename(trip.get("destination", "itinerary"))

    return JSONResponse(
        content=json_data,
        headers={
            "Content-Disposition": f'attachment; filename="itinerary-{safe_dest}.json"',
        },
    )


# ── Plain Text Summary Export ──────────────────────────────────────────────

@router.post(
    "/trips/{trip_id}/summary",
    response_model=TripSummaryResponse,
    summary="Generate a formatted plain text trip summary for clipboard copying",
)
@router.post(
    "/trips/{trip_id}/summary/",
    response_model=TripSummaryResponse,
    include_in_schema=False,
)
async def get_trip_summary(
    trip_id: str,
    user_id: str | None = Query(default=None, description="Optional owner user ID"),
) -> TripSummaryResponse:
    """
    Generate an engaging, structured plain text summary of the trip itinerary
    formatted with emoji highlights, suitable for copying to clipboard or messaging apps.
    """
    return await share_service.get_trip_summary(trip_id=trip_id, user_id=user_id)

