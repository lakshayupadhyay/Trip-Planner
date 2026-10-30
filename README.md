# ✈️ Personalized Travel Itinerary Planner

> An AI-powered web application that generates personalized travel itineraries based on your preferences, budget, and travel style.

---

## 📋 Project Overview

The Personalized Travel Itinerary Planner helps users plan their dream trips effortlessly. By entering destination, travel dates, budget, and interests, the app generates a detailed day-by-day itinerary powered by AI — including accommodation suggestions, local attractions, dining recommendations, and transportation tips.

---

## 🛠️ Technology Stack

| Layer        | Technology         | Purpose                              |
|--------------|--------------------|--------------------------------------|
| Frontend     | React.js           | Interactive user interface           |
| Backend      | Python + FastAPI   | REST API and business logic          |
| Database     | Supabase           | PostgreSQL database + authentication |
| AI           | Google Gemini API  | Itinerary generation                 |
| Frontend CDN | Vercel             | Frontend hosting and deployment      |
| Backend Host | Render             | Backend API hosting                  |
| Version Ctrl | Git + GitHub       | Source control                       |

---

## 📁 Project Structure

```
personalized-travel-planner/
├── frontend/               # React.js application (to be scaffolded)
├── backend/
│   └── app/
│       ├── main.py         # FastAPI entry point
│       ├── api/            # Route handlers (controllers)
│       ├── services/       # Business logic layer
│       ├── models/         # Pydantic data models
│       └── utils/          # Helper functions and utilities
├── docs/                   # Project documentation
├── tests/                  # Test files
├── .gitignore              # Git ignore rules
├── .env.example            # Environment variable template (no secrets)
└── README.md               # This file
```

---

## ✅ Prerequisites

Make sure the following are installed on your machine before setting up the project:

- **Node.js** v18 or later — [Download](https://nodejs.org/)
- **npm** v9 or later (comes with Node.js)
- **Python** 3.10 or later — [Download](https://www.python.org/downloads/)
- **Git** — [Download](https://git-scm.com/)
- A **GitHub** account — [Sign up](https://github.com/)
- A **Supabase** account — [Sign up](https://supabase.com/) *(for Epic 2)*

---

## 🚀 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/personalized-travel-planner.git
cd personalized-travel-planner
```

### 2. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Open .env and fill in your real credentials (never commit .env!)
```

### 3. Backend Setup

```bash
cd backend

# Create a virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt

# Run the development server
uvicorn app.main:app --reload
```

> API will be available at: `http://localhost:8000`
> Interactive docs at: `http://localhost:8000/docs`
> Database connectivity test: `http://localhost:8000/health/db`

### 3a. Configure Supabase Credentials

1. Go to your [Supabase Dashboard](https://supabase.com/dashboard)
2. Open your project → **Project Settings → API**
3. Copy your **Project URL** and **service-role secret key**
4. Open `.env` (not `.env.example`) and fill in:

```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
```

> ⚠️ Never commit `.env` to Git. It is already git-ignored.

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies (once scaffolded in Epic 2)
npm install

# Start the development server
npm start
```

> Frontend will be available at: `http://localhost:3000`

---

## 🗺️ Planned Features

- [ ] User authentication (sign up / sign in via Supabase Auth)
- [ ] Destination search and selection
- [ ] AI-powered day-by-day itinerary generation
- [ ] Budget estimator and tracker
- [ ] Interactive map view of the itinerary
- [ ] Save, edit, and share itineraries
- [ ] Weather forecast integration
- [ ] Multi-language support

---

## 🤖 AI-Assisted Development

This project is built with the help of **Google Antigravity** — an AI coding agent that assists with project setup, code generation, debugging, and documentation. See [`docs/ai-assisted-development.md`](docs/ai-assisted-development.md) for full details.

---

## 🏗️ Development Epics

| Epic | Title                          | Status      |
|------|-------------------------------|-------------|
| 1    | Vibe Coding Environment Setup  | ✅ Complete |
| 2    | Supabase Database Setup        | ✅ Complete |
| 3    | Backend API & Prompt Engineering | ✅ Complete (Activities 3.1, 3.2, 3.3 Complete) |
| 4    | AI Itinerary Generation        | 🔄 In Progress (Activity 4.1 Complete) |
| 5    | Interactive Trip Management    | 🔜 Planned  |
| 6    | Deployment (Vercel + Render)   | 🔜 Planned  |

### Epic 3 Activities Breakdown
- **Activity 3.1: User Preference Capture** (Frontend form, Pydantic schemas, Supabase trips/preferences integration) — ✅ Complete
- **Activity 3.2: Prompt Structuring Logic** (Modular prompt engineering service, 10-section structured prompt, preview endpoint) — ✅ Complete ([Documentation](docs/prompt-structuring-logic.md))
- **Activity 3.3: Destination Recommendation Engine** (Gemini API integration, structured destination discovery, personalized activity & dining recommendations, responsive frontend cards) — ✅ Complete ([Documentation](docs/destination-recommendation-engine.md))

### Epic 4 Activities Breakdown
- **Activity 4.1: Daily Itinerary Builder** (Pluggable AI provider architecture for Gemini and Groq, structured day-by-day itinerary schema with morning/afternoon/evening activities, dietary-compliant dining, transit, daily budgets, Supabase persistence, and interactive frontend browser) — ✅ Complete ([Documentation](docs/daily-itinerary-builder.md))

---

## 🤝 Contributing

This project is currently in early development. Contribution guidelines will be added in a future epic.

---

## 📄 License

This project is licensed under the MIT License. See `LICENSE` for details.

