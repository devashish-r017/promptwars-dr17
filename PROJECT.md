# PROJECT.md — StormShield

## Problem Statement

Every monsoon season, millions of individuals and families across India face flooding, waterlogging, electrical hazards, travel disruptions, and health risks — yet preparedness advice remains generic, static, and monolingual. There is no single tool that delivers **personalized**, **weather-aware**, **multilingual** guidance covering the full Before → During → After monsoon lifecycle with real-time situational awareness.

## Goal

Build a GenAI-powered web application that generates personalized monsoon preparedness plans, emergency checklists, travel advisories, safety recommendations, and real-time alerts — all tailored to the user's profile (location, family, dwelling) and current weather conditions, available in English and Hindi.

## Users

- **Individuals and families** in Indian cities preparing for or experiencing monsoon season
- **Demo audience** (hackathon judges) evaluating the app's personalization, weather-awareness, and AI capabilities

## MVP Scope — What Ships

1. **Profile Picker & Onboarding** — name-based profiles (no auth), quick form capturing city, family size, dwelling type, with advanced options; profile switcher for demo
2. **Dashboard** — weather status card with severity badge, personalized risk score gauge, condensed checklist card, travel status card, safety tips card, recent alerts feed
3. **Preparedness Plan** — AI-generated three-phase plan (Before/During/After) in expandable accordion; auto-highlights current phase; personalized to profile and weather; regenerate button
4. **Alerts Center** — polling-based alert feed (30s interval) with severity badges and AI-generated recommended actions; Demo Mode button triggering a scripted escalating alert timeline over ~2–3 minutes
5. **AI Chat Assistant** — global floating action button opening a slide-in panel; context-aware (profile + weather + current page); Markdown responses; session-scoped history; suggested prompt chips
6. **Weather System** — hybrid three-tier: scenario override → simulated data → OpenWeatherMap live (optional); scenario override panel for demo control
7. **Multilingual Support** — English + Hindi; AI-generated content in selected language; static UI labels via translation dictionary; language toggle in navbar
8. **Response Caching** — SQLite-backed cache with TTL (1h weather-dependent, 24h profile-only); invalidation on profile update or weather change

## Non-Goals — Explicitly Out of Scope

- User authentication with passwords or OAuth
- Mobile native app (responsive web only)
- More than two languages (English + Hindi only)
- Push notifications (browser Notification API, service workers)
- Map/GIS visualization of flood zones or routes
- Integration with government disaster APIs (NDMA, IMD)
- Production-grade deployment, CI/CD, or infrastructure
- Offline support / PWA

## Constraints

- **Time box**: hackathon scope — build to demo-ready, not production-hardened
- **Stack**: Vite + React + TypeScript + Tailwind CSS v4 (frontend), Python + FastAPI + SQLite (backend), LangChain + Google Gemini (AI) — per BASELINE.md
- **API keys**: requires `GOOGLE_API_KEY`; `OPENWEATHERMAP_API_KEY` optional
- **No external infra**: no Docker, Postgres, Redis — SQLite only

## Success Criteria

1. Two distinct profiles produce visibly different preparedness plans, checklists, and risk scores
2. Changing the weather scenario override causes all AI content to regenerate with weather-appropriate guidance
3. Demo Mode timeline delivers 5 escalating alerts over ~2–3 minutes with toast notifications
4. Language toggle switches all AI-generated content to Hindi (Devanagari script)
5. AI chat answers profile- and weather-aware questions on any page
6. App loads and operates without the OpenWeatherMap key (simulated weather fallback works)
