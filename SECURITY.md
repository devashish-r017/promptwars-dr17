# SECURITY.md — StormShield

> This is hackathon-scope, demo-safe security — not production-hardened. Do not deploy to a public network without a full security review.

## Secrets Handling

- All secrets live in `backend/.env` and are loaded via `python-dotenv`
- Required: `GOOGLE_API_KEY`
- Optional: `OPENWEATHERMAP_API_KEY`, `GEMINI_MODEL`
- `.env` is listed in `.gitignore` — never committed
- No secret may appear in source code, logs, frontend bundles, or API responses

## Input Validation

| Boundary         | Method                                                                 |
|------------------|------------------------------------------------------------------------|
| API requests     | Pydantic schemas validate all incoming JSON bodies and query parameters |
| Profile fields   | City must be from the predefined Indian cities enum; family_size ≥ 1; dwelling_type from allowed enum values |
| Chat messages    | Max length enforced (2000 chars); stripped of control characters before passing to LangChain |
| Weather override | Scenario value must match a predefined enum (`normal`, `heavy_rain`, `flood_risk`, `cyclone_warning`, `post_monsoon_clear`) |
| AI prompt injection | User chat input is placed in a designated `{user_message}` template variable, never concatenated directly into the system prompt string |

## Never-Do List

| Never Do                                             | Do Instead                                                      |
|------------------------------------------------------|-----------------------------------------------------------------|
| Never log raw user chat messages                     | Log message length and timestamp only                           |
| Never include API keys in API responses or errors    | Return generic error messages; log key-related errors server-side only |
| Never trust client-supplied `profile_id` without DB lookup | Verify the profile exists in SQLite before using it          |
| Never return raw LLM errors to the frontend          | Catch exceptions in the AI service; return a user-friendly error message |
| Never commit `.env` or `stormshield.db`              | Ensure both are in `.gitignore` before first commit             |
| Never disable CORS in production                     | CORS is configured to allow only `http://localhost:5173` in dev |

## License & Package Compliance

- **Exception - `lightningcss` (MPL-2.0)**:
  - **Context**: CodeAnt or other compliance scanners might flag `lightningcss` as a "Non-Permissive Package" because it is under the MPL-2.0 weak copyleft license.
  - **Justification**: `lightningcss` is pulled in solely as a build-time devDependency by the `@tailwindcss/vite` plugin (required for Tailwind CSS v4) and `vite`. It is used exclusively for compilation, minification, and vendor prefixing of CSS.
  - **Distribution**: This package is **never distributed** to the client browser, nor is its source code modified. Only the raw compiled, standard-compliant CSS is served. Therefore, this usage is fully compliant and does not trigger any source-disclosure/copyleft requirements of MPL-2.0. It is a documented false positive in security reviews.

