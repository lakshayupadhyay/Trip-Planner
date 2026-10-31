"""
backend/app/services/share_service.py

Service layer for Trip Sharing, Exporting (PDF, JSON), and Text Summaries.
Features:
  - Cryptographically secure share tokens (secrets.token_urlsafe)
  - Public read-only itinerary view with zero user PII exposure
  - Server-side PDF generation via ReportLab
  - Structured JSON export matching Pydantic response models
  - Plain-text summary for clipboard copying
  - Supabase persistence with seamless fallback cache for local dev / resilience
"""

from __future__ import annotations

import inspect
import io
import logging
import secrets
from datetime import datetime, timezone
from typing import Any
from fastapi import HTTPException

logger = logging.getLogger(__name__)

from app.models.share import (
    TripShareResponse,
    TripRevokeResponse,
    SharedTripPublicResponse,
    TripSummaryResponse,
)
from app.services.trip_service import TripService
from app.services.itinerary_service import ItineraryService

# Fallback store for local dev or when Supabase shared_trips table is not yet migrated
_IN_MEMORY_SHARES: dict[str, dict[str, Any]] = {}
_TRIP_TO_SHARE_TOKEN: dict[str, str] = {}


class ShareService:
    """
    Handles trip sharing, public itinerary retrieval, and multi-format exports.
    """

    def __init__(
        self,
        trip_service: TripService | None = None,
        itinerary_service: ItineraryService | None = None,
        db: Any | None = None,
    ) -> None:
        self.trip_service = trip_service or TripService(db=db)
        self.itinerary_service = itinerary_service or ItineraryService(db=db)
        self._db = db

    @property
    def db(self) -> Any:
        """Lazily load the shared Supabase client."""
        if self._db is not None:
            return self._db
        try:
            from app.utils.supabase_client import supabase
            return supabase
        except Exception:
            return None

    async def _get_itinerary_safe(self, trip_id: str) -> Any:
        """
        Safely fetch saved itinerary for a trip.
        Supports both synchronous ItineraryService (production) and AsyncMock (unit tests).
        Logs clear warnings without exposing sensitive information.
        """
        try:
            res = self.itinerary_service.get_itinerary_by_trip_id(trip_id)
            if inspect.isawaitable(res):
                return await res
            return res
        except HTTPException as http_exc:
            logger.info("Saved itinerary lookup for trip %s returned HTTP %s: %s", trip_id, http_exc.status_code, http_exc.detail)
            return None
        except Exception as exc:
            logger.warning("Unexpected error retrieving itinerary for trip %s: %s", trip_id, exc)
            return None

    # ── Share Management ────────────────────────────────────────────────────────

    def create_or_get_share_link(
        self,
        trip_id: str,
        user_id: str | None = None,
        base_url: str = "http://localhost:5173",
    ) -> TripShareResponse:
        """
        Generate or retrieve a secure shareable link for a trip.
        Verifies trip existence and saves token to database/cache.
        """
        # 1. Validate trip exists
        trip = self.trip_service.get_trip_by_id(trip_id, user_id=user_id)
        clean_trip_id = str(trip["id"])

        # 2. Check if active share already exists in database
        existing_token: str | None = None
        created_at: str | None = None

        if self.db is not None:
            try:
                res = (
                    self.db.table("shared_trips")
                    .select("share_token, is_active, created_at")
                    .eq("trip_id", clean_trip_id)
                    .eq("is_active", True)
                    .limit(1)
                    .execute()
                )
                if res.data:
                    existing_token = res.data[0]["share_token"]
                    created_at = res.data[0].get("created_at")
            except Exception:
                # Table may not exist yet or query failed; proceed to fallback
                pass

        # Check in-memory fallback if DB had no match
        if not existing_token and clean_trip_id in _TRIP_TO_SHARE_TOKEN:
            token_candidate = _TRIP_TO_SHARE_TOKEN[clean_trip_id]
            if _IN_MEMORY_SHARES.get(token_candidate, {}).get("is_active"):
                existing_token = token_candidate
                created_at = _IN_MEMORY_SHARES[token_candidate].get("created_at")

        # 3. If no active token, generate a cryptographically secure token
        if not existing_token:
            share_token = secrets.token_urlsafe(32)
            now_iso = datetime.now(timezone.utc).isoformat()
            created_at = now_iso

            # Save in DB
            if self.db is not None:
                try:
                    # Deactivate any previous shares for this trip
                    self.db.table("shared_trips").update({"is_active": False}).eq("trip_id", clean_trip_id).execute()
                    self.db.table("shared_trips").insert({
                        "trip_id": clean_trip_id,
                        "share_token": share_token,
                        "is_active": True,
                        "created_at": now_iso,
                    }).execute()
                except Exception:
                    pass

            # Update in-memory fallback
            _IN_MEMORY_SHARES[share_token] = {
                "trip_id": clean_trip_id,
                "share_token": share_token,
                "is_active": True,
                "created_at": now_iso,
            }
            _TRIP_TO_SHARE_TOKEN[clean_trip_id] = share_token
        else:
            share_token = existing_token

        share_url = f"{base_url.rstrip('/')}/?share={share_token}"

        return TripShareResponse(
            trip_id=clean_trip_id,
            share_token=share_token,
            share_url=share_url,
            is_active=True,
            created_at=created_at,
        )

    def revoke_share_link(
        self, trip_id: str, user_id: str | None = None
    ) -> TripRevokeResponse:
        """
        Disable/revoke sharing for a trip. Existing share URLs will return HTTP 410 Gone.
        """
        # Validate trip existence
        trip = self.trip_service.get_trip_by_id(trip_id, user_id=user_id)
        clean_trip_id = str(trip["id"])

        # Deactivate in database
        if self.db is not None:
            try:
                self.db.table("shared_trips").update({"is_active": False}).eq("trip_id", clean_trip_id).execute()
            except Exception:
                pass

        # Deactivate in in-memory fallback
        if clean_trip_id in _TRIP_TO_SHARE_TOKEN:
            token = _TRIP_TO_SHARE_TOKEN[clean_trip_id]
            if token in _IN_MEMORY_SHARES:
                _IN_MEMORY_SHARES[token]["is_active"] = False

        return TripRevokeResponse(
            trip_id=clean_trip_id,
            success=True,
            message="Trip sharing link has been revoked. The previous link is no longer accessible.",
        )

    async def get_shared_trip(self, share_token: str) -> SharedTripPublicResponse:
        """
        Retrieve read-only trip and itinerary data for public viewers.
        Returns HTTP 404 if token does not exist.
        Returns HTTP 410 if token was revoked.
        Never returns sensitive user information (user_id, email).
        """
        clean_token = share_token.strip()
        record: dict[str, Any] | None = None

        # 1. Look up in DB
        if self.db is not None:
            try:
                res = (
                    self.db.table("shared_trips")
                    .select("*")
                    .eq("share_token", clean_token)
                    .limit(1)
                    .execute()
                )
                if res.data:
                    record = res.data[0]
            except Exception:
                pass

        # 2. Look up in fallback cache if DB had no match
        if not record and clean_token in _IN_MEMORY_SHARES:
            record = _IN_MEMORY_SHARES[clean_token]

        if not record:
            raise HTTPException(
                status_code=404,
                detail="Shared trip not found or link is invalid.",
            )

        if not record.get("is_active", False):
            raise HTTPException(
                status_code=410,
                detail="This trip share link has been revoked by the owner.",
            )

        trip_id = str(record["trip_id"])

        # 3. Fetch trip details
        try:
            trip = self.trip_service.get_trip_by_id(trip_id)
        except HTTPException:
            raise HTTPException(
                status_code=404,
                detail="The trip associated with this share link no longer exists.",
            )

        # 4. Fetch saved itinerary
        itinerary = await self._get_itinerary_safe(trip_id)

        # Calculate duration days
        start_date_str = str(trip["start_date"])
        end_date_str = str(trip["end_date"])
        try:
            d1 = datetime.strptime(start_date_str, "%Y-%m-%d")
            d2 = datetime.strptime(end_date_str, "%Y-%m-%d")
            duration_days = max(1, (d2 - d1).days + 1)
        except Exception:
            duration_days = len(itinerary.days) if itinerary and itinerary.days else 1

        # Build public response without any user_id or email
        return SharedTripPublicResponse(
            share_token=clean_token,
            trip_id=trip_id,
            destination=trip["destination"],
            start_date=start_date_str,
            end_date=end_date_str,
            duration_days=duration_days,
            total_budget=float(trip.get("budget", 0.0)),
            travel_style=trip.get("travel_style", "cultural"),
            travel_pace=trip.get("travel_pace", "moderate"),
            primary_vibe=trip.get("primary_vibe"),
            secondary_vibes=trip.get("secondary_vibes") or [],
            trip_summary=itinerary.trip_summary if itinerary else f"Trip to {trip['destination']}",
            total_estimated_cost=itinerary.total_estimated_cost if itinerary else f"${trip.get('budget', 0):,.0f} USD",
            packing_and_prep_tips=itinerary.packing_and_prep_tips if itinerary else [],
            days=itinerary.days if itinerary else [],
            route_optimized=itinerary.route_optimized if itinerary else False,
            optimization_summary=itinerary.optimization_summary if itinerary else None,
            is_shared=True,
            created_at=record.get("created_at"),
        )

    # ── Text Summary Export ─────────────────────────────────────────────────────

    async def get_trip_summary(
        self, trip_id: str, user_id: str | None = None
    ) -> TripSummaryResponse:
        """
        Generate structured highlights and clipboard-copyable text summary.
        """
        trip = self.trip_service.get_trip_by_id(trip_id, user_id=user_id)
        itinerary = await self._get_itinerary_safe(trip_id)
        if itinerary:
            trip["has_itinerary"] = True
            trip["status"] = "confirmed"
        else:
            trip["has_itinerary"] = False
            trip["status"] = "pending"

        dest = trip["destination"]
        s_date = str(trip["start_date"])
        e_date = str(trip["end_date"])
        budget = float(trip.get("budget", 0))
        primary_vibe = trip.get("primary_vibe") or "Standard"
        sec_vibes = trip.get("secondary_vibes") or []
        pace = trip.get("travel_pace", "moderate").capitalize()

        lines: list[str] = []
        lines.append(f"🌍 TRIP ITINERARY: {dest.upper()}")
        lines.append(f"📅 Dates: {s_date} to {e_date}")
        lines.append(f"✨ Travel Vibe: {primary_vibe}" + (f" ({', '.join(sec_vibes)})" if sec_vibes else ""))
        lines.append(f"⏱️ Pace: {pace} | 💰 Budget: ${budget:,.0f} USD")
        lines.append("────────────────────────────────────────────")

        daily_highlights: list[dict[str, Any]] = []

        if itinerary and itinerary.days:
            for day in itinerary.days:
                lines.append(f"\n📍 Day {day.day_number}: {day.theme}")
                m_act = day.morning_activity.name if day.morning_activity else "Sightseeing"
                a_act = day.afternoon_activity.name if day.afternoon_activity else "Exploration"
                lines.append(f"  • Morning: {m_act}")
                if day.lunch:
                    lines.append(f"  • Lunch: {day.lunch.name} ({day.lunch.cuisine})")
                lines.append(f"  • Afternoon: {a_act}")
                if day.dinner:
                    lines.append(f"  • Dinner: {day.dinner.name} ({day.dinner.cuisine})")
                if day.evening_activity:
                    lines.append(f"  • Evening: {day.evening_activity.name}")

                daily_highlights.append({
                    "day_number": day.day_number,
                    "theme": day.theme,
                    "morning": m_act,
                    "lunch": day.lunch.name if day.lunch else None,
                    "afternoon": a_act,
                    "dinner": day.dinner.name if day.dinner else None,
                    "evening": day.evening_activity.name if day.evening_activity else None,
                })

            if itinerary.trip_summary:
                lines.append("\n📝 Summary:")
                lines.append(f"  {itinerary.trip_summary}")
        else:
            lines.append("\n(Itinerary details are pending generation.)")

        lines.append("\n────────────────────────────────────────────")
        lines.append("Generated with Personalized Travel Planner")

        summary_text = "\n".join(lines)

        return TripSummaryResponse(
            trip_id=str(trip["id"]),
            destination=dest,
            start_date=s_date,
            end_date=e_date,
            duration_days=len(itinerary.days) if itinerary and itinerary.days else 1,
            total_budget=budget,
            primary_vibe=trip.get("primary_vibe"),
            secondary_vibes=sec_vibes,
            summary_text=summary_text,
            daily_highlights=daily_highlights,
        )

    # ── JSON Export ─────────────────────────────────────────────────────────────

    async def export_trip_json(
        self, trip_id: str, user_id: str | None = None
    ) -> dict[str, Any]:
        """
        Assemble complete trip and itinerary data into structured JSON matching Pydantic response models.
        """
        trip = self.trip_service.get_trip_by_id(trip_id, user_id=user_id)
        itinerary = await self._get_itinerary_safe(trip_id)
        if itinerary:
            itinerary_data = itinerary.model_dump()
            trip["has_itinerary"] = True
            trip["status"] = "confirmed"
        else:
            itinerary_data = None
            trip["has_itinerary"] = False
            trip["status"] = "pending"

        return {
            "export_metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "format": "application/json",
                "schema_version": "1.0",
            },
            "trip": trip,
            "itinerary": itinerary_data,
        }

    # ── PDF Export ──────────────────────────────────────────────────────────────

    async def export_trip_pdf(
        self, trip_id: str, user_id: str | None = None
    ) -> bytes:
        """
        Generate a professional, multi-page PDF itinerary using ReportLab.
        Includes cover header, trip overview, daily schedule, transit routes, and packing tips.
        """
        trip = self.trip_service.get_trip_by_id(trip_id, user_id=user_id)
        itinerary = await self._get_itinerary_safe(trip_id)
        if itinerary:
            trip["has_itinerary"] = True
            trip["status"] = "confirmed"
        else:
            trip["has_itinerary"] = False
            trip["status"] = "pending"

        return self._build_pdf_bytes(trip=trip, itinerary=itinerary)

    def _build_pdf_bytes(self, trip: dict[str, Any], itinerary: Any | None) -> bytes:
        """Internal helper to construct ReportLab PDF elements."""
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle,
            HRFlowable,
            KeepTogether,
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        buffer = io.BytesIO()

        # Page setup
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40,
        )

        styles = getSampleStyleSheet()

        # Custom palette
        primary_color = colors.HexColor("#1e293b")      # Slate 800
        accent_color = colors.HexColor("#0284c7")       # Sky 600
        secondary_color = colors.HexColor("#0f766e")    # Teal 700
        light_bg = colors.HexColor("#f8fafc")           # Slate 50
        card_border = colors.HexColor("#e2e8f0")        # Slate 200
        text_muted = colors.HexColor("#64748b")         # Slate 500

        # Typography styles
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=28,
            textColor=primary_color,
            spaceAfter=6,
        )

        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=12,
            leading=16,
            textColor=accent_color,
            spaceAfter=14,
        )

        heading_day_style = ParagraphStyle(
            "DayHeading",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=colors.white,
        )

        activity_title_style = ParagraphStyle(
            "ActivityTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=primary_color,
        )

        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#334155"),
        )

        tip_style = ParagraphStyle(
            "Tip",
            parent=styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=8.5,
            leading=11,
            textColor=secondary_color,
        )

        meta_label_style = ParagraphStyle(
            "MetaLabel",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            textColor=text_muted,
        )

        meta_value_style = ParagraphStyle(
            "MetaValue",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=primary_color,
        )

        elements: list[Any] = []

        # ── 1. Header & Title Banner ──────────────────────────────────────────
        dest_name = trip.get("destination", "Your Destination")
        elements.append(Paragraph(f"✈️ Travel Itinerary: {dest_name}", title_style))
        s_date = str(trip.get("start_date", ""))
        e_date = str(trip.get("end_date", ""))
        elements.append(Paragraph(f"{s_date} — {e_date} &bull; Personalized Travel Planner", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=accent_color, spaceAfter=14))

        # ── 2. Trip Metadata Summary Box ──────────────────────────────────────
        primary_vibe = trip.get("primary_vibe") or "Standard"
        sec_vibes = ", ".join(trip.get("secondary_vibes") or []) or "None"
        budget_val = f"${float(trip.get('budget', 0)):,.0f} USD"
        pace_val = str(trip.get("travel_pace", "moderate")).capitalize()
        travelers_val = str(trip.get("num_travelers", 1))

        meta_table_data = [
            [
                Paragraph("<b>Destination:</b>", meta_label_style),
                Paragraph(dest_name, meta_value_style),
                Paragraph("<b>Total Budget:</b>", meta_label_style),
                Paragraph(budget_val, meta_value_style),
            ],
            [
                Paragraph("<b>Travel Pace:</b>", meta_label_style),
                Paragraph(pace_val, meta_value_style),
                Paragraph("<b>Travelers:</b>", meta_label_style),
                Paragraph(f"{travelers_val} Person(s)", meta_value_style),
            ],
            [
                Paragraph("<b>Primary Vibe:</b>", meta_label_style),
                Paragraph(primary_vibe, meta_value_style),
                Paragraph("<b>Secondary Vibes:</b>", meta_label_style),
                Paragraph(sec_vibes, meta_value_style),
            ],
        ]

        meta_table = Table(meta_table_data, colWidths=[90, 175, 100, 165])
        meta_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), light_bg),
            ("BOX", (0, 0), (-1, -1), 0.5, card_border),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, card_border),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 14))

        # ── 3. Executive Summary (if available) ────────────────────────────────
        if itinerary and getattr(itinerary, "trip_summary", None):
            summary_p = Paragraph(f"<b>Overview:</b> {itinerary.trip_summary}", body_style)
            elements.append(summary_p)
            elements.append(Spacer(1, 14))

        # ── 4. Day-by-Day Detailed Plan ────────────────────────────────────────
        if itinerary and getattr(itinerary, "days", None):
            for day in itinerary.days:
                day_elements: list[Any] = []

                # Day Header Banner
                day_header_text = f"Day {day.day_number}: {day.theme}"
                day_banner = Table(
                    [[Paragraph(day_header_text, heading_day_style)]],
                    colWidths=[530],
                )
                day_banner.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), primary_color),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ]))
                day_elements.append(day_banner)
                day_elements.append(Spacer(1, 8))

                # Activities rows
                act_rows = []

                # Morning
                if day.morning_activity:
                    sched = f" ({day.morning_activity.schedule.start_time})" if day.morning_activity.schedule else ""
                    act_rows.append([
                        Paragraph(f"<b>🌅 Morning{sched}</b>", meta_label_style),
                        Paragraph(f"<b>{day.morning_activity.name}</b><br/>{day.morning_activity.description}", body_style),
                        Paragraph(day.morning_activity.estimated_cost or "Free", meta_value_style),
                    ])

                # Lunch
                if day.lunch:
                    act_rows.append([
                        Paragraph("<b>🍴 Lunch</b>", meta_label_style),
                        Paragraph(f"<b>{day.lunch.name}</b> ({day.lunch.cuisine})<br/>{day.lunch.description}", body_style),
                        Paragraph(day.lunch.estimated_cost or "", meta_value_style),
                    ])

                # Afternoon
                if day.afternoon_activity:
                    sched = f" ({day.afternoon_activity.schedule.start_time})" if day.afternoon_activity.schedule else ""
                    act_rows.append([
                        Paragraph(f"<b>☀️ Afternoon{sched}</b>", meta_label_style),
                        Paragraph(f"<b>{day.afternoon_activity.name}</b><br/>{day.afternoon_activity.description}", body_style),
                        Paragraph(day.afternoon_activity.estimated_cost or "Free", meta_value_style),
                    ])

                # Dinner
                if day.dinner:
                    act_rows.append([
                        Paragraph("<b>🍷 Dinner</b>", meta_label_style),
                        Paragraph(f"<b>{day.dinner.name}</b> ({day.dinner.cuisine})<br/>{day.dinner.description}", body_style),
                        Paragraph(day.dinner.estimated_cost or "", meta_value_style),
                    ])

                # Evening
                if day.evening_activity:
                    sched = f" ({day.evening_activity.schedule.start_time})" if day.evening_activity.schedule else ""
                    act_rows.append([
                        Paragraph(f"<b>🌙 Evening{sched}</b>", meta_label_style),
                        Paragraph(f"<b>{day.evening_activity.name}</b><br/>{day.evening_activity.description}", body_style),
                        Paragraph(day.evening_activity.estimated_cost or "Free", meta_value_style),
                    ])

                if act_rows:
                    act_table = Table(act_rows, colWidths=[90, 340, 100])
                    act_table.setStyle(TableStyle([
                        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                        ("BOX", (0, 0), (-1, -1), 0.5, card_border),
                        ("INNERGRID", (0, 0), (-1, -1), 0.5, card_border),
                        ("TOPPADDING", (0, 0), (-1, -1), 5),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                        ("LEFTPADDING", (0, 0), (-1, -1), 8),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ]))
                    day_elements.append(act_table)
                    day_elements.append(Spacer(1, 6))

                # Route & Logistics
                if day.transportation:
                    transit_info = f"<b>Transit:</b> {day.transportation.mode} (~{day.transportation.estimated_time}, {day.transportation.estimated_cost})"
                    day_elements.append(Paragraph(transit_info, tip_style))

                if getattr(day, "total_travel_distance_km", None):
                    route_note = f"<b>Optimized Route:</b> Estimated ~{day.total_travel_distance_km:.1f} km road distance (~{day.total_travel_time_minutes} mins travel time)"
                    day_elements.append(Paragraph(route_note, tip_style))

                if day.practical_tips:
                    day_elements.append(Paragraph(f"<b>💡 Daily Tip:</b> {day.practical_tips}", tip_style))

                day_elements.append(Spacer(1, 14))
                elements.append(KeepTogether(day_elements))
        else:
            elements.append(Paragraph("<i>No day-by-day itinerary generated yet. Visit the planner to generate your custom trip!</i>", body_style))
            elements.append(Spacer(1, 14))

        # ── 5. Packing & Prep Tips ────────────────────────────────────────────
        if itinerary and getattr(itinerary, "packing_and_prep_tips", None):
            prep_elements: list[Any] = []
            prep_elements.append(Paragraph("<b>🎒 Packing & Travel Prep Tips</b>", activity_title_style))
            prep_elements.append(Spacer(1, 4))
            for tip in itinerary.packing_and_prep_tips:
                prep_elements.append(Paragraph(f"&bull; {tip}", body_style))
            prep_elements.append(Spacer(1, 14))
            elements.append(KeepTogether(prep_elements))

        # Build document with page numbering footer
        def _footer(canvas_obj: Any, doc_obj: Any) -> None:
            canvas_obj.saveState()
            canvas_obj.setFont("Helvetica", 8)
            canvas_obj.setFillColor(text_muted)
            page_text = f"Page {doc_obj.page} &bull; Personalized Travel Planner &bull; Created for {dest_name}"
            canvas_obj.drawRightString(doc_obj.pagesize[0] - 40, 25, page_text)
            canvas_obj.drawString(40, 25, "Confidential & Personal Travel Itinerary")
            canvas_obj.restoreState()

        doc.build(elements, onFirstPage=_footer, onLaterPages=_footer)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
