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

## Environment

Commit only `.env.example` files. Do not commit real `.env`, `.env.local`, service-role keys, database passwords, provider tokens, or object storage credentials.

## Current Scope

This foundation intentionally does not include recommendation models, database tables, Supabase policies, production deployment, or service-role usage in the browser.
