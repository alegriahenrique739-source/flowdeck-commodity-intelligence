# Deployment Readiness

This document captures the readiness audit and hardening plan for moving FlowDeck from a local demo to a public demo V1.0.

Related deployment procedure docs:

```text
docs/DEPLOYMENT_GUIDE.md
docs/PUBLIC_DEMO_DEPLOYMENT_RUNBOOK.md
docs/PUBLIC_DEMO_SMOKE_TEST.md
docs/ENVIRONMENT_VARIABLES.md
```

FlowDeck Public Demo V1.0 should let a reviewer open a public frontend URL, run the backend-owned sample demo, view the generated run detail, and download the synthetic Excel report without installing Python, Node, or running local terminals.

## Target Public Demo Architecture

- Frontend: public Next.js deployment.
- Backend: public FastAPI deployment.
- Frontend API base URL is configured with `NEXT_PUBLIC_FLOWDECK_API_BASE_URL`.
- Backend allows the deployed frontend origin through `FLOWDECK_ALLOWED_ORIGINS`.
- Demo mode uses backend-owned synthetic Brent/WTI sample data.
- Backend remains the source of truth for all financial logic.
- Frontend displays API responses and does not duplicate formulas.

Expected public demo path:

```text
Public frontend URL -> /demo -> Run Sample Demo -> /runs/[runId] -> Download Excel Report
```

## Recommended First Public Demo Scope

Public-facing:

- `/demo`
- `/runs`
- `/runs/[runId]`
- Run-scoped Excel report download

Local/development until secured:

- `/workspace` manual CSV upload workflow

The upload workflow should not be exposed publicly without explicit security review. Public file upload needs safeguards around file size, file type, content validation, abuse prevention, rate limits, logging, retention, and user isolation. The first public demo should rely on backend-owned synthetic sample data through `/demo/run`.

## Environment Variables

Frontend:

```text
NEXT_PUBLIC_FLOWDECK_API_BASE_URL=http://127.0.0.1:8000
NEXT_PUBLIC_FLOWDECK_PUBLIC_DEMO_MODE=false
```

Public example:

```text
NEXT_PUBLIC_FLOWDECK_API_BASE_URL=https://flowdeck-api.example.com
NEXT_PUBLIC_FLOWDECK_PUBLIC_DEMO_MODE=true
```

Backend:

```text
FLOWDECK_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

Public example:

```text
FLOWDECK_ALLOWED_ORIGINS=https://flowdeck-demo.example.com
```

Local backend run command:

```bash
python -m uvicorn backend.app.main:app --reload
```

Public backend start command:

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

Public platforms commonly provide host and port values through their own environment. Keep those platform-specific values out of the repository unless they are non-secret examples.

## File, Run, And Report Storage Risk

Current local storage:

```text
runs/<run_id>/run_metadata.json
runs/<run_id>/flowdeck_report.xlsx
```

This is acceptable for local demos because data is synthetic, file volume is low, and runs are local-only. It is not production persistence.

Public demo implications:

- Many deployment platforms have ephemeral filesystems.
- Generated reports may disappear when the service restarts.
- There is no cleanup job yet.
- There is no database yet.
- There is no user isolation yet.
- Run IDs are local metadata references, not authenticated resources.

For Public Demo V1.0, use this only for short-lived synthetic demo runs. Production should add durable storage, cleanup policy, access control, and audit logging.

## CORS Readiness

Current local origins:

```text
http://localhost:3000
http://127.0.0.1:3000
```

Before public sharing:

- Add the deployed frontend URL to `FLOWDECK_ALLOWED_ORIGINS`.
- Avoid wildcard CORS by default.
- Keep credentials disabled unless authentication is explicitly added.
- Verify `/demo/run`, `/runs/{run_id}`, and `/runs/{run_id}/report` work from the deployed frontend.

## Security Notes

- No secrets should be committed to the repository.
- No real trade data should be committed or used in the public demo.
- No licensed Bloomberg, Refinitiv, ICE, CME, or similar market data should be redistributed.
- No authentication exists yet.
- Public upload should remain disabled or clearly local/development-only until secured.
- Demo mode should use only backend-owned synthetic sample data.
- FlowDeck is analytics-only and does not execute trades.
- Hedge recommendations require human review.

## Deployment Platform Options

Frontend candidates:

- Vercel
- Netlify
- Azure Static Web Apps

Backend candidates:

- Render
- Railway
- Fly.io
- Azure App Service
- AWS App Runner or ECS

Keep the first public demo deployment simple. Do not add platform-specific configuration until the chosen platform is known.

## Public Demo Checklist

Before sharing a public link:

- Backend is reachable.
- Frontend is reachable.
- Frontend points to the public backend through `NEXT_PUBLIC_FLOWDECK_API_BASE_URL`.
- Backend CORS allows the public frontend origin.
- `/demo` loads.
- `POST /demo/run` succeeds.
- Generated `/runs/[runId]` page loads.
- `/runs/{run_id}/report` downloads an `.xlsx` file.
- `NEXT_PUBLIC_FLOWDECK_PUBLIC_DEMO_MODE=true` is set for the deployed frontend.
- The UI and docs clearly state synthetic demo data only.
- `/workspace` upload flow is not publicly exposed, or is clearly marked local/development-only behind an explicit security decision.
- No secrets are present in environment examples or committed files.
- Local run/report storage behavior is understood for the chosen platform.

## Known Blockers Before Production

- Authentication and authorization.
- Database persistence.
- Durable report storage.
- Storage cleanup policy.
- Production logging.
- Monitoring and alerting.
- Rate limiting and abuse protection.
- Upload security.
- User and portfolio isolation.
- Real market data license integration.
- Audit trail and retention controls.
- Deployment packaging and operational runbooks.
