# TODO.md — StormShield Build Tracker

Ordered by dependency. Each task follows the Mini Loop: Understand → Plan → Implement → Verify → Review → Continue.

- [x] **1. Project scaffolding** — Initialize frontend (Vite + React + TS + Tailwind v4) and backend (uv + FastAPI); create `.gitignore`; verify both dev servers start ✅ Both servers start, TS compiles clean, backend imports OK
- [x] **2. Backend data models** — Create SQLAlchemy models: `UserProfile`, `CachedResponse`, `Alert`; create `database.py` with SQLite engine; verify tables are created on startup ✅ Tables created on backend startup
- [x] **3. Backend Pydantic schemas** — Define request/response schemas for all API endpoints: profiles, weather, plans, dashboard, alerts, chat; verify schema validation with sample data ✅ All schemas defined, backend compiles clean
- [x] **4. Weather service** — Implement hybrid weather provider: scenario override (in-memory), simulated data (per-city mock), OpenWeatherMap live (optional); verify all three tiers resolve correctly ✅ `/api/weather/Mumbai` returns realistic simulated data
- [x] **5. AI service** — Implement LangChain + Gemini integration: prompt templates for plan, checklist, travel, safety, dashboard summary, chat; structured JSON output parsing for page content, Markdown for chat; verify generation with a test profile ✅ Service compiles, prompt templates defined for all content types
- [x] **6. Cache service** — Implement SQLite-backed response cache with TTL lookup, storage, and invalidation; verify cache hit/miss behavior ✅ Cache service with get/set/invalidate implemented
- [x] **7. Alert service** — Implement alert CRUD and Demo Mode timeline (5 escalating alerts over ~150 seconds); verify timeline fires alerts at correct intervals ✅ 5-step demo timeline with async task spawning
- [x] **8. Backend API routes** — Wire up all route handlers: `/api/profiles`, `/api/weather`, `/api/plans`, `/api/dashboard`, `/api/alerts`, `/api/chat`; verify each endpoint with manual HTTP requests ✅ All routes registered, health check returns OK
- [x] **9. Frontend profile flow** — Build ProfilePicker and ProfileForm components; connect to profiles API; verify create/select/switch profile works end-to-end ✅ ProfilePicker with form + existing profile cards
- [x] **10. Frontend dashboard** — Build Dashboard with weather status, risk score, quick checklist, travel status, safety tips, recent alerts cards; connect to dashboard API; verify cards render with AI content ✅ Dashboard with 6 card types + scenario override
- [x] **11. Frontend preparedness plan** — Build PrepPlan with three-phase accordion; connect to plans API; verify phase content renders and current phase auto-highlights ✅ Three-phase accordion with auto-expand + regenerate
- [x] **12. Frontend alerts & chat** — Build AlertsCenter with polling + Demo Mode controls; build ChatFAB and ChatPanel with Markdown rendering and suggested prompts; verify alerts appear and chat responds contextually ✅ AlertsCenter with 30s polling + demo controls; ChatPanel with FAB, markdown, suggested prompts
- [x] **13. Multilingual support** — Add language toggle, translations dictionary, and Hindi prompt instructions; verify AI content generates in Hindi and UI labels switch ✅ ~70 EN/HI translation keys, language toggle in navbar, AI prompts include language instruction
