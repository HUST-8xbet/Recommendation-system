# Music Recommendation

Foundation for a music recommendation web app. This repository currently contains only the project skeleton: a Next.js frontend, a FastAPI backend, Supabase migration folder, and placeholder recommender package.

## Structure

```text
frontend/              Next.js app router frontend
backend/               FastAPI backend
supabase/migrations/   SQL migrations
recommender/           Future recommendation experiments and serving code
docs/                  Project notes and handoff documents
```

## Local Setup

### Backend

```bash
cd backend
uv sync --dev
uv run uvicorn app.main:app --reload
```

The backend serves `GET /health` on `http://localhost:8000/health`.
Set backend environment variables from `backend/.env.example` in the process environment when overriding defaults.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

The frontend expects `NEXT_PUBLIC_API_BASE_URL` to point at the backend, for example `http://localhost:8000`.

### Backend catalog local gate

Run these commands from `backend/`:

```bash
# Unit tests only (does not require Docker or Supabase)
uv run pytest -m "not integration"

# Integration tests; provide local Supabase values explicitly, never production values
SUPABASE_URL=http://127.0.0.1:54321 SUPABASE_PUBLISHABLE_KEY="<local-anon-key>" \
  uv run pytest -m integration

# Full local gate (integration test skips when local Supabase is unavailable)
uv run pytest
uv run ruff check .
uv run ruff format --check .
python -m compileall app tests
git diff --check
```

The integration test does not start Supabase, apply migrations, or seed data. Prepare the local instance separately with `supabase start` and `supabase db reset`; the test only connects to loopback and skips clearly when the local API is unavailable or credentials are not supplied.

## Environment

Commit only `.env.example` files. Do not commit real `.env`, `.env.local`, service-role keys, database passwords, provider tokens, or object storage credentials.

## Current Scope

This foundation intentionally does not include recommendation models, database tables, Supabase policies, production deployment, or service-role usage in the browser.
