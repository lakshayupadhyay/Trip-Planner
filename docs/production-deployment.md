# Production Deployment Guide
**Project**: Personalized Travel Itinerary Planner  
**Activity**: Epic 5 – Activity 5.3: Testing & Production Deployment

---

## 1. Architecture Overview

```
                      ┌────────────────────────────────────────┐
                      │          Vercel / Netlify             │
                      │     (React + Vite SPA Frontend)       │
                      └──────────────────┬─────────────────────┘
                                         │ HTTPS Requests
                                         ▼
                      ┌────────────────────────────────────────┐
                      │          Render / Railway              │
                      │      (FastAPI + Python Backend)        │
                      └────────────┬──────────────┬────────────┘
                                   │              │
                   PostgreSQL TLS  │              │ HTTPS API Calls
                                   ▼              ▼
                     ┌────────────────┐   ┌───────────────────────────┐
                     │ Supabase Cloud │   │ Google Gemini & Groq APIs │
                     │  (PostgreSQL)  │   │     (AI Providers)        │
                     └────────────────┘   └───────────────────────────┘
```

---

## 2. Environment Variables Checklist

### Backend Environment Variables (`.env`)

| Variable | Description | Example / Default |
|---|---|---|
| `SUPABASE_URL` | Supabase project API URL | `https://xyz.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service-role key (server-side only) | `eyJhbGciOi...` |
| `GEMINI_API_KEY` | Google Gemini API key | `AIzaSy...` |
| `GROQ_API_KEY` | Groq Cloud API key | `gsk_...` |
| `GEMINI_MODEL` | Active Gemini generation model | `gemini-3.8-flash` |
| `GROQ_MODEL` | Active Groq fallback model | `llama-3.3-70b-versatile` |
| `ALLOWED_ORIGINS` | Comma-separated production frontend domains | `https://your-app.vercel.app` |
| `PORT` | Server listening port (set by host) | `8000` |

> [!CAUTION]
> Never commit `.env` or production API keys to Git. Ensure `.gitignore` ignores all `.env` variants.

### Frontend Environment Variables (`.env.production`)

| Variable | Description | Example |
|---|---|---|
| `VITE_API_BASE_URL` | Base URL of deployed backend | `https://travel-planner-api.onrender.com` |

---

## 3. Database Deployment (Supabase)

1. Open your project in the [Supabase Dashboard](https://supabase.com/dashboard).
2. Go to the **SQL Editor**.
3. Verify existing tables: `trips`, `preferences`, `itineraries`, `users`.
4. Run the Activity 5.2 migration from `database/migrations/001_add_shared_trips.sql`:
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

## 4. Backend Deployment

### Option A: Render
1. Push your repository to GitHub.
2. In the Render Dashboard, click **New +** > **Blueprint**.
3. Select your repository. Render will automatically read `render.yaml`.
4. Alternatively, click **New +** > **Web Service**:
   - **Environment**: Python 3.11+
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Under **Environment Variables**, add `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `GEMINI_API_KEY`, `GROQ_API_KEY`, `ALLOWED_ORIGINS`.
6. Click **Deploy**.

### Option B: Railway
1. Click **New Project** > **Deploy from GitHub repo**.
2. Set the root directory to `/backend` or use the root `backend/Dockerfile`.
3. Under **Variables**, add all required backend environment variables.
4. Railway will automatically build and expose the service on port 8000.

---

## 5. Frontend Deployment

### Option A: Vercel
1. In Vercel, click **Add New** > **Project** and select your GitHub repository.
2. Configure project settings:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
3. Under **Environment Variables**, add:
   - `VITE_API_BASE_URL`: The deployed backend URL (e.g. `https://travel-planner-api.onrender.com`).
4. Click **Deploy**. The included `frontend/vercel.json` ensures client-side routing works seamlessly.

### Option B: Netlify
1. In Netlify, click **Add new site** > **Import an existing project**.
2. Select your repository.
3. Configure build settings (or let Netlify read `frontend/netlify.toml`):
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/dist`
4. Add `VITE_API_BASE_URL` in **Environment Variables**.
5. Click **Deploy site**.

---

## 6. Post-Deployment Verification

1. **Backend Health Check**:
   ```bash
   curl -i https://your-backend-api.onrender.com/health
   # Expected: {"status": "healthy", "version": "0.1.0"}
   ```
2. **Database Connectivity**:
   ```bash
   curl -i https://your-backend-api.onrender.com/health/db
   # Expected: {"status": "connected", "message": "Supabase connection is healthy."}
   ```
3. **Response Timing Header**:
   Check response headers for `X-Process-Time-Ms`.
4. **End-to-End Test**:
   - Visit the production frontend URL.
   - Plan and generate a 3-day itinerary.
   - Test PDF download, JSON download, and Copy Summary.
   - Test "Share Trip" and open the generated link in an incognito window.

