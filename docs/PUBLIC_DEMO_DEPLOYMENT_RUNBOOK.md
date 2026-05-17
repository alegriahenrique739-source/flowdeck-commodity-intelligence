# Public Demo Deployment Runbook

This runbook records the Public Demo V1 deployment procedure and the currently deployed URLs.

Before pushing to GitHub or sharing a deployment, review `docs/PUBLIC_DEMO_RELEASE_CHECKLIST.md`.

## Deployment Objective

Create a public demo link for professors, recruiters, commodities professionals, and technical reviewers without exposing the full upload workflow publicly.

Public demo flow:

```text
/demo -> Run Sample Demo -> /runs/[runId] -> Download Excel Report
```

The `/workspace` upload workflow remains local/development-only until upload security, authentication, rate limiting, storage, and abuse controls are reviewed.

## Target URLs

Backend:

```text
https://flowdeck-api.onrender.com
```

Frontend:

```text
https://flowdeck-commodity-intelligence.vercel.app
```

Demo entry:

```text
https://flowdeck-commodity-intelligence.vercel.app/demo
```

## Deployment Order

1. Push the repo to GitHub.
2. Deploy the backend to Render or an equivalent FastAPI host.
3. Test backend `/health` and `/docs`.
4. Configure backend CORS with the frontend URL placeholder.
5. Deploy the frontend to Vercel.
6. Configure frontend API base URL.
7. Enable public demo mode.
8. Smoke test `/demo`.

## Environment Variable Matrix

### Backend

| Variable | Local value | Production placeholder | Required | Notes |
| --- | --- | --- | --- | --- |
| `FLOWDECK_ALLOWED_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000` | `https://flowdeck-commodity-intelligence.vercel.app` | Yes | Use exact origins. Avoid wildcard CORS. |
| `PORT` | Platform/dev-server provided | Render/platform provided | Yes in public host | Do not hardcode local ports in deployment config. |

No secrets are currently required for public demo mode.

### Frontend

| Variable | Local value | Production placeholder | Required | Notes |
| --- | --- | --- | --- | --- |
| `NEXT_PUBLIC_FLOWDECK_API_BASE_URL` | `http://127.0.0.1:8000` | `https://flowdeck-api.onrender.com` | Yes | Must point to the deployed FastAPI backend. |
| `NEXT_PUBLIC_FLOWDECK_PUBLIC_DEMO_MODE` | `false` | `true` | Yes for public demo | Emphasizes `/demo` and keeps Workspace out of top-level nav. |

## Backend Platform Setup Notes

Render-style setup:

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
- Root directory: repository root.
- Python: use a supported Python 3 runtime. The app is currently tested locally with modern Python 3.
- Health check: `https://flowdeck-api.onrender.com/health`
- API docs: `https://flowdeck-api.onrender.com/docs`

Common backend failure points:

- Missing or failed dependency install from `requirements.txt`.
- Wrong ASGI start command.
- `$PORT` not passed to Uvicorn.
- Sample data path issue if deployment root is wrong.
- CORS not updated with the deployed frontend URL.
- Ephemeral file storage removing generated run reports after restart.

## Frontend Platform Setup Notes

Vercel-style setup:

- Project root: `frontend/` if deploying the frontend as a subdirectory from the repo.
- Install command: Vercel default, or `npm install`.
- Build command: `npm run build`.
- Output: Next.js managed output.

Required env vars:

```text
NEXT_PUBLIC_FLOWDECK_API_BASE_URL=https://flowdeck-api.onrender.com
NEXT_PUBLIC_FLOWDECK_PUBLIC_DEMO_MODE=true
```

Common frontend failure points:

- Wrong backend API base URL.
- Public demo mode not enabled.
- Backend CORS not updated.
- Assuming `/workspace` is a public feature; it is local/development until secured.
- Vercel project root set to repo root instead of `frontend/`.

## Public Demo Smoke Test Checklist

Current manual pass status:

- `https://flowdeck-api.onrender.com/health` works.
- `https://flowdeck-commodity-intelligence.vercel.app/demo` opens.
- **Run Sample Demo** works.
- Generated `/runs/[runId]` detail page opens.
- Excel report downloads successfully.
- Render CORS includes `https://flowdeck-commodity-intelligence.vercel.app`.

After deployment:

- Frontend opens.
- `/demo` opens.
- **Run Sample Demo** works.
- `run_id` appears.
- **View Run Detail** works.
- **Download Excel Report** works.
- `/runs` shows the generated run.
- Backend `/health` works.
- Backend `/docs` works.
- Laptop layout is readable.
- Mobile layout is acceptable for basic review if practical.

## Rollback Plan

- Keep the local demo-ready backup available.
- Revert frontend env vars if the frontend points to a bad backend.
- Redeploy the previous Vercel build.
- Redeploy the previous backend commit.
- Disable or stop sharing the public demo link if backend demo runs fail.
- Use the local demo as fallback for meetings.

## Public Sharing Checklist

Before sending the link:

- Synthetic-data disclaimer is visible.
- Upload workflow is not promoted publicly.
- Report download works.
- Product brief and presentation package are current.
- No secrets are in the repo.
- CORS uses the exact frontend URL.
- App does not expose stack traces in normal error responses.
- `/demo` is the intended public entry point.

## Known Limitations In Public Demo

- Local/file-based run storage may be ephemeral.
- No authentication.
- No database.
- No durable storage.
- No production logs or monitoring.
- Synthetic data only.
- No trade execution.
- Hedge recommendations require human review.
