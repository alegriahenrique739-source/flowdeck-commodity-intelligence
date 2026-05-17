# Public Demo V1 Tag Note

Use this note when creating the first clean public-demo checkpoint for FlowDeck.

## Suggested Tag

```text
public-demo-v1
```

## Suggested Backup Folder

```text
FlowDeck_PUBLIC_DEMO_V1_READY
```

## What This Checkpoint Includes

- Backend-owned synthetic demo workflow through `POST /demo/run`.
- Public-facing frontend demo path:

```text
/demo -> Run Sample Demo -> /runs/[runId] -> Download Excel Report
```

- FastAPI backend with validation, curves, exposure, hedging, stress P&L, Excel export, run metadata, and report download endpoints.
- Next.js frontend with `/demo`, `/runs`, `/runs/[runId]`, and local/development `/workspace`.
- Public-demo-mode frontend flag: `NEXT_PUBLIC_FLOWDECK_PUBLIC_DEMO_MODE=true`.
- Render-style backend deployment config and Vercel/Render deployment documentation.
- Presentation package, product brief, demo script, release notes, GitHub readiness checklist, and public demo runbooks.
- Synthetic sample data only.

## Test Status To Confirm Before Tagging

Run the final check set immediately before creating the tag:

```bash
python -m pytest
cd frontend
npm run typecheck
npm run lint
npm run build
NEXT_PUBLIC_FLOWDECK_PUBLIC_DEMO_MODE=true npm run build
npm run test:e2e -- tests/e2e/smoke.spec.ts
NEXT_PUBLIC_FLOWDECK_PUBLIC_DEMO_MODE=true npm run test:e2e -- tests/e2e/smoke.spec.ts
```

Expected status for this checkpoint:

- Backend tests passing.
- Frontend typecheck passing.
- Frontend lint passing.
- Frontend default production build passing.
- Frontend public-demo-mode production build passing.
- Smoke tests passing in default mode.
- Smoke tests passing in public-demo mode.

## Demo Path

Fastest reviewer path:

```text
Open /demo
Click Run Sample Demo
Open the generated /runs/[runId] detail page
Download Excel report
```

## Known Limitations

- Synthetic demo data only.
- No real trade data.
- No licensed Bloomberg, Refinitiv, ICE, CME, or similar market data.
- No authentication.
- No database persistence.
- Local/file-based run and report storage may be ephemeral on hosted platforms.
- No durable object storage or cleanup policy yet.
- No public upload security.
- `/workspace` should remain local/development-only until secured.
- No trade execution.
- Hedge outputs require human review.

## Do Not Include In GitHub

- `.env`, `.env.local`, or other local environment files.
- API keys, credentials, tokens, or secrets.
- `frontend/node_modules/`.
- `frontend/.next/`.
- `frontend/test-results/` and Playwright reports.
- `.pytest_cache/`, `__pycache__/`, `.uv-cache/`.
- Generated `runs/<run_id>/` folders except `runs/.gitkeep`.
- Generated reports under `reports/` except intentionally documented synthetic sample outputs.
- Temporary downloads or local-only artifacts.

## Rollback Note

Keep a local backup named `FlowDeck_PUBLIC_DEMO_V1_READY` before deployment experiments. If a public demo deployment fails, revert to this checkpoint, restore the previous frontend/backend deployment, or disable the public link while continuing to use the local demo for presentations.
