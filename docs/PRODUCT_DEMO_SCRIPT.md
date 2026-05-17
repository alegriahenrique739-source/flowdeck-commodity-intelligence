# Product Demo Script

FlowDeck demonstrates an Excel-native Commodity Trading Intelligence workflow for Brent/WTI oil desks. The demo shows CSV data intake, market data validation, forward curves, physical plus paper exposure, net exposure, hedge simulation, stress P&L, Excel report generation, and local run tracking.

For a concise shareable one-page overview, see `docs/FLOWDECK_PRODUCT_BRIEF.md`.

For the demo mode plan and backend `/demo` endpoints, see `docs/DEMO_MODE_UX_PLAN.md`.

For the final pre-presentation runbook, see `docs/DEMO_READY_CHECKPOINT.md`.

## Demo Objective

Show how FlowDeck turns local CSV inputs into a desk-ready analytics workflow:

- Ingest synthetic Brent/WTI market data and position files.
- Validate data quality before analytics.
- Build forward curves and calendar spread context.
- Combine physical cargo and futures positions into hedgeable net exposure.
- Simulate deterministic hedge recommendations.
- Run synthetic stress P&L scenarios.
- Export a professional Excel workbook.
- Track local demo runs and download prior reports.

FlowDeck is an analytics layer above Excel/CSV workflows. It does not execute trades and is not a CTRM replacement.

## Audience Positioning

### Commodities Professor

Position FlowDeck as a practical applied analytics platform that demonstrates commodity data contracts, futures curve construction, exposure aggregation, hedge logic, and stress P&L with clean sign conventions.

### Trading House Or Recruiter

Position FlowDeck as a serious desk-oriented prototype: local data intake, validation, exposure, hedge simulation, stress testing, and Excel output in a workflow that resembles how analysts and traders already work.

### Technical Reviewer

Position FlowDeck as a modular FastAPI plus Next.js application with backend-owned financial logic, typed frontend API calls, test coverage, visual regression screenshots, and local file-based run metadata.

### Non-Technical Finance Contact

Position FlowDeck as a tool that takes messy spreadsheet-style inputs, checks them, summarizes market and exposure risk, and produces a polished Excel report for review.

## Pre-Demo Setup Checklist

Start the backend from the repository root:

```bash
python -m uvicorn backend.app.main:app --reload
```

Start the frontend:

```bash
cd frontend
npm run dev
```

Optional: create a fresh local run record and Excel report before the demo:

```bash
python scripts/run_demo_workflow.py
```

Optional: create the same synthetic sample run through the backend API:

```bash
curl -X POST "http://127.0.0.1:8000/demo/run?target_hedge_ratio=0.80&stress_scenario=PARALLEL_DOWN_5"
```

Check these URLs before presenting:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
http://localhost:3000
```

## Demo Data

Use synthetic sample files only:

```text
data/sample/market_data/valid_brent_wti_futures.csv
data/sample/positions/valid_futures_positions.csv
data/sample/positions/valid_physical_cargoes.csv
```

Browser upload requires manually selecting these files from the local FlowDeck project folder.

## Demo Story

We start with Brent/WTI market data and sample physical plus futures positions. FlowDeck validates the data, builds curves, calculates net exposure, recommends a hedge, stress-tests the portfolio, and exports a trader-ready Excel report.

## Live Demo Flow

1. Open `http://localhost:3000`.
2. Show the FlowDeck Overview page and confirm API status is connected.
3. Open the Runs dashboard.
4. Show previous runs, run metadata, and report download if a run exists.
5. Open `http://localhost:3000/demo`.
6. Show the FlowDeck Demo story, data safety notes, and architecture section.
7. Keep target hedge ratio at `0.80` and stress scenario at `PARALLEL_DOWN_5`.
8. Click **Run Sample Demo**.
9. Show the returned run ID, summary metrics, run detail link, and Excel report download link.
10. Download and open the demo Excel workbook.
11. If time allows, open Workspace and show that manual CSV upload remains available for explicit file testing.
12. Upload the three sample CSV files and briefly step through validation, curves, positions, net exposure, hedge simulation, stress P&L, and Excel export.
13. Explain how the workbook supports desk review and Excel-native workflows.

## Talking Points

- FlowDeck does not execute trades.
- The backend remains the financial source of truth.
- The frontend does not duplicate formulas.
- Excel export fits existing desk workflows.
- All demo data is synthetic.
- Future market data integrations should be bring-your-own-data / bring-your-own-license.
- FlowDeck is useful as an analytics layer above Excel/CSV workflows.
- The current workflow is local-first and intentionally avoids database/auth complexity.

## Common Failure Checks

### Backend Offline

Check:

```text
http://127.0.0.1:8000/health
```

Restart:

```bash
python -m uvicorn backend.app.main:app --reload
```

### Wrong Port

Backend should be on `127.0.0.1:8000`. Frontend should be on `localhost:3000`.

### Frontend Cannot Connect To API

Confirm the frontend environment points to:

```text
NEXT_PUBLIC_FLOWDECK_API_BASE_URL=http://127.0.0.1:8000
```

### CSV Files Not Selected

The Workspace action buttons remain disabled until the required files are selected. Re-select the three sample CSV files from `data/sample/`.

### Excel Download Blocked

Check browser download permissions and confirm the backend `/reports/excel` endpoint is available.

### Browser Cache Or Stale Frontend

Restart `npm run dev` and refresh the browser.

### Tests Fail Because Backend Is Not Running

Workspace upload-flow, visual analytics screenshots, and part of the error-state tests require the backend at `http://127.0.0.1:8000`.

## Two-Minute Version

1. Open Overview and point out connected API status.
2. Open the Demo page and click **Run Sample Demo**.
3. Show run ID, summary metrics, run detail page, and report download link.
4. Open the Excel report.
5. Mention that the manual upload workflow below uses the same backend services for explicit CSV testing.

Script:

```text
FlowDeck takes Brent/WTI CSV inputs, validates them, builds curves, combines physical and futures exposure, estimates hedge impact, stress-tests the book, and exports a clean Excel workbook. It is analytics only, with backend-owned formulas and synthetic demo data.
```

## Seven-Minute Version

1. Start on Overview and explain local-first positioning.
2. Open API Docs briefly to show formal FastAPI contract.
3. Open Runs dashboard and explain local run metadata and report downloads.
4. Open the Demo page and show the backend-owned sample demo panel.
5. Click **Run Sample Demo** and explain that sample data remains backend-owned.
6. Show run summary metrics, direct run detail link, and report download.
7. Download and open the Excel workbook.
8. Scroll to the manual upload workflow and explain it uses the same backend services for explicit CSV testing.
9. If time allows, upload market data, futures positions, and physical cargoes.
10. Validate market data and explain why validation matters before analytics.
11. Build curves and point to Brent/WTI forward curves.
12. Compute net exposure, run hedge simulation, and run stress P&L.
13. Close by explaining where FlowDeck fits: an analytics layer above Excel/CSV workflows, not trade execution.

Closing line:

```text
The value is not replacing Excel; it is making the data, calculations, validation, and report generation around Excel more reliable and repeatable for an oil desk.
```
