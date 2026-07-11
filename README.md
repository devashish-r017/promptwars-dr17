# StormShield ⛈️

> **Intelligent monsoon preparedness for families.**

StormShield is a GenAI-powered web application designed to help individuals, families, and communities prepare for, navigate, and recover from the monsoon season. By leveraging Google Gemini (via LangChain) and integrating real-time/simulated weather conditions, StormShield delivers highly personalized, multilingual (English & Hindi) safety guidance and active alerts.

---

## 🌟 Key Features

*   **Personalized Preparedness Plans** — Customized safety checklists and action plans tailored to user location, family size, dwelling type (e.g., ground-floor vs. high-rise), vulnerable members (kids/elderly/pets), health conditions, and vehicle ownership.
*   **Weather-Aware Guidance** — The application adapts all AI-generated content (preparedness plans, travel recommendations, risk scores) dynamically based on actual or simulated weather conditions.
*   **Emergency Checklists** — Smart, interactive checklists highlighting essential supplies (medical, food, waterproof documents) custom-curated for the family configuration.
*   **Travel Advisories** — Real-time travel safety ratings (Safe, Caution, Avoid) and route recommendations based on active weather events, tailored to the user's vehicle ownership status.
*   **Safety Recommendations** — Phase-specific monsoon safety tips addressing electrical hazards, waterlogging, structural integrity, and monsoon-related health risks (dengue, waterborne diseases).
*   **Multilingual Assistance** — Full bilingual support in both English and Hindi (हिन्दी), covering both the static UI chrome and all dynamically generated AI responses.
*   **Situational Real-Time Alerts** — A continuous alert feed polling for active weather events, flashing immediate toast notifications when new warnings or evacuation notices are issued.
*   **Full Timeline Coverage** — Complete safety coverage addressing the three crucial phases of severe weather: **Before** (preparation), **During** (active safety), and **After** (recovery).
*   **Interactive AI Assistant** — A global, context-aware chatbot capable of answering questions in the selected language using the active page context, weather severity, and user profile.

---

## 🛠️ Technology Stack

| Layer | Technology | Description |
|---|---|---|
| **Frontend** | Vite + React + TypeScript + Tailwind CSS v4 | Clean component architecture, `@tailwindcss/vite` configuration, and responsive layouts. |
| **Backend** | Python + FastAPI | High-performance async backend managed with `uv`. |
| **Database** | SQLite via SQLAlchemy | Light database footprint storing user profiles, alert histories, and cached responses. |
| **AI Layer** | Google Gemini 2.5 (Flash/Pro) | Handled via LangChain with Pydantic output parsers for structured JSON generation. |

---

## 📂 Project Structure

```text
/
├── AGENTS.md            # Guidelines, commands, and project boundaries
├── PROJECT.md           # Problem statement, MVP scope, and success criteria
├── SECURITY.md          # Secrets handling, input validation, and security boundaries
├── TODO.md              # Build tracker showing completed tasks
├── backend/
│   ├── app/
│   │   ├── api/         # Thin route handlers (profiles, weather, plans, alerts, chat)
│   │   ├── models/      # SQLAlchemy ORM models (UserProfile, CachedResponse, Alert)
│   │   ├── schemas/     # Pydantic schemas for request/response validation
│   │   ├── services/    # Business logic (ai_service, weather_service, cache_service, alert_service)
│   │   └── main.py      # FastAPI entry point
│   ├── .env.example     # Environment variables template
│   └── pyproject.toml   # uv Python project configuration
└── frontend/
    ├── src/
    │   ├── components/  # React pages & components (Dashboard, PrepPlan, AlertsCenter, ProfilePicker)
    │   ├── lib/         # API clients, translations, type definitions
    │   ├── App.tsx      # Main application router and state management
    │   └── main.tsx     # Client entry point
    ├── index.html       # Single Page Application HTML root
    └── package.json     # Node.js project manifest
```

---

## 🚀 Setup & Installation

### Prerequisites
*   Node.js (v18+) & `npm`
*   Python (v3.10+) & `uv` (Fast Python package manager. [Install uv](https://docs.astral.sh/uv/getting-started/installation/))
*   A Google Gemini API key ([Get a Gemini API Key](https://ai.google.dev/))

### 1. Backend Setup
1.  Navigate to the `backend` directory:
    ```shell
    cd backend
    ```
2.  Create your local configuration environment file from the template:
    ```shell
    cp .env.example .env
    ```
3.  Open `.env` and fill in your keys:
    ```env
    GOOGLE_API_KEY=your_gemini_api_key_here
    # Optional: OpenWeatherMap API key (falls back to simulated weather if empty)
    OPENWEATHERMAP_API_KEY=your_openweathermap_api_key_here
    GEMINI_MODEL=gemini-2.5-flash
    ```
4.  Install Python dependencies and sync the virtual environment:
    ```shell
    uv sync
    ```
5.  Start the FastAPI development server:
    ```shell
    uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```
    The API docs will be available at `http://localhost:8000/docs`.

### 2. Frontend Setup
1.  Open a new terminal session and navigate to the `frontend` directory:
    ```shell
    cd frontend
    ```
2.  Install npm dependencies:
    ```shell
    npm install
    ```
3.  Start the Vite development server:
    ```shell
    npm run dev
    ```
    Open `http://localhost:5173/` in your browser to view the application.

---

## 🧪 Testing & Verification

### Run Backend Verification
Ensure all routes and services import properly:
```shell
cd backend
uv run python -c "from app.main import app; print('App imported successfully!')"
```

### Run Frontend Type Checks
To verify that all TypeScript type annotations compile successfully:
```shell
cd frontend
npx tsc --noEmit
```

---

## 🎬 How to Demo StormShield

To demonstrate the full capability of the application's weather-aware personalization:

1.  **Create Custom Profiles**:
    *   Create a profile for a family living on a **Ground Floor** in **Mumbai** with **elderly family members** (risk: high flooding/mobility issues).
    *   Create a second profile for a couple living in a **High Rise** in **Delhi** (risk: high wind speeds/power cuts).
    *   Observe the different risk levels, preparation timelines, and travel safety instructions generated.
2.  **Change Weather Scenarios**:
    *   On the **Dashboard**, use the **Weather Scenario** dropdown selector.
    *   Switch between `Normal`, `Heavy Rain`, and `Flood Risk`.
    *   Verify that the Dashboard Risk Score and the Preparedness Plan accordion update immediately (using cached/regenerated weather data).
3.  **Run the Alert Demo**:
    *   Go to the **Alerts** tab.
    *   Click **Start Demo Timeline**.
    *   This triggers a 2.5-minute async background task that pushes 5 escalating warnings (Rain Watch → Heavy Rain Warning → Flood Alert → Evacuation Advisory → Stabilizing).
    *   Observe the notifications pop up instantly as toast banners on whatever page you are browsing.
4.  **Bilingual Toggle**:
    *   Click the language indicator (`EN` / `हिं`) in the navbar.
    *   Verify that all text cards, checklist items, safety plans, and chat responses translate natively to Devanagari script.
