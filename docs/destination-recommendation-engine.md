# 🧭 Activity 3.3: Destination Recommendation Engine

## 1. Overview & Architecture

Activity 3.3 enhances the **Personalized Travel Itinerary Planner** by introducing an intelligent recommendation engine powered by the **Google Gemini API** (`google-genai` SDK).

The engine supports two primary recommendation modes:
1. **Activity & Dining Recommendations**: When a destination is selected, the engine curates a personalized mix of attractions, cultural activities, nature spots, and restaurants strictly respecting user budget, pacing, travel style, and dietary requirements.
2. **Destination Discovery**: When a traveler is undecided or exploring options, the engine suggests top destination candidates tailored to their preferred region, financial budget, and travel interests.

```
┌────────────────────────────────────────────────────────┐
│                   React Frontend                       │
│  - Step 1: Destination Ideas Inspiration Panel         │
│  - Step 4: AI Recommendations Preview                  │
│  - tripsAPI.getDestinationRecommendations()            │
│  - tripsAPI.getActivityRecommendations()               │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP POST
                            ▼
┌────────────────────────────────────────────────────────┐
│                   FastAPI Backend                      │
│  - POST /api/v1/recommendations/destinations           │
│  - POST /api/v1/recommendations/activities             │
│  - Pydantic Validation & Normalization                 │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│        RecommendationService (Gemini Integration)      │
│  - Prompt Synthesis with Constraints & Guardrails      │
│  - Google GenAI Client (gemini-3.8-flash)              │
│  - Markdown-Stripping JSON Parser                      │
│  - Error Handling: 429 Quota, 502 Parsing, 504 Timeout │
└────────────────────────────────────────────────────────┘
```

---

## 2. API Endpoints

### 2.1 POST `/api/v1/recommendations/destinations`

Suggests candidate travel destinations based on user style, region, and budget constraints.

#### Request Body
```json
{
  "preferred_region": "East Asia",
  "num_travelers": 2,
  "budget": 3500.0,
  "travel_style": "cultural",
  "travel_interests": ["history", "food", "temples"],
  "travel_pace": "moderate",
  "additional_requirements": "High-speed rail connectivity"
}
```

#### Response Body (`200 OK`)
```json
{
  "recommendations": [
    {
      "destination": "Kyoto, Japan",
      "country": "Japan",
      "description": "The historical heart of Japan with thousands of classical Buddhist temples, gardens, and imperial palaces.",
      "why_it_matches": "Directly satisfies your cultural travel style, deep interest in historic temples, and scenic walking districts.",
      "estimated_budget_range": "$1,400 - $2,000 USD per person",
      "best_time_to_visit": "October to November or March to May",
      "highlight_attractions": [
        "Fushimi Inari-taisha",
        "Kinkaku-ji (Golden Pavilion)",
        "Gion Historic District",
        "Arashiyama Bamboo Grove"
      ],
      "practical_tips": "Purchase an ICOCA card for seamless transit; visit Fushimi Inari before 8:00 AM to avoid crowds."
    }
  ],
  "notes": "All destinations provide robust high-speed rail access and high safety indices."
}
```

---

### 2.2 POST `/api/v1/recommendations/activities`

Generates tailored attractions, experiences, and dietary-compliant dining spots for a chosen destination.

#### Request Body
```json
{
  "destination": "Barcelona, Spain",
  "num_travelers": 2,
  "budget": 2500.0,
  "travel_style": "cultural",
  "travel_interests": ["architecture", "food", "beaches"],
  "travel_pace": "moderate",
  "dietary_preferences": ["vegetarian"],
  "additional_requirements": "Prefer walkable neighborhoods"
}
```

#### Response Body (`200 OK`)
```json
{
  "destination": "Barcelona, Spain",
  "recommendations": [
    {
      "name": "Sagrada Família",
      "category": "Attractions",
      "description": "Antoni Gaudí's breathtaking modernist basilica with towering stained-glass facades.",
      "reason_for_recommendation": "Matches your architecture interest; an essential cultural landmark.",
      "estimated_cost": "~€26 - €36 EUR / person",
      "suggested_duration": "2 - 2.5 hours",
      "best_time_to_visit": "Morning (9:30 AM) for optimal light through stained glass",
      "location": "Eixample District",
      "practical_tips": "Mandatory to reserve timed-entry tickets online weeks in advance."
    },
    {
      "name": "Teresa Carles",
      "category": "Dining",
      "description": "Pioneering plant-based culinary institution in Barcelona serving inventive vegetarian Catalan fare.",
      "reason_for_recommendation": "Strictly satisfies your vegetarian dietary preference without compromising on authentic local cuisine.",
      "estimated_cost": "~€25 - €35 EUR / person",
      "suggested_duration": "1.5 hours",
      "best_time_to_visit": "Dinner (8:30 PM)",
      "location": "El Raval / Ciutat Vella",
      "practical_tips": "Book evening tables in advance; try the homemade artisan veggie pasta."
    }
  ],
  "notes": "Barcelona is highly walkable, but comfortable shoes and pocket pickpocket vigilance in the Gothic Quarter are recommended."
}
```

---

## 3. Personalization & Accuracy Guardrails

1. **Dietary Integrity**: Dining recommendations strictly honor specified constraints (e.g., vegetarian, vegan, halal, kosher, gluten-free). Prompts explicitly enforce real, reputable restaurants adhering to the dietary requirement.
2. **Budget Realism**: Costs and budget ranges are estimated realistically and calibrated against the traveler's financial allocation.
3. **Pacing Balance**: Pacing directives (`slow`, `moderate`, `fast`) adjust the depth and recommended visit durations.
4. **No Fictitious Bookings**: System instructions explicitly prohibit inventing confirmed reservation numbers, real-time ticket availability, or guaranteed table holds.
5. **Robust Error Handling**:
   - HTTP 422: Validates payload fields (date sequencing, traveler count 1-20, positive budget, non-empty destination).
   - HTTP 429: Translates Google API `RESOURCE_EXHAUSTED` into clear user guidance.
   - HTTP 500: Raised gracefully if `GEMINI_API_KEY` is missing without crashing the server.
   - HTTP 502: Catches invalid JSON outputs from generative responses.
   - HTTP 504: Handles LLM timeouts cleanly.

---

## 4. Testing & Verification

Automated test suite covers both unit services and full integration routes:

```bash
# Run backend pytest suite (41 tests, 100% pass)
cd backend
.venv\Scripts\python -m pytest ..\tests -v
```

Tests included:
- `tests/test_recommendation_service.py`:
  - `test_clean_json_text`: Markdown code block extraction.
  - `test_get_activity_recommendations_success`: Structured parsing with mocked Gemini.
  - `test_get_destination_recommendations_success`: Multi-attribute destination validation.
  - `test_missing_api_key_raises_http_500`: Key validation.
  - `test_malformed_json_raises_http_502`: Bad LLM response recovery.
  - `test_rate_limit_raises_http_429`: Quota handling.
  - `test_timeout_raises_http_504`: Deadline exceeded handling.
- `tests/test_recommendations_api.py`:
  - `test_recommend_destinations_api_success`: End-to-end endpoint check.
  - `test_recommend_activities_api_success`: Full activity response check.
  - `test_recommend_activities_empty_destination_422`: Schema validation.
  - `test_recommend_destinations_invalid_travelers_422`: Boundaries on traveler count.
  - `test_recommend_activities_negative_budget_422`: Budget validation.
  - `test_recommend_service_exception_propagation`: Upstream status pass-through.

