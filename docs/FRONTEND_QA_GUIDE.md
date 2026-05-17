# Frontend QA Guide

This guide explains how to test FlowDeck frontend and local backend changes consistently. FlowDeck is local-first, uses synthetic demo data only, and keeps financial calculations in the FastAPI backend.

## Test Categories

### Backend Python Tests

Use for service logic, API routes, run metadata, Excel export, and any change that could affect analytics behavior.

```bash
python -m pytest
```

Run these before and after backend changes, API contract changes, or any work that touches shared sample data.

### Frontend Typecheck

Use for TypeScript correctness across pages, components, API clients, and Playwright tests.

```bash
cd frontend
npm run typecheck
```

Run this after any frontend code or type changes.

### Frontend Lint

Use for Next.js and React lint checks.

```bash
cd frontend
npm run lint
```

Run this after frontend component, page, or test changes.

### Frontend Production Build

Use to verify that the Next.js app compiles and prerenders correctly.

```bash
cd frontend
npm run build
```

Run this before calling a frontend increment stable. Existing webpack cache warnings may appear and are non-blocking if the build exits successfully.

### Playwright Smoke Tests

Use for main page rendering and navigation.

```bash
cd frontend
npm run test:e2e
```

This command runs all Playwright tests, including smoke, upload-flow, error-state, and visual tests. Use it before saving a stable frontend state.

### Workspace Upload-Flow E2E Tests

Use for the CSV upload workflow from sample files through Excel report download.

```bash
cd frontend
npm run test:e2e:workspace
```

Run this after changes to Workspace uploads, API client FormData handling, step actions, result panels, charts, or report download UX.

### Error-State E2E Tests

Use for API offline messaging, disabled action states, non-CSV warnings, backend validation errors, and report generation failures.

```bash
cd frontend
npm run test:e2e:errors
```

Run this after error handling, validation display, API status, or disabled-button UX changes.

### Visual Regression Screenshots

Use for stabilized frontend page states and Workspace chart layout.

```bash
cd frontend
npm run test:e2e:visual
```

Run this after chart, layout, spacing, typography, table, shell, or theme changes.

## When To Run What

- Backend formula or service changes: run `python -m pytest`, then targeted frontend E2E if the UI displays changed outputs.
- API endpoint or response shape changes: run `python -m pytest`, `npm run typecheck`, and relevant Playwright tests.
- General frontend UI changes: run `npm run typecheck`, `npm run lint`, `npm run build`, and `npm run test:e2e`.
- Workspace upload changes: run `npm run test:e2e:workspace`.
- Chart or layout changes: run `npm run test:e2e:visual`; update screenshots only when the visual change is intentional.
- Error handling changes: run `npm run test:e2e:errors`.
- Before committing, saving a stable backup, or handing off: run backend tests, frontend checks, and full Playwright E2E.

## Required Services

Backend command from the repository root:

```bash
python -m uvicorn backend.app.main:app --reload
```

The backend must be running at `http://127.0.0.1:8000` for:

- `npm run test:e2e:workspace`
- `npm run test:e2e:errors` for the invalid backend validation case
- `npm run test:e2e:visual` for the Workspace analytics screenshot
- Full `npm run test:e2e`

The Playwright config starts the Next.js dev server automatically with:

```bash
npm run dev
```

It uses `http://localhost:3000` by default. Override with:

```bash
PLAYWRIGHT_BASE_URL=http://localhost:3000 npm run test:e2e
```

For manual frontend QA:

```bash
cd frontend
npm run dev
```

Then open:

```text
http://localhost:3000
```

## Visual Screenshots

Visual screenshot baselines are stored under:

```text
frontend/tests/e2e/visual.spec.ts-snapshots/
```

Current baselines cover:

- Overview page.
- Runs dashboard empty state.
- Workspace empty state.
- Workspace analytics state with charts.

If a visual change is intentional, update baselines with:

```bash
cd frontend
npm run test:e2e:visual -- --update-snapshots
```

Then rerun:

```bash
npm run test:e2e:visual
```

Only update screenshots after reviewing the UI manually or confirming the change is intended. Do not update screenshots to hide accidental regressions.

## Debugging Failed Tests

### Backend Offline

Symptoms: API status shows offline, upload-flow tests fail, validation calls fail.

Fix:

```bash
python -m uvicorn backend.app.main:app --reload
```

Confirm:

```text
http://127.0.0.1:8000/health
```

### Port 8000 Already Used

Symptoms: Uvicorn cannot bind to port 8000, or tests hit an unexpected backend.

Fix: stop the existing backend process, then restart Uvicorn. Avoid changing API URLs unless the test environment is explicitly configured for it.

### Port 3000 Already Used

Symptoms: Playwright web server startup fails or opens an unexpected frontend.

Fix: stop the existing Next.js dev server, or set `PLAYWRIGHT_BASE_URL` to the intended local frontend URL.

### Stale Frontend Build

Symptoms: manual QA shows old UI after changes.

Fix: stop and restart `npm run dev`. For production checks, rerun:

```bash
npm run build
```

### Missing Node Or npm

Symptoms: frontend commands are not recognized.

Fix: install Node.js/npm or use the project environment where `frontend/node_modules` is installed. Then run:

```bash
cd frontend
npm install
```

### Screenshot Mismatch

Symptoms: `npm run test:e2e:visual` fails with a diff.

Fix: inspect the diff artifact. If the UI change is intended, update snapshots. If not, fix the UI regression and rerun the visual test.

### Excel Download Test Failure

Symptoms: Workspace upload-flow fails at report download.

Check:

- Backend is running.
- All three sample CSV files are available under `data/sample/`.
- `/reports/excel` still returns an `.xlsx` FileResponse.
- Browser downloads are not blocked by a test environment change.

### CORS Issue

Symptoms: manual browser requests fail while backend works from direct HTTP calls.

Check backend CORS origins. Default local frontend origins are:

```text
http://localhost:3000
http://127.0.0.1:3000
```

Override if needed:

```text
FLOWDECK_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Pre-Change Checklist

- Read `AGENTS.md` and `docs/PROJECT_STATUS.md`.
- Back up the project folder before major increments.
- Run `python -m pytest`.
- Run frontend typecheck, lint, and build for UI work.
- Verify the current app manually if the change affects layout or workflow.
- Avoid changing financial formulas without focused tests.

## Post-Change Checklist

- Run targeted tests for the changed area.
- Run full Playwright E2E if the UI changed.
- Run `python -m pytest` if backend contracts, data samples, or shared workflows changed.
- Update documentation when commands, behavior, or test responsibilities change.
- Update visual screenshots only for intentional UI changes.
- Create a fresh backup after all checks pass and the state is stable.
