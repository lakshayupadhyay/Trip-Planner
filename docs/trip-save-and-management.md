# Epic 5 – Activity 5.1: Trip Save & Management

## Project Overview
* **Application**: Personalized Travel Itinerary Planner
* **Location**: `D:\genai\personalized-travel-planner`
* **Tech Stack**: React.js (Vite) + FastAPI (Python 3.15) + Supabase PostgreSQL + Framer Motion + Lucide React + Pydantic v2

---

## 1. Database Schema & Persistence Strategy

Activity 5.1 transforms the application from a trip-generation prototype into a persistent travel management platform without breaking existing tables or requiring risky database migrations.

### Table Reuse & Relationships

| Table Name | Primary Purpose in Activity 5.1 | Key Columns / Usage |
|---|---|---|
| `trips` | Core trip parent entity | `id (UUID)`, `user_id (UUID)`, `destination`, `start_date`, `end_date`, `total_budget`, `created_at` |
| `preferences` | Traveler preference record | `id`, `user_id`, `budget`, `travel_style`, `interests`, `preferred_destination`, `created_at` |
| `itineraries` | Daily itineraries & full metadata | `id`, `trip_id (UUID FK)`, `day_number (INT)`, `activities (JSONB)`, `created_at` |

### Preserving Vibe & Route Metadata in `itineraries.activities (JSONB)`:
1. **Day 1 Metadata Attachment**: When an itinerary is generated, Day 1's `activities` JSONB record stores `trip_metadata`:
   * `primary_vibe` & `secondary_vibes`
   * `trip_summary` & `total_estimated_cost`
   * `travel_style` & `travel_pace`
   * `optimization_summary` & `route_optimized` flag
   * `packing_and_prep_tips`
2. **Draft Preferences Preservation**: If a user creates or updates a trip before generating a daily itinerary, a draft preferences row is stored in `itineraries` (`day_number: 9999`) ensuring vibes and traveler counts are never lost.
3. **Cascading Deletions**: When a trip is deleted, all associated `itineraries` records are cleanly deleted first, preventing orphan rows.

---

## 2. Backend CRUD API Reference

All routes are mounted under prefix `/api/v1/trips` and `/api/v1/itinerary`.

### 1. `POST /api/v1/trips/`
* **Description**: Create a new trip and persist preferences in Supabase.
* **Request**: `TripCreateRequest`
* **Response**: `TripResponse` (HTTP 201) with `has_itinerary: false`.

### 2. `GET /api/v1/trips/`
* **Description**: List all saved trips (newest first). Supports optional `?user_id=...` filter.
* **Response**: `list[TripResponse]` with computed `has_itinerary` flag and loaded vibe chips.

### 3. `GET /api/v1/trips/{trip_id}`
* **Description**: Retrieve a single trip by UUID.
* **Response**: `TripResponse` (HTTP 200) or HTTP 404 if missing.

### 4. `PUT /api/v1/trips/{trip_id}` and `PATCH /api/v1/trips/{trip_id}`
* **Description**: Update destination, dates, budget, travelers count, vibes, pace, or dietary preferences.
* **Validation**: Enforces `end_date > start_date` and `budget > 0`.
* **Regeneration Flag**: Sets `itinerary_regeneration_recommended: true` if destination or travel dates change.

### 5. `DELETE /api/v1/trips/{trip_id}`
* **Description**: Permanently delete a trip and its associated daily itineraries.
* **Response**: `TripDeleteResponse` (HTTP 200).

### 6. `GET /api/v1/trips/{trip_id}/itinerary` (also `GET /api/v1/itinerary/{trip_id}`)
* **Description**: Directly retrieve the saved daily itinerary from Supabase without triggering AI regeneration.
* **Response**: `ItineraryResponse` with complete route legs, schedules, transit, dining, and daily budgets.

---

## 3. Frontend Trip Management Dashboard

### Component: `frontend/src/components/TripDashboard.jsx`
* **Toolbar & Search**:
  * Real-time search by destination name.
  * Filter tabs: `All Trips`, `With Itineraries`, `Drafts`.
* **Trip Cards**:
  * Destination with map pin and duration in nights.
  * Status tag: `✓ Itinerary Ready` or `⏳ Draft`.
  * Travelers count, total budget, style, and pace indicators.
  * Primary vibe (`✨ Romantic`) and secondary vibes (`+ Food & Culinary`).
  * Action buttons:
    * `View Itinerary`: Opens the saved itinerary view.
    * `Edit`: Opens the Edit Modal.
    * `Delete`: Opens the safe deletion confirmation dialog.
    * `Continue Plan`: Generates a daily plan if draft.
* **Edit Modal**:
  * Pre-populates all existing parameters.
  * Real-time warning alert if dates or destination change.
* **Delete Confirmation Dialog**:
  * Modal preventing accidental deletions.
* **App Navigation (`frontend/src/App.jsx`)**:
  * Top navigation tabs: `Plan a Trip` and `My Trips (N)` with live trip count.
  * Breadcrumb header to return from Itinerary View to My Trips.

---

## 4. Verification & Test Suite

* **Backend Test Suite (`pytest ..\tests -v`)**:
  ```
  107 passed, 1 warning in 1.02s
  ```
  * Includes 8 tests in `tests/test_trip_management.py` covering all CRUD operations, 404/422 handling, date validation, and itinerary retrieval.
* **Frontend Vite Build (`npm run build`)**:
  ```
  ✓ 1936 modules transformed.
  dist/index.html                   0.48 kB
  dist/assets/index-sU-daw_X.css   33.70 kB
  dist/assets/index-B8QW1Fn4.js   353.09 kB
  ✓ built in 2.17s
  ```

