# Deployment Guide

This guide describes the first public demo deployment target for FlowDeck. It is intentionally minimal and keeps the public scope focused on backend-owned synthetic demo mode.

For the step-by-step dry-run procedure, see `docs/PUBLIC_DEMO_DEPLOYMENT_RUNBOOK.md`.
For post-deployment checks, use `docs/PUBLIC_DEMO_SMOKE_TEST.md`.
For environment variable details, see `docs/ENVIRONMENT_VARIABLES.md`.
Before pushing for public review, use `docs/PUBLIC_DEMO_RELEASE_CHECKLIST.md`.

## Target Architecture

- Frontend: Vercel-hosted Next.js app.
- Backend: Render or equivalent FastAPI host.
- Frontend calls backend through `NEXT_PUBLIC_FLOWDECK_API_BASE_URL`.
- Backend allows the deployed frontend origin through `FLOWDECK_ALLOWED_ORIGINS`.
- Public entry point: `/demo`.
- Public demo workflow: `/demo -> Run Sample Demo -> /runs/[runId] -> Download Excel Report`.
- Backend-owned synthetic data only.

The `/workspace` upload workflow remains local/development-only until upload security, authentication, rate limiting, storage, and abuse controls are reviewed.

## Backend Deployment

Render-style build command:

```bash
pip install -r requirements.txt
```

Render-style start command:

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

This repository includes a minimal `render.yaml` with those commands. If using another FastAPI host, keep the same ASGI entry point:

```text
backend.app.main:app
```

## Backend Environment Variables

Required:

```text
FLOWDECK_ALLOWED_ORIGINS=https://your-flowdeck-frontend.vercel.app
```

Platform-provided:

```text
PORT
```

Not implemented yet, but expected later:

```text
FLOWDECK_STORAGE_BACKEND
FLOWDECK_REPORT_RETENTION_HOURS
```

Do not use wildcard CORS by default.

## Frontend Deployment

Deploy the `frontend/` directory as the Vercel project root.

Required frontend environment variables:

```text
NEXT_PUBLIC_FLOWDECK_API_BASE_URL=https://your-flowdeck-api.onrender.com
NEXT_PUBLIC_FLOWDECK_PUBLIC_DEMO_MODE=true
```

When public demo mode is enabled:

- The top navigation emphasizes Demo.
- Workspace is hidden from top-level navigation.
- The Overview primary call to action points to `/demo`.
- The `/workspace` route still exists for local/development use if directly opened.

For local development, keep:

```text
NEXT_PUBLIC_FLOWDECK_API_BASE_URL=http://127.0.0.1:8000
NEXT_PUBLIC_FLOWDECK_PUBLIC_DEMO_MODE=false
```

## CORS Setup

Set backend CORS to the exact deployed frontend URL:

```text
FLOWDECK_ALLOWED_ORIGINS=https://your-flowdeck-frontend.vercel.app
```

If preview deployments need access, add only the exact preview origins you trust. Avoid `*`.

## Public Demo Smoke Test

After deployment:

1. Open backend `/health`.
2. Open backend `/docs`.
3. Open frontend `/demo`.
4. Click **Run Sample Demo**.
5. Confirm the run summary appears.
6. Click **View Run Detail**.
7. Confirm `/runs/[runId]` loads.
8. Click **Download Excel Report**.
9. Confirm the `.xlsx` file downloads.
10. Confirm the UI and docs clearly state synthetic demo data only.

## Known Limitations

- Run and report storage is file-based and may be ephemeral on public platforms.
- No authentication.
- No database persistence.
- No durable report storage.
- No cleanup job.
- No production logging or monitoring.
- No public upload security.
- Demo data is synthetic only.
- FlowDeck does not execute trades.
- Hedge outputs require human review.
