# Environment & Configuration Management Guide
**Project**: Personalized Travel Itinerary Planner  
**Activity**: Epic 5 – Activity 5.4: Environment & Configuration Management

---

## 1. Overview & Architecture

The application centralizes all backend configuration using **Pydantic Settings v2** (`backend/app/config.py`).
This guarantees:
- Typed validation and schema enforcement at startup.
- Dynamic environment switching across **development**, **staging**, and **production**.
- Strict secret redaction: sensitive credentials are never leaked in logs, exception traces, or string representations (`Settings.safe_dict()`).
- Clear separation between public client configurations (`VITE_...`, `SUPABASE_ANON_KEY`) and backend-only credentials (`SUPABASE_SERVICE_ROLE_KEY`, `SECRET_KEY`, AI provider API keys).

---

## 2. Environment Variables Specification

### A. Server & Environment

| Variable | Type | Default | Description |
|---|---|---|---|
| `ENVIRONMENT` | String | `development` | Runtime mode: `development`, `staging`, `production`, `test`. |
| `DEBUG` | Boolean | `false` | Enables debug traceback. **Must be false in production**. |
| `BACKEND_URL` | URL | `http://localhost:8000` | Backend API base URL. |
| `FRONTEND_URL` | URL | `http://localhost:5173` | Frontend web client URL. |
| `ALLOWED_ORIGINS` | Comma-separated or List | `http://localhost:3000,http://localhost:5173` | Allowed CORS origins. |
| `LOG_LEVEL` | String | `INFO` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. |

### B. Supabase Configuration (Backend Only)

| Variable | Type | Required | Description |
|---|---|---|---|
| `SUPABASE_URL` | URL | **Yes** | Your Supabase project URL (`https://xyz.supabase.co`). |
| `SUPABASE_SERVICE_ROLE_KEY` | String | **Yes** | Administrative service-role key (bypasses RLS). Backend only. |
| `SUPABASE_KEY` / `SUPABASE_ANON_KEY` | String | No | Public anonymous key for scoped client access. |

### C. JWT Authentication & Security

| Variable | Type | Default / Constraint | Description |
|---|---|---|---|
| `SECRET_KEY` | String | Min 32 chars | HMAC-SHA256 secret for signing tokens. |
| `ALGORITHM` | String | `HS256` | JWT signing algorithm. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Integer | `1440` (24h) | Access token validity in minutes. |

### D. AI & LLM Providers

| Variable | Default | Description |
|---|---|---|
| `AI_PROVIDER` | `gemini` | Active AI provider: `gemini`, `groq`, `huggingface`, `ollama`. |
| `GEMINI_API_KEY` | None | API key for Google Gemini (`gemini-3.8-flash`). |
| `GEMINI_MODEL` | `gemini-3.8-flash` | Selected Gemini model. |
| `GROQ_API_KEY` | None | API key for Groq Cloud (`llama-3.3-70b-versatile`). |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Selected Groq model. |
| `HUGGINGFACE_API_KEY` | None | User Access Token for Hugging Face Inference API. |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Base URL of local Ollama server. |

### E. Frontend Environment (`Vite`)

| Variable | Default | Description |
|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Target backend URL for API requests. |
| `VITE_SUPABASE_URL` | `https://your-project.supabase.co` | Public Supabase project URL. |
| `VITE_SUPABASE_ANON_KEY` | `your-anon-key` | Public anonymous key (safe for browser). |

---

## 3. Environment Setup by Stage

### Development Setup
1. Copy template files:
   ```bash
   cp .env.example .env
   cp frontend/.env.example frontend/.env.local
   ```
2. Fill in your development API keys (`GEMINI_API_KEY` or `GROQ_API_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`).
3. Set `DEBUG=true` and `ENVIRONMENT=development`.

### Staging Setup
- Mirror production configuration with isolated staging database and staging API quotas.
- Use distinct Supabase project for staging to avoid test data corrupting production.
- Set `ENVIRONMENT=staging` and `DEBUG=false`.

### Production Setup
- Set `ENVIRONMENT=production` and `DEBUG=false` (enforced by `Settings` model validator).
- Ensure `SECRET_KEY` is a cryptographically strong 32+ character random string.
- Provide all credentials directly via platform environment variables (Render / Railway / Vercel secret managers).
- Restrict `ALLOWED_ORIGINS` to the exact deployed frontend domains.

---

## 4. Provider Setup Guides

### 1. Google Gemini API
1. Visit [Google AI Studio](https://aistudio.google.com/).
2. Create an API Key and copy it.
3. In `.env`, add:
   ```env
   AI_PROVIDER=gemini
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-3.8-flash
   ```

### 2. Groq Cloud API
1. Visit [Groq Console](https://console.groq.com/keys).
2. Create an API Key.
3. In `.env`, add:
   ```env
   AI_PROVIDER=groq
   GROQ_API_KEY=gsk_your_groq_api_key_here
   GROQ_MODEL=llama-3.3-70b-versatile
   ```

### 3. Hugging Face Inference API
1. Visit [Hugging Face Settings -> Access Tokens](https://huggingface.co/settings/tokens).
2. Generate a token with `read` permissions.
3. In `.env`, add:
   ```env
   AI_PROVIDER=huggingface
   HUGGINGFACE_API_KEY=hf_your_token_here
   ```

### 4. Local Ollama Server
1. Download and install [Ollama](https://ollama.ai/).
2. Pull your preferred model:
   ```bash
   ollama pull llama3
   ```
3. Ensure the server is running on `http://localhost:11434`.
4. In `.env`, set:
   ```env
   AI_PROVIDER=ollama
   OLLAMA_BASE_URL=http://localhost:11434
   ```

---

## 5. Security & Key Rotation Procedures

### Generating a New JWT Secret
Run the following Python one-liner to generate a strong 256-bit URL-safe secret:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Secret Rotation Procedure
1. **Supabase Service Role Key**:
   - In Supabase Dashboard -> Project Settings -> API, generate a new Service Role secret.
   - Update `SUPABASE_SERVICE_ROLE_KEY` in the Render / Railway environment settings.
   - Trigger a zero-downtime redeploy.
2. **AI Provider Keys**:
   - Create a secondary key in Google AI Studio or Groq Console.
   - Update `GEMINI_API_KEY` or `GROQ_API_KEY` in your platform environment settings.
   - Redeploy the application.
   - Delete the old key in the provider console once the new deployment is verified.
3. **JWT Secret Rotation**:
   - Update `SECRET_KEY` in production environment settings.
   - Existing active sessions will expire and require user re-authentication, preventing stale token reuse.

