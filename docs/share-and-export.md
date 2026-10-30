# Epic 5 – Activity 5.2: Share & Export Module Documentation

## 1. Overview
The Share & Export Module transforms the Personalized Travel Itinerary Planner into a collaborative, exportable application. Travelers can generate secure, read-only shareable links for friends and collaborators, stream multi-page PDF itineraries generated server-side, download structured JSON files, and copy formatted trip summaries to the clipboard.

---

## 2. Architecture & Design Principles

### A. Zero-PII Public Sharing
- Public share tokens are generated via `secrets.token_urlsafe(32)`.
- The public endpoint `GET /api/v1/shared/{share_token}` returns only trip itinerary content.
- Sensitive user data (`user_id`, email, auth tokens) is strictly excluded from responses and never passed to the frontend.
- Shared trips are read-only; no edit, delete, or regeneration endpoints are exposed on the public view.
- Tokens can be revoked at any time by the owner; revoked tokens immediately return `HTTP 410 Gone`.

### B. Server-Side PDF Generation
- Built with **ReportLab** (`reportlab>=5.0.0`), eliminating client-side layout inconsistencies and rendering issues.
- Includes a title banner, trip metadata box (destination, dates, pace, budget, vibes), executive overview, day-by-day activity tables with start/end times and costs, transit and route leg summaries, daily tips, and packing lists.
- Built-in two-pass footer with page numbering (`Page X • Personalized Travel Planner`).
- Streamed directly via FastAPI with `Content-Type: application/pdf` and `Content-Disposition: attachment; filename="itinerary-{destination}.pdf"`.

### C. Offline / Fallback Resilience
- The backend checks Supabase table `shared_trips`. If the database table is unavailable or before migration execution, it automatically falls back to an in-memory cache (`_IN_MEMORY_SHARES`), ensuring tests and local development function without blocking on cloud DDL.

---

## 3. Endpoints

| Method | Path | Description | Access |
|---|---|---|---|
| `POST` | `/api/v1/trips/{trip_id}/share` | Generate or fetch active share link | Owner / Authenticated |
| `DELETE` | `/api/v1/trips/{trip_id}/share` | Revoke active share link | Owner / Authenticated |
| `GET` | `/api/v1/shared/{share_token}` | Retrieve public itinerary | Public (Read-Only) |
| `GET` | `/api/v1/trips/{trip_id}/export/pdf` | Download PDF document | Owner / Public |
| `GET` | `/api/v1/trips/{trip_id}/export/json` | Download structured JSON | Owner / Public |
| `POST` | `/api/v1/trips/{trip_id}/summary` | Generate clipboard plain text summary | Owner / Public |

---

## 4. Database Schema Migration

The SQL migration is provided at `database/migrations/001_add_shared_trips.sql`:

```sql
CREATE TABLE IF NOT EXISTS shared_trips (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id     UUID        NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    share_token VARCHAR(64) UNIQUE NOT NULL,
    is_active   BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_shared_trips_token ON shared_trips(share_token);
CREATE INDEX IF NOT EXISTS idx_shared_trips_trip_id ON shared_trips(trip_id);
```

---

## 5. Verification Commands

### Backend Tests
```bash
cd backend
$env:PYTHONPATH="D:\genai\personalized-travel-planner\backend"
.\.venv\Scripts\python.exe -m pytest ..\tests -v
```
**Result**: 120 passed in 4.76s.

### Frontend Production Build
```bash
cd frontend
npm run build
```
**Result**: Built in 2.12s with zero errors.

