# AGENTS.md — StormShield

## Technology Stack

| Layer    | Technology                                                        |
|----------|-------------------------------------------------------------------|
| Frontend | Vite + React + TypeScript + Tailwind CSS v4 (@tailwindcss/vite)   |
| Backend  | Python + FastAPI, managed with `uv`                               |
| Database | SQLite via SQLAlchemy                                             |
| AI       | Google Gemini (gemini-2.5-flash default) via LangChain            |
| Packages | `npm` (frontend), `uv` (backend)                                 |

## Folder Conventions

```text
/
├── AGENTS.md
├── PROJECT.md
├── SECURITY.md
├── TODO.md
├── BASELINE.md
├── frontend/
│   ├── src/
│   │   ├── lib/           # API client, types, translations
│   │   └── components/    # React components (pages + shared)
│   ├── index.html
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── api/           # Route handlers (thin)
│   │   ├── services/      # Business logic, AI chains, weather
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic request/response schemas
│   │   └── main.py
│   ├── tests/
│   ├── .env               # Secrets — never committed
│   └── pyproject.toml
├── .gitignore
└── README.md
```

## Build / Test / Run Commands

```shell
# Frontend — install dependencies
cd frontend && npm install

# Frontend — development server (port 5173)
cd frontend && npm run dev

# Frontend — type check
cd frontend && npx tsc --noEmit

# Backend — install dependencies
cd backend && uv sync

# Backend — development server (port 8000)
cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Backend — run tests
cd backend && uv run python -m pytest tests/ -v
```

## Boundaries

### Always Do

- Use Pydantic schemas for all API request/response validation
- Load secrets from `backend/.env` via `python-dotenv`; use `os.getenv()`
- Return structured JSON from AI service for page content; Markdown for chat only
- Cache AI responses in SQLite before returning to the client
- Include `profile_id` context in every AI prompt
- Keep route handlers thin — delegate logic to services

### Ask First

- Adding a new Python or npm dependency
- Changing the SQLite schema (add a migration note)
- Modifying the weather scenario override format
- Altering the Demo Mode alert timeline sequence or timing

### Never Do

- Hardcode API keys in source files — use `.env` instead
- Commit `.env` or `stormshield.db` — add to `.gitignore` instead
- Install Docker, PostgreSQL, or Redis — use SQLite instead
- Use `pip` or `requirements.txt` — use `uv` instead
- Use the old `tailwind.config.js` workflow — use `@tailwindcss/vite` plugin instead
- Send raw unsanitized user input directly into LangChain prompts — escape/validate first
- Log API keys or full user chat messages — log sanitized summaries instead

## Definition of Done

A task is done when:
1. Code compiles/type-checks without errors (`npx tsc --noEmit`, `uv run python -c "import app"`)
2. The relevant API endpoint returns the expected schema (manually verified or tested)
3. The frontend component renders correctly in the browser
4. No secrets are exposed in source or logs
5. TODO.md item is marked `[x]` with an observed pass/fail result

## Related Documents

- **PROJECT.md** — problem statement, MVP scope, success criteria
- **SECURITY.md** — secrets handling, input validation, never-do list
- **TODO.md** — ordered build tracker derived from MVP scope
