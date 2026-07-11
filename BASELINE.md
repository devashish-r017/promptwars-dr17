# BASELINE.md

## Purpose
This document defines stable engineering decisions shared across all generated projects. This file is a compiler, not a project file. It defines HOW to generate a hackathon project harness — never WHAT to build.

## Provenance
This baseline is informed by contemporary research and production practices for AI coding agents, harness engineering, and repository instruction files. Update this document as best practices evolve

## Mandatory: human review gate
The agent must generate PROJECT.md, AGENTS.md, SECURITY.md, and TODO.md, then **stop and wait for human approval** before writing any implementation code. Auto-generated context files that are never reviewed measurably reduce task success and raise cost — generation is a draft step, not a final one.

## Global rules for every generated file
1. State WHAT is needed, not HOW to build it — no component names, no exact API endpoints, no database schema, no business logic detail in AGENTS.md. That detail belongs in PROJECT.md.
2. Length ceilings: AGENTS.md ≤ 120 lines. PROJECT.md, SECURITY.md, TODO.md ≤ 1 page each. If a file needs to grow past this, split into a new referenced file instead of expanding.
3. No redundancy across files. A fact lives in exactly one file. AGENTS.md points to the others by name and one-line description — it does not repeat their contents.
4. Every "don't" must be paired with a "do." A bare prohibition makes the agent overly cautious and conservative; a prohibition plus an alternative moves it forward correctly.
5. Prefer pointers over embedded detail. Reference other files and real file paths, not copied code snippets that can go stale.
6. Commands must be copy-pasteable and exact, with flags — never a vague verb like "run tests."
7. Omit anything the agent could discover itself by reading the code or package manifests.

## Mandatory Engineering Baseline
Unless explicitly overridden by the user, generated projects must use:
- Frontend: Vite + React + TypeScript + Tailwind CSS v4 (via @tailwindcss/vite plugin — not the old init/config-file approach) (Do not initialize using the deprecated tailwind.config.js workflow unless explicitly requested.)
- Backend: Python + FastAPI, managed with uv (Prefer uv over pip or requirements.txt unless explicitly requested.)
- DB: SQLite (Do not introduce PostgreSQL, Redis, Docker, or external infrastructure unless required by the problem statement.)
- Frontend package manager: npm

## Mandatory Repository Baseline
Repository conventions:
- Preserve this hierarchy by default.
- New directories may be introduced only when justified by the project.

```text
/
├── .git
├── AGENTS.md
├── frontend/
│   ├── src/
│   │   ├── lib/          # Backend/API communication only (Port 8000)
│   │   └── components/
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── api/          # Route handlers (thin)
│   │   ├── services/     # Business logic and AI clients
│   │   ├── models/
│   │   ├── schemas/
│   │   └── main.py
│   ├── tests/
│   ├── .env
│   └── pyproject.toml
├── .gitignore
└── README.md
```

## Mandatory Setup Commands
- Frontend
```shell
cd frontend
npm create vite@latest . -- --template react
npm install
npm install tailwindcss @tailwindcss/vite
```

- Backend
```shell
cd backend
uv init
uv add fastapi uvicorn sqlalchemy pydantic python-dotenv
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## AGENTS.md must contain
- Technology stack, derived from the Mandatory Technology Baseline unless explicitly overridden by the user.
- Folder conventions
- Build / test / run commands (exact)
- Boundaries, as three tiers: **Always do** / **Ask first** / **Never do** (Never-do items must name specifics, not general principles)
- Definition of Done
- One-line pointers to PROJECT.md, SECURITY.md, TODO.md

## AGENTS.md must NOT contain
- Component names, specific API endpoints, DB schema, business requirements — these live in PROJECT.md
- Code style prose — name the linter/formatter instead of describing style rules
- Anything already discoverable from the code itself

## PROJECT.md must contain (max 1 page)
- Problem statement, restated in one paragraph
- Goal (one sentence)
- Users (who this is for)
- MVP scope — what ships within the time box
- Non-goals — explicitly out of scope, as important as the MVP list
- Constraints (time box, environment, judging criteria if known)
- Success criteria — how you'll know the demo worked

## SECURITY.md must contain (max 1 page)
- Secrets handling rule: env vars only, never hardcoded, `.env` never committed
- Input validation requirement: where and how
- Never-do list, specific to this build (e.g. "never log raw user message text"), each paired with the safe alternative
- One line stating this is hackathon-scope, demo-safe security — not production-hardened. Don't overclaim.

## TODO.md must contain
- An ordered task list derived from PROJECT.md's MVP scope only — not from AGENTS.md
- Each item tagged: `[ ]` pending, `[~]` in progress, `[x]` done
- 10–15 items max. This is a build tracker, not a backlog.

## Mini Loop Engineering
Apply this loop to every task in TODO.md, in order, before marking it done:

```
1. Understand — restate the task in one sentence; confirm it maps to a PROJECT.md MVP item
2. Plan        — list the files that will change, in order
3. Implement   — write the code
4. Verify      — run the relevant command (test / lint / manual check); report the actual result
5. Review      — re-check the diff against AGENTS.md's Definition of Done
6. Continue    — mark the TODO.md item done; move to the next task
```
Do not skip Verify. A task is only "done" after an observed pass/fail result — never an assumption.

## Generation instructions
Given this file plus a problem statement, generate in this order:
1. **PROJECT.md** — from the problem statement alone
2. **AGENTS.md** — referencing PROJECT.md; add only stack, structure, and boundaries
3. **SECURITY.md** — scoped to what PROJECT.md's MVP actually touches
4. **TODO.md** — derived from PROJECT.md's MVP list, structured per Mini Loop Engineering

Then stop. Present all four files for human review. Do not begin implementation until approved.
