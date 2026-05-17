# FlowDeck Public Demo V1 Release Notes

## Release Name

FlowDeck Public Demo V1

## Release Purpose

FlowDeck Public Demo V1 is the first share-ready version intended for professors, recruiters, commodities professionals, and technical reviewers. It demonstrates a public-link workflow for Brent/WTI commodity trading intelligence using backend-owned synthetic demo data.

Public Demo V1 is live:

```text
Frontend: https://flowdeck-commodity-intelligence.vercel.app
Demo:     https://flowdeck-commodity-intelligence.vercel.app/demo
Backend:  https://flowdeck-api.onrender.com
Health:   https://flowdeck-api.onrender.com/health
```

Primary public flow:

```text
/demo -> Run Sample Demo -> /runs/[runId] -> Download Excel Report
```

## Current Capabilities

- Backend-owned synthetic demo workflow through `/demo/run`.
- Market data validation for Brent/WTI futures curves.
- Forward curve construction and calendar spread analytics.
- Futures position ingestion and exposure aggregation.
- Physical cargo ingestion and exposure aggregation.
- Net exposure engine by hedge index, exposure month, and book.
- Deterministic hedge simulation.
- Synthetic stress P&L.
- Professional Excel report generation and download.
- Local run metadata with read-only run detail views.
- Presentation package, deployment runbooks, and public demo release docs.
- Public Demo V1 tag note and GitHub repository description guidance.

## Local Manual Workflow

The local Workspace remains available for manual CSV upload:

```text
/workspace
```

It supports market data, futures positions, and physical cargo CSVs, then calls the same backend analytics endpoints. It should remain local/development-only until public upload security is explicitly implemented.

## Backend Capabilities

- FastAPI service layer.
- Pydantic schemas and validation.
- pandas CSV ingestion.
- openpyxl Excel report export.
- Demo mode endpoint using synthetic sample files.
- Run metadata and report download endpoints.
- CORS support through `FLOWDECK_ALLOWED_ORIGINS`.

## Frontend Capabilities

- Next.js, React, and TypeScript frontend.
- Public-demo-mode navigation through `NEXT_PUBLIC_FLOWDECK_PUBLIC_DEMO_MODE`.
- Dedicated `/demo` page.
- `/runs` dashboard and `/runs/[runId]` detail page.
- Local `/workspace` CSV upload workflow.
- Visual analytics in Workspace.
- Excel report download links.

## Test Status

Current release checks include:

- Backend pytest suite passing.
- Frontend typecheck passing.
- Frontend lint passing.
- Frontend production build passing.
- Public-demo-mode production build passing.
- Smoke tests passing in default mode.
- Smoke tests passing in public-demo mode.

## Known Limitations

- Synthetic demo data only.
- Local/file-based run and report storage may be ephemeral on public hosts.
- No authentication.
- No database persistence.
- No durable object storage.
- No production logging or monitoring.
- No rate limiting.
- No public upload security.
- No real market data integration.
- No trade execution.
- Hedge outputs require human review.

## Deployment Readiness Status

Deployed to Vercel plus Render-style FastAPI hosting for Public Demo V1. Still not production-ready.

Public demo env vars:

```text
NEXT_PUBLIC_FLOWDECK_API_BASE_URL=https://flowdeck-api.onrender.com
NEXT_PUBLIC_FLOWDECK_PUBLIC_DEMO_MODE=true
FLOWDECK_ALLOWED_ORIGINS=https://flowdeck-commodity-intelligence.vercel.app
```

Manual public deployment QA confirmed:

- Backend `/health` works.
- Public `/demo` opens.
- **Run Sample Demo** works.
- Generated `/runs/[runId]` detail page opens.
- Excel report downloads successfully.
- Render CORS includes the Vercel frontend origin.

## Intentionally Not Included Yet

- Authentication.
- Database persistence.
- Durable storage for reports.
- Public CSV upload security.
- Real market data feeds.
- Licensed market data redistribution.
- Trade execution.
- Portfolio/user management.
- Production audit trail.

## Next Roadmap Steps

- Keep the public demo link healthy and smoke-test after each deployment.
- Create or update a stable checkpoint tag named `public-demo-v1` after final checks pass.
- Decide whether to hide or gate `/workspace` at routing level before broader sharing.
- Add durable storage and cleanup policy if public demo usage increases.
- Add authentication and database persistence before production workflows.
