# 🗓️ Epic 4, Activity 4.1: Daily Itinerary Builder

## 1. Overview & Architecture

Activity 4.1 implements the **Daily Itinerary Builder** for the **Personalized Travel Itinerary Planner**. It translates traveler preferences, dates, budget constraints, travel styles, and dietary restrictions into comprehensive, day-by-day travel schedules.

### Key Architectural Highlights
- **Pluggable AI Provider Architecture**: Abstract `LLMProvider` interface powering both **Google Gemini** (`google-genai` SDK) and **Groq** (`groq` SDK) with unified asynchronous invocation and runtime provider selection via environment variable `LLM_PROVIDER` (`gemini` or `groq`) or per-request override.
- **Strict Structured JSON Schema**: Pydantic v2 models validating morning, afternoon, and evening activities, restaurant dining recommendations, transit logistics, and itemized daily budgets.
- **Supabase Persistence**: Automatically stores daily itinerary rows in the Supabase PostgreSQL `itineraries` table (`trip_id`, `day_number`, `activities` JSONB).
- **Interactive React Frontend**: Responsive day-by-day itinerary browser with day navigation tabs, categorized activity cards, meal recommendations with dietary compatibility notes, transit advice, and budget summaries.

```
┌────────────────────────────────────────────────────────┐
│                   React Frontend                       │
│  - ItineraryDisplay.jsx (Day tabs, slot cards)        │
│  - CreateTrip.jsx (Preference capture & action bar)   │
│  - tripsAPI.generateItinerary()                       │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP POST /api/v1/itinerary/generate
                            ▼
┌────────────────────────────────────────────────────────┐
│                   FastAPI Backend                      │
│  - POST /api/v1/itinerary/generate                     │
│  - ItineraryGenerateRequest (Pydantic validation)      │
│  - ItineraryService.generate_itinerary()              │
└─────────────┬──────────────────────────┬───────────────┘
              │                          │
              ▼                          ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│   Pluggable AI Engine    │  │     Supabase Database    │
│  - LLMProvider (ABC)     │  │  - Table: `trips`        │
│  - GeminiProvider        │  │  - Table: `itineraries`  │
│  - GroqProvider          │  │    (trip_id, day_number, │
│  - get_llm_provider()    │  │     activities jsonb)    │
└──────────────────────────┘  └──────────────────────────┘
```

---

## 2. AI Model Provider Architecture

Located in `backend/app/services/providers/`:

| Class / Module | Purpose |
|---|---|
| `LLMProvider` (`base.py`) | Abstract base class defining `async generate(prompt, system_prompt)` |
| `GeminiProvider` (`gemini_provider.py`) | Async Gemini implementation using `google-genai` client |
| `GroqProvider` (`groq_provider.py`) | Async Groq implementation using `groq` SDK with JSON response mode |
| `get_llm_provider` (`factory.py`) | Factory function resolving provider from environment (`LLM_PROVIDER`) or explicit override |

### Environment Configuration
```env
# AI / LLM Provider Selection
LLM_PROVIDER=gemini              # 'gemini' or 'groq'
GEMINI_API_KEY=your-gemini-key
GEMINI_MODEL=gemini-3.8-flash
GROQ_API_KEY=your-groq-key
GROQ_MODEL=llama-3.3-70b-versatile
```

---

## 3. Data Models (`app/models/itinerary.py`)

- `Activity`: Individual sight or activity (`time_slot`, `name`, `description`, `location`, `suggested_duration`, `estimated_cost`, `best_time_to_visit`, `booking_required`, `practical_tips`).
- `DiningRecommendation`: Restaurant or food venue (`meal_type`, `name`, `cuisine`, `description`, `estimated_cost`, `dietary_compliance`, `location`, `practical_tips`).
- `Transportation`: Local transit between sights (`mode`, `estimated_time`, `estimated_cost`, `route_details`, `tips`).
- `DailyBudget`: Itemized daily costs (`activities_cost`, `dining_cost`, `transportation_cost`, `total_daily_estimated`, `currency`).
- `DayItinerary`: Chronological single-day plan linking morning, afternoon, evening activities, lunch, dinner, transit, daily budget, and practical tips.
- `ItineraryResponse`: Unified trip schedule with executive summary, duration, budget, days array, and prep/packing tips.
- `ItineraryGenerateRequest`: Extends `TravelPreferences` with optional `trip_id` and optional `provider`.

---

## 4. API Specification

### Endpoint: `POST /api/v1/itinerary/generate`

#### Request Payload
```json
{
  "destination": "Kyoto, Japan",
  "start_date": "2027-04-01",
  "end_date": "2027-04-03",
  "num_travelers": 2,
  "budget": 2000.0,
  "travel_style": "cultural",
  "travel_interests": ["history", "food", "temples"],
  "dietary_preferences": ["vegetarian"],
  "travel_pace": "moderate",
  "additional_requirements": "High-speed rail connectivity",
  "trip_id": "3060d1c4-0a78-4ef9-9590-5a05bd808915",
  "provider": "gemini"
}
```

#### Response (`200 OK`)
```json
{
  "trip_id": "3060d1c4-0a78-4ef9-9590-5a05bd808915",
  "destination": "Kyoto, Japan",
  "start_date": "2027-04-01",
  "end_date": "2027-04-03",
  "duration_days": 3,
  "total_budget": 2000.0,
  "travel_style": "cultural",
  "travel_pace": "moderate",
  "trip_summary": "A 3-day cultural immersion across Kyoto's sacred shrines, historic tea districts, and serene bamboo groves.",
  "total_estimated_cost": "~$650 USD total across both travelers",
  "provider_used": "gemini",
  "packing_and_prep_tips": [
    "Purchase an ICOCA IC card for local trains and buses",
    "Wear comfortable slip-on shoes for frequent temple entry"
  ],
  "days": [
    {
      "day_number": 1,
      "date": "2027-04-01",
      "theme": "Eastern Kyoto & Ancient Zen Sanctuaries",
      "morning_activity": {
        "time_slot": "morning",
        "name": "Kiyomizu-dera Temple",
        "description": "Historic wooden stage temple offering sweeping vistas over Kyoto.",
        "location": "Higashiyama",
        "suggested_duration": "2 hours",
        "estimated_cost": "¥400 (~$3 USD)",
        "best_time_to_visit": "8:30 AM",
        "booking_required": false,
        "practical_tips": "Arrive early before tour groups."
      },
      "lunch": {
        "meal_type": "Lunch",
        "name": "Yodoya Soba",
        "cuisine": "Traditional Soba & Tofu",
        "description": "Artisan handmade soba in historic Higashiyama.",
        "estimated_cost": "~$15 USD / person",
        "dietary_compliance": "Vegetarian soba broth available upon request",
        "location": "Higashiyama"
      },
      "afternoon_activity": {
        "time_slot": "afternoon",
        "name": "Yasaka Shrine & Maruyama Park",
        "description": "Stroll through the lantern-adorned shrine and adjacent gardens.",
        "location": "Gion",
        "suggested_duration": "1.5 hours",
        "estimated_cost": "Free",
        "best_time_to_visit": "2:30 PM",
        "booking_required": false
      },
      "dinner": {
        "meal_type": "Dinner",
        "name": "Shigetsu",
        "cuisine": "Shojin Ryori",
        "description": "Michelin Bib Gourmand Zen vegetarian temple dining.",
        "estimated_cost": "~$40 USD / person",
        "dietary_compliance": "100% vegetarian and vegan Buddhist cuisine",
        "location": "Arashiyama"
      },
      "evening_activity": {
        "time_slot": "evening",
        "name": "Gion Shirakawa Lantern Walk",
        "description": "Atmospheric evening stroll alongside preserved wooden machiya and willow trees.",
        "location": "Gion",
        "suggested_duration": "1 hour",
        "estimated_cost": "Free",
        "best_time_to_visit": "7:30 PM",
        "booking_required": false
      },
      "transportation": {
        "mode": "Kyoto City Bus & Walking",
        "estimated_time": "15-20 mins between sights",
        "estimated_cost": "¥230 (~$1.60 USD)",
        "route_details": "Bus 206 from Kyoto Station to Gojo-zaka",
        "tips": "Tap IC card when exiting the bus"
      },
      "daily_budget": {
        "activities_cost": "~$3 USD",
        "dining_cost": "~$55 USD",
        "transportation_cost": "~$4 USD",
        "total_daily_estimated": "~$62 USD / person",
        "currency": "USD"
      },
      "practical_tips": "Carry cash for smaller temple stalls and souvenir shops."
    }
  ]
}
```

---

## 5. Supabase Database Integration

The generated daily plans are persisted to the Supabase `itineraries` table:

```sql
-- Schema Reference:
-- Table: itineraries
--   id: uuid (PK, default: gen_random_uuid())
--   trip_id: uuid (FK to trips.id)
--   day_number: int4
--   activities: jsonb
--   created_at: timestamptz (default: now())
```

When an itinerary is generated:
1. `trip_id` is linked or created in the `trips` table.
2. Prior rows for that `trip_id` are cleaned to allow seamless regeneration.
3. Each day's complete schedule is stored as a JSONB payload linked to its `day_number`.

---

## 6. Testing & Quality Assurance

- **69 automated tests** passing in `0.44s`.
- Unit tests for `GeminiProvider`, `GroqProvider`, and `get_llm_provider` factory.
- Validation tests for all Pydantic models.
- Service tests validating JSON markdown cleanup, malformed response handling (502), rate limit translation (429), and database saving.
- Integration tests for `POST /api/v1/itinerary/generate` and `POST /api/v1/itinerary/prompt-preview`.
- Frontend production build (`npm run build`) compiles with 0 errors.

