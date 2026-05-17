# Public Demo Release Checklist

Use this checklist before pushing FlowDeck to GitHub for reviewer access or attempting a public demo deployment.

Also review `docs/GITHUB_READINESS_CHECKLIST.md` and `docs/PUBLIC_DEMO_V1_RELEASE_NOTES.md` before the first public share.

## Pre-GitHub Hygiene

- No secrets.
- No `.env` or `.env.local` files.
- No `node_modules`.
- No `.next` build output.
- No Python caches.
- No old temporary runs intended for local-only use.
- No real trade data.
- No licensed Bloomberg, Refinitiv, ICE, CME, or similar market data.
- No API keys.
- No personal credentials.

## Required Files To Keep

- `README.md`
- `AGENTS.md`
- `requirements.txt`
- `render.yaml`
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/.env.local.example`
- `.env.example`
- `docs/`
- `presentation_package/`
- `data/sample/` synthetic demo CSV files
- Playwright visual screenshots when intentionally part of tests or the presentation package

## Files And Folders Generally Not To Commit

- `runs/` generated outputs except `runs/.gitkeep`
- `reports/` generated outputs unless specifically documented as a sample artifact
- Local caches
- Browser test artifacts
- Temporary downloads
- `.env`
- `.env.local`
- `frontend/node_modules/`
- `frontend/.next/`
- `frontend/test-results/`
- `.pytest_cache/`
- `__pycache__/`

## Test Checklist Before Release

- Backend tests: `python -m pytest`
- Frontend typecheck: `cd frontend && npm run typecheck`
- Frontend lint: `cd frontend && npm run lint`
- Frontend build: `cd frontend && npm run build`
- Public-demo-mode build: `NEXT_PUBLIC_FLOWDECK_PUBLIC_DEMO_MODE=true npm run build`
- Smoke tests: `cd frontend && npm run test:e2e -- tests/e2e/smoke.spec.ts`
- Public-demo-mode smoke tests: same command with `NEXT_PUBLIC_FLOWDECK_PUBLIC_DEMO_MODE=true`
- Optional full E2E: `cd frontend && npm run test:e2e`

## Manual Demo Checklist

- Local `/demo` works.
- **Run Sample Demo** works.
- Run detail page works.
- Excel report download works.
- `/workspace` is still treated as local/development.
- Public demo disclaimers are visible.
- Presentation package is current.

## Deployment Checklist

- Backend URL known.
- Frontend URL known.
- Backend CORS uses the exact frontend URL.
- Frontend API base URL is configured.
- Public demo mode is enabled.
- Backend `/health` works.
- Backend `/docs` works.
- Frontend `/demo` works.
- Report download works.

## Rollback Checklist

- Stable local backup exists.
- Previous frontend deployment can be restored.
- Previous backend deployment can be restored.
- Public link can be disabled if backend fails.
- Local demo remains available for meetings.

## Release Decision

Do not release publicly until:

- Hygiene warnings have been reviewed.
- Tests pass.
- Public demo mode build passes.
- Smoke tests pass.
- The demo has been manually run once end to end.
