# Activity 4.2: Route & Time Optimization Documentation

## Overview
Activity 4.2 introduces an intelligent Route & Time Optimization engine to the **Personalized Travel Itinerary Planner**. The system arranges activities in geographically sensible sequences, minimizes transit times and backtracking, calculates road network distances using realistic urban circuity factors, and generates conflict-free daily schedules tailored to user travel pace.

---

## 1. Route Optimization Algorithm

### Geographical Sequencing & Time Windows
Within each travel day, activities are organized around natural meal anchors and time windows:
1. **Morning Sightseeing / Attraction**: High-energy exploration beginning at the pace-designated start time.
2. **Lunch Anchor**: Scheduled within the 12:00 PM – 1:30 PM window, honoring dietary preferences.
3. **Afternoon Cultural / Leisure Activity**: Complementary activity clustered in geographic proximity to lunch and dinner.
4. **Dinner Anchor**: Scheduled within the 6:30 PM – 8:30 PM window.
5. **Evening Experience / Stroll**: Relaxing twilight or nightlife experience nearby.

### Distance Minimization & Backtracking Prevention
- Evaluates the road distance matrix between stops $D[S_i, S_{i+1}]$ using coordinates or neighborhood geographic proximity.
- Minimizes the total path length $\sum D[S_i, S_{i+1}]$ across all daily stops while respecting time constraints (opening hours and meal windows).
- Eliminates zig-zag backtracking across cities by grouping geographically adjacent sights within each day.

---

## 2. Distance and Travel Time Calculations

### Haversine Formula with Urban Road Circuity
Real-world city travel is constrained by street grids, traffic lights, and terrain. **Straight-line distance is never presented as actual road distance**.

The system computes great-circle distance via the spherical Haversine formula:
$$a = \sin^2\left(\frac{\Delta\phi}{2}\right) + \cos\phi_1\cos\phi_2\sin^2\left(\frac{\Delta\lambda}{2}\right)$$
$$c = 2\operatorname{atan2}\left(\sqrt{a}, \sqrt{1-a}\right)$$
$$d_{\text{straight}} = R \times c \quad (R = 6,371.0088\text{ km})$$

To model actual road network distance, an **Urban Circuity Factor** ($\approx 1.30$) is applied:
$$d_{\text{road}} \approx d_{\text{straight}} \times 1.30$$

Every calculated distance is explicitly marked with:
- `is_estimated = True`
- `estimation_method = "haversine_circuity_estimate"` or `"district_heuristic"`
- Clear user-facing label (e.g. `"Estimated ~2.4 km road distance"`).

### Multi-Modal Travel Speeds & Buffers
Transit time is estimated across three primary modes:

| Mode | Distance Threshold | Modeled Speed | Fixed Wait/Boarding Buffer |
|---|---|---|---|
| **Walking** | $\le 1.2\text{ km}$ | $4.8\text{ km/h}$ | $2\text{ mins}$ (crossings & lights) |
| **Public Transit** | $1.2\text{ km} - 8.0\text{ km}$ | $22.0\text{ km/h}$ | $6\text{ mins}$ (wait & transfers) |
| **Driving / Taxi** | $> 8.0\text{ km}$ | $28.0\text{ km/h}$ | $4\text{ mins}$ (traffic & boarding) |

### Graceful Fallback for Missing Coordinates
When coordinates or external routing engines are unavailable:
- **Intra-district**: Locations sharing neighborhood tokens are estimated at $\sim 1.1\text{ km}$ ($14\text{ mins}$ walking).
- **Inter-district**: Locations in different areas are estimated at $\sim 4.6\text{ km}$ ($22\text{ mins}$ transit).
- Labeled with `estimation_method = "district_heuristic"` without fabricating exact coordinates.

---

## 3. Time Optimization & Conflict-Free Scheduling

### Travel Pace Customization

| Travel Pace | Day Start Time | Rest Buffer Between Stops | Lunch Duration | Dinner Duration | Target Daily Sights |
|---|---|---|---|---|---|
| **Relaxed** | 09:30 AM | $45\text{ mins}$ | $75\text{ mins}$ | $90\text{ mins}$ | 1–2 key attractions |
| **Moderate** | 09:00 AM | $25\text{ mins}$ | $60\text{ mins}$ | $75\text{ mins}$ | 2–3 balanced attractions |
| **Fast** | 08:30 AM | $15\text{ mins}$ | $45\text{ mins}$ | $60\text{ mins}$ | 3–4 high-energy sights |

### Zero Schedule Overlaps Guarantee
Each stop's schedule is sequentially derived:
$$\text{Start Time}_{k} = \text{End Time}_{k-1} + \text{Transit Time}(k-1 \to k) + \text{Pace Rest Buffer}$$
$$\text{End Time}_{k} = \text{Start Time}_{k} + \text{Activity Duration}_{k}$$

---

## 4. API Endpoints

### 1. `POST /api/v1/itinerary/generate` (Enriched)
Generates an AI-powered day-by-day itinerary and automatically applies Route & Time Optimization before persisting to Supabase.
- Request body: `ItineraryGenerateRequest`
- Response: `ItineraryResponse` with `route_legs`, `schedule`, and `route_optimized = True`.

### 2. `POST /api/v1/itinerary/optimize-route`
Optimizes route sequences, transit legs, and schedules for an existing itinerary response.
- Request body: `RouteOptimizationRequest(itinerary, travel_pace?, preferred_mode?)`
- Response: `ItineraryResponse`

### 3. `POST /api/v1/itinerary/optimize-day`
Optimizes a single day's route and schedules.
- Request body: `DayOptimizationRequest(destination, day, travel_pace, preferred_mode?)`
- Response: `DayItinerary`

---

## 5. Frontend Visual Route Representation

### Features in `ItineraryDisplay.jsx`
1. **Scheduled Times on Activity Cards**: Exact arrival and departure hours (`09:00 AM – 11:00 AM`).
2. **Transit Connector Legs**: Cards placed between consecutive activities showing:
   - Recommended mode icon (`Walking`, `Transit`, `Driving`).
   - Estimated road distance and transit duration.
   - Distinct `"Estimated"` tag.
   - Directions summary.
3. **Interactive Visual Route Map**:
   - Sequential numbered stop nodes (`1: Morning`, `2: Lunch`, `3: Afternoon`, `4: Dinner`, `5: Evening`).
   - Connected path with directional transit badges.
   - Interactive inspection of stop coordinates, district, and scheduled times.
4. **On-the-Fly Pace Re-Optimization**:
   - Quick selector (`Relaxed`, `Moderate`, `Fast`) updates the day schedule and transit buffers dynamically.

---

## 6. External API Requirements
- **Built-in Mode (Default)**: Zero paid external APIs. Uses mathematical Haversine calculations and urban circuity modeling ($1.30\times$).
- **Optional OSRM Provider**: Integrates OpenStreetMap public routing with automatic fallback to Haversine circuity if offline or blocked.
- **Database**: Supabase PostgreSQL uses existing `itineraries.activities` JSONB column with zero schema migrations required.

---

## 7. Manual Testing Instructions

1. Start FastAPI backend:
   ```bash
   cd backend
   .venv\Scripts\uvicorn app.main:app --reload --port 8000
   ```
2. Start Vite frontend:
   ```bash
   cd frontend
   npm run dev
   ```
3. Open `http://localhost:5173` in a browser.
4. Fill in destination (e.g., `Kyoto, Japan`), dates, budget, and select travel pace.
5. Click **Generate Complete Itinerary**.
6. Verify:
   - Scheduled start/end times appear on every activity card.
   - Transit connector cards appear between consecutive stops with distance, time, and "Estimated" tag.
   - Click **Visual Route Map** tab to view the sequential flow of stops and connecting transit badges.
   - Switch between **Relaxed**, **Moderate**, and **Fast** to see the timetable buffers adjust dynamically.

