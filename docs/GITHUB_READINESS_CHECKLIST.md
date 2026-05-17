# GitHub Readiness Checklist

Use this before pushing FlowDeck to GitHub or sharing the repository with reviewers.

## Include

- `README.md`
- `AGENTS.md`
- `.gitignore`
- `.env.example`
- `requirements.txt`
- `render.yaml`
- `backend/`
- `data/sample/` synthetic demo CSV files
- `docs/`
- `examples/`
- `frontend/` source files
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/.env.local.example`
- `presentation_package/`
- `scripts/`
- `tests/`
- `runs/.gitkeep`
- `reports/.gitkeep`

## Exclude

- `.env`
- `.env.local`
- `frontend/.env.local`
- `frontend/node_modules/`
- `frontend/.next/`
- `frontend/test-results/`
- `frontend/playwright-report/`
- `.pytest_cache/`
- `__pycache__/`
- `.uv-cache/`
- Generated `runs/<run_id>/` folders
- Generated report workbooks under `reports/`
- Temporary downloads

## .gitignore Verification

Confirm `.gitignore` covers:

- Local environment files.
- Python caches.
- Node dependencies.
- Next.js build output.
- Playwright test artifacts.
- Generated runs.
- Generated reports.
- Temporary uv cache.

## No Secrets Checklist

- No API keys.
- No credentials.
- No private tokens.
- No `.env` files.
- No personal account information.
- No secrets in docs or examples.

## Data Checklist

- No real trade data.
- No real counterparty data.
- No real positions.
- No real cargo data.
- No licensed Bloomberg, Refinitiv, ICE, CME, or similar data.
- Synthetic sample CSVs are clearly under `data/sample/`.

## Documentation Checklist

- `README.md` points to public demo deployment docs.
- `docs/DEPLOYMENT_GUIDE.md` is current.
- `docs/PUBLIC_DEMO_DEPLOYMENT_RUNBOOK.md` is current.
- `docs/PUBLIC_DEMO_RELEASE_CHECKLIST.md` is current.
- `docs/PUBLIC_DEMO_V1_RELEASE_NOTES.md` is current.
- `docs/PUBLIC_DEMO_V1_TAG_NOTE.md` is current.
- `docs/GITHUB_REPO_DESCRIPTION.md` is current.
- `presentation_package/` is concise and synthetic-data-only.

## Final Test Commands

Backend:

```bash
python -m pytest
```

Frontend:

```bash
cd frontend
npm run typecheck
npm run lint
npm run build
```

Public-demo-mode build:

```bash
cd frontend
NEXT_PUBLIC_FLOWDECK_PUBLIC_DEMO_MODE=true npm run build
```

Smoke tests:

```bash
cd frontend
npm run test:e2e -- tests/e2e/smoke.spec.ts
NEXT_PUBLIC_FLOWDECK_PUBLIC_DEMO_MODE=true npm run test:e2e -- tests/e2e/smoke.spec.ts
```

## Final Manual Demo Commands

Backend:

```bash
python -m uvicorn backend.app.main:app --reload
```

Frontend:

```bash
cd frontend
npm run dev
```

Manual check:

```text
http://localhost:3000/demo
Run Sample Demo
View Run Detail
Download Excel Report
```
