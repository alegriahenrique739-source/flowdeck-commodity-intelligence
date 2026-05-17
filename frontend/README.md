# FlowDeck Frontend

Local Next.js frontend shell for FlowDeck. The UI is read-only and calls the FastAPI backend for all data and financial outputs.

## Backend

From the repository root:

```bash
python -m uvicorn backend.app.main:app --reload
```

Create at least one local run:

```bash
python scripts/run_demo_workflow.py
```

## Frontend Setup

```bash
cd frontend
npm install
```

Optional local environment file:

```bash
copy .env.local.example .env.local
```

Expected variable:

```text
NEXT_PUBLIC_FLOWDECK_API_BASE_URL=http://127.0.0.1:8000
NEXT_PUBLIC_FLOWDECK_PUBLIC_DEMO_MODE=false
```

For a public demo deployment, set:

```text
NEXT_PUBLIC_FLOWDECK_PUBLIC_DEMO_MODE=true
```

This emphasizes `/demo` in navigation and keeps Workspace out of the top-level public nav. The `/workspace` route remains available for local/development use.

## Run

```bash
npm run dev
```

Open:

```text
http://localhost:3000
```

Workspace:

```text
http://localhost:3000/workspace
```

Presentation demo:

```text
http://localhost:3000/demo
```

Use `/demo` for meetings and walkthroughs. It explains the FlowDeck story,
reuses the backend-owned **Run Sample Demo** panel, and links directly to
generated `/runs/[runId]` metadata pages and Excel reports. Use `/workspace`
when you want the manual CSV upload workflow.

Use synthetic sample files from the backend project:

```text
data/sample/market_data/valid_brent_wti_futures.csv
data/sample/positions/valid_futures_positions.csv
data/sample/positions/valid_physical_cargoes.csv
```

The Workspace includes a **Run Sample Demo** panel that calls the backend-owned
`POST /demo/run` endpoint. This runs the full synthetic Brent/WTI workflow
without manual CSV selection, then shows the run ID, summary metrics, Runs link,
and Excel report download link.

Manual upload remains available below the demo panel. The workspace uploads
selected files to existing FastAPI endpoints for validation, curves, positions,
net exposure, hedge simulation, stress P&L and Excel export. Each step shows
readiness, running, complete, and error states. Backend validation issues are
displayed as readable lists, with raw JSON available in collapsible debug
sections for analysts who need to inspect payloads.

Workspace visual analytics are rendered from existing API responses:

- Forward Curves line chart after curve build.
- Net Exposure by Bucket horizontal bar chart after net exposure.
- Hedge Impact before/after bar comparison after hedge simulation.
- Stress P&L by Bucket horizontal bar chart after stress analysis.

These charts are frontend presentation only. Exposure, hedge and stress
calculations remain backend-owned.

## Quality

For the full frontend QA workflow, see:

```text
../docs/FRONTEND_QA_GUIDE.md
```

```bash
npm run typecheck
npm run lint
npm run build
```

## Smoke Tests

Install Playwright browsers after installing dependencies:

```bash
npx playwright install chromium
```

Run lightweight frontend smoke tests:

```bash
npm run test:e2e
```

Run headed mode for local debugging:

```bash
npm run test:e2e:headed
```

The smoke tests start the Next.js dev server automatically and use
`http://localhost:3000` by default. Override with:

```bash
PLAYWRIGHT_BASE_URL=http://localhost:3000 npm run test:e2e
```

The backend is optional for the smoke tests. Pages should render even when API
status calls fail.

Run the Workspace upload-flow tests:

```bash
npm run test:e2e:workspace
```

These tests require the FastAPI backend to be running at
`http://127.0.0.1:8000` because they exercise `POST /demo/run`, upload the
synthetic sample CSV files, and call the real analytics endpoints. They use:

```text
data/sample/market_data/valid_brent_wti_futures.csv
data/sample/positions/valid_futures_positions.csv
data/sample/positions/valid_physical_cargoes.csv
```

The upload-flow tests also verify the Excel download event and expected
filename `flowdeck_workspace_report.xlsx`.

Run focused frontend error-state tests:

```bash
npm run test:e2e:errors
```

These tests cover API offline messaging, disabled Workspace actions,
non-CSV upload warnings, backend validation errors from an invalid market data
sample, a mocked sample-demo failure, and a mocked Excel report generation
failure. The validation-error test requires the FastAPI backend at
`http://127.0.0.1:8000`; API offline and mocked failure cases use Playwright
network interception.

Run lightweight visual regression screenshots:

```bash
npm run test:e2e:visual
```

The visual suite captures the Overview page, Demo page, run detail page, Runs
dashboard empty state, Workspace empty state, and Workspace analytics state with charts. The
analytics state uses the same synthetic sample CSV files and requires the
FastAPI backend at `http://127.0.0.1:8000`. API status, Demo sample-file
metadata, and Runs data are mocked where practical to keep screenshots stable.

If a frontend visual change is intentional, update baselines with:

```bash
npm run test:e2e:visual -- --update-snapshots
```

## Notes

- The frontend does not calculate exposure, hedge recommendations, stress P&L, or report content.
- The FastAPI backend remains the source of truth.
- The `/demo` page is the preferred presentation entry point.
- Generated demo runs link directly to `/runs/[runId]` for read-only metadata review.
- The Workspace is local/demo mode. Quick demos use backend-owned synthetic sample data through `/demo/run`; manual workflow testing uses user-selected CSV files from the local project folder.
- CORS is configured by the backend for `http://localhost:3000` and `http://127.0.0.1:3000` by default.
