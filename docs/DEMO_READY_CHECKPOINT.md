# Demo-Ready Checkpoint

This checkpoint is the final pre-presentation runbook for FlowDeck. Use it before showing the product to a professor, recruiter, commodities professional, or technical reviewer.

## Current Demo-Ready Status

FlowDeck is ready for a local end-to-end demo with:

- FastAPI backend for validation, analytics, demo orchestration, run metadata, and Excel report downloads.
- Next.js frontend for Overview, Demo, Runs, Run Detail, and Workspace pages.
- Dedicated `/demo` page for the fastest presentation flow.
- `/workspace` manual CSV workflow for explicit market data, futures, and physical cargo upload.
- `/runs` dashboard for local run history.
- `/runs/[runId]` detail page for read-only run metadata review.
- Excel report download from generated demo runs.
- Backend-owned synthetic Brent/WTI demo data.
- Automated backend, frontend, E2E, error-state, and visual regression checks.

FlowDeck remains analytics-only. It does not execute trades and does not redistribute licensed market data.

## One-Command-Style Runbook

Terminal 1:

```powershell
cd C:\Users\alegr\Documents\Codex\FlowDeck
python -m uvicorn backend.app.main:app --reload
```

Terminal 2:

```powershell
cd C:\Users\alegr\Documents\Codex\FlowDeck\frontend
npm run dev
```

Check these URLs:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
http://localhost:3000
http://localhost:3000/demo
http://localhost:3000/workspace
http://localhost:3000/runs
```

## Fastest Demo Path

1. Open `http://localhost:3000/demo`.
2. Show the product story and synthetic-data safety notes.
3. Click **Run Sample Demo**.
4. Explain the summary metrics: curves, exposure buckets, total net exposure, post-hedge absolute exposure, and stress P&L.
5. Click **View Run Detail**.
6. Click **Download Excel Report**.
7. Open the downloaded Excel workbook.
8. Mention that `http://localhost:3000/workspace` supports the manual CSV workflow.

## Backup Checklist

Before any major future increment or presentation:

- Copy the full `FlowDeck` folder.
- Use a timestamped backup name.
- Run backend tests.
- Run frontend typecheck, lint, and build.
- Run E2E tests if the UI changed.
- Open `/demo` manually and run one sample demo.
- Confirm the generated Excel report downloads and opens.

Recommended backup name:

```text
FlowDeck_demo_ready_2026-05-17_increment_12_5
```

## Final QA Commands

Backend:

```powershell
python -m pytest
```

Frontend:

```powershell
cd frontend
npm run typecheck
npm run lint
npm run build
npm run test:e2e
npm run test:e2e:workspace
npm run test:e2e:errors
npm run test:e2e:visual
```

The Playwright suites require the backend at `http://127.0.0.1:8000`.

## Demo Troubleshooting

### Backend Offline

Check:

```text
http://127.0.0.1:8000/health
```

Restart from the repository root:

```powershell
python -m uvicorn backend.app.main:app --reload
```

### Frontend Offline

Restart from `frontend/`:

```powershell
npm run dev
```

Open:

```text
http://localhost:3000
```

### Port 8000 Already In Use

Stop the existing backend process, then restart Uvicorn. Avoid changing ports during a demo unless the frontend environment has also been updated.

### Port 3000 Already In Use

Stop the existing Next.js dev server, then rerun `npm run dev`.

### API Status Offline

Confirm:

- Backend is running on `127.0.0.1:8000`.
- Frontend environment uses `NEXT_PUBLIC_FLOWDECK_API_BASE_URL=http://127.0.0.1:8000`.
- CORS still allows `http://localhost:3000`.

### Excel Download Does Not Start

Check browser download permissions, then test the generated run report URL:

```text
http://127.0.0.1:8000/runs/<run_id>/report
```

### Tests Fail Because Backend Was Not Running

Start the backend before Playwright workspace, error-state, visual, or full E2E tests.

### Visual Screenshots Fail After Intentional UI Change

Inspect the screenshot diff first. If the change is intentional, update snapshots:

```powershell
cd frontend
npm run test:e2e:visual -- --update-snapshots
npm run test:e2e:visual
```

Do not update snapshots to hide accidental regressions.

## Reviewer Walkthrough

Use this 5-minute script:

```text
FlowDeck is an Excel-native commodity trading intelligence platform for oil desks. It sits above CSV and Excel workflows, validates input data, combines physical cargo and futures exposure, calculates hedgeable net exposure, simulates an offsetting hedge, stress-tests the book, and exports a trader-ready Excel workbook.

The demo uses synthetic Brent/WTI sample data owned by the backend. I open the Demo page, run the sample workflow, review the returned run metrics, open the generated run detail page, and download the Excel report. The value is repeatability: fewer spreadsheet errors, clearer physical plus paper exposure, and a report format that still fits how desks work.

The backend remains the source of truth for financial logic. The frontend displays API outputs and does not duplicate formulas. Current limitations are intentional: this is local/demo mode, no authentication, no database persistence, no real market data feed, and no trade execution.
```

## Do-Not-Touch Before Demo

Avoid these changes immediately before presenting:

- Changing financial formulas.
- Changing API endpoint behavior.
- Updating visual snapshots without reviewing the UI.
- Changing synthetic demo data.
- Adding dependencies.
- Large frontend refactors.
- Untested UI changes.
- Reworking Excel report structure.

## Current Limitations To Mention

- Synthetic/local demo mode only.
- No real market data license integration yet.
- No authentication.
- No database persistence.
- No trade execution.
- Hedge recommendations require human review.
- FlowDeck is not financial advice and is not a CTRM replacement yet.

