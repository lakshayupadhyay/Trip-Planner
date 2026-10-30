# 📜 Activity 3.2: Prompt Structuring Logic Documentation

## 1. Purpose of `prompt_service.py`

[`backend/app/services/prompt_service.py`](../backend/app/services/prompt_service.py) is a dedicated, modular prompt engineering service. It isolates prompt composition from API routing and external LLM client execution.

### Key Objectives
* **Deterministic Transformation**: Converts validated user travel preferences into structured natural-language prompts.
* **Separation of Concerns**: Kept separate from trip persistence and paid LLM API calls.
* **Cost Efficiency**: Allows prompt inspection, previewing, and debugging without consuming LLM API credits.

---

## 2. Prompt Structuring Workflow

```
┌─────────────────────────────────┐
│   User Travel Preferences       │
│  (Destination, Dates, Budget,   │
│   Style, Interests, Pace, etc.) │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│  Pydantic Validation Layer      │
│  (TravelPreferences Schema)     │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│  Prompt Engineering Service     │
│  (prompt_service.py)            │
│  - calculate_trip_duration()    │
│  - _get_pace_guidelines()       │
│  - _get_style_guidelines()      │
│  - Financial breakdowns         │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│  10-Section Structured Prompt   │
│  Ready for Generative AI (LLM)  │
└─────────────────────────────────┘
```

### The 10 Prompt Sections

1. **AI Role and Instructions**: Directs the LLM to act as an expert travel concierge and planner.
2. **Destination and Travel Dates**: Specific location, calendar dates, and computed duration in days and nights.
3. **Traveler Information**: Headcount, solo vs. group context, and group logistics guidance.
4. **Budget Constraints**: Total budget, per-person allocation, target daily spend estimate, and explicit instructions against inventing unrealistic prices.
5. **Travel Style and Interests**: Style orientation (Adventure, Cultural, Relaxation, Family, Romantic, etc.) and targeted travel interest points.
6. **Daily Activity Pace**: Tailored daily density and downtime instructions (Relaxed: 1–2 highlights; Moderate: 2–3 balanced; Fast: 3–4 high-energy).
7. **Dietary Preferences**: Explicit dietary guardrails for dining spots and regional food recommendations.
8. **Additional Requirements**: User-provided accessibility requests, neighborhood preferences, or special notes.
9. **Expected Output Format**: Standardized day-by-day itinerary schema (Day Header, Morning, Lunch, Afternoon, Evening & Dinner, Transit, Daily Costs, and Practical Tips).
10. **Accuracy and Safety Constraints**: Mandates realistic estimates, disallows fictitious booking confirmations, and advises verification of opening hours and seasonal closures.

---

## 3. The Prompt Preview Endpoint

### `POST /api/v1/itinerary/prompt-preview`

Allows developers, QA testers, and the frontend to preview the generated prompt for any combination of preferences.

#### Request Body (`TravelPreferences`):
```json
{
  "destination": "Germany",
  "start_date": "2027-06-01",
  "end_date": "2027-06-07",
  "num_travelers": 2,
  "budget": 2800.0,
  "travel_style": "cultural",
  "travel_interests": ["history", "castles", "food"],
  "dietary_preferences": ["none"],
  "travel_pace": "moderate",
  "additional_requirements": "Prefer rail travel between cities"
}
```

#### Response Body (`PromptPreviewResponse`):
```json
{
  "destination": "Germany",
  "duration_days": 7,
  "prompt": "# TRAVEL ITINERARY GENERATION REQUEST\n\n## 1. AI Role and Instructions\n..."
}
```

> **Note**: This endpoint does **not** call Google Gemini or any paid AI API. It performs purely local prompt construction and validation.

---

## 4. Connection to Google Gemini API (Upcoming Activity)

In the subsequent activity (AI Itinerary Generation):
1. `gemini_service.py` will import `build_itinerary_prompt()`.
2. The structured prompt will be passed to `google-genai` / `google-generativeai` using `GEMINI_API_KEY`.
3. The model's response will be parsed, validated, and stored in the Supabase `itineraries` table.

