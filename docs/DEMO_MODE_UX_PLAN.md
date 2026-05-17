# Demo Mode UX Plan

This plan defines a "Demo Mode / Load Sample Data" feature for FlowDeck. Increment 12.0 implemented the backend-owned demo service and `/demo` API endpoints. Increment 12.1 added the Workspace **Run Sample Demo** panel. Increment 12.2 added a dedicated frontend `/demo` page for presentations. Increment 12.3 adds direct run detail pages.

## Objective

Demo mode should make FlowDeck easier to present quickly and confidently. The current Workspace is functional, but manually selecting three CSV files slows the story down. A one-click sample workflow would help with:

- Faster product demos.
- Fewer manual setup steps.
- Cleaner recruiter, professor, and trader presentations.
- Easier storytelling around the full FlowDeck workflow.
- More repeatable local demonstrations.

## Current Pain Point

The Workspace currently requires users to manually select:

```text
data/sample/market_data/valid_brent_wti_futures.csv
data/sample/positions/valid_futures_positions.csv
data/sample/positions/valid_physical_cargoes.csv
```

This is acceptable for development and explicit upload testing, but it is not ideal for polished demos. Browser security also prevents a web page from silently reading arbitrary local files without user selection, so a naive "load these local files from the frontend" approach is not viable.

## UX Options Considered

### Option 1: Frontend-Only "Load Sample Data" Button

The frontend could include a button that loads bundled sample files.

Limitations:

- Browser security prevents silently loading arbitrary local project files.
- Sample CSVs would likely need to be copied into `frontend/public`.
- This risks duplicating demo data and drifting from backend sample files.
- It could encourage frontend-owned demo data paths, which is not ideal for FlowDeck's backend-owned analytics model.

### Option 2: Backend-Powered Demo Run Endpoint

Add a backend endpoint such as:

```text
POST /demo/run
```

The backend would use server-side sample files under `data/sample/`, run the full workflow, create run metadata, generate an Excel report, and return a run ID plus summary.

Benefits:

- Sample data remains backend-owned.
- No browser local-file bypassing.
- No financial logic duplicated in the frontend.
- Produces the same artifacts as the real workflow: metadata and Excel report.
- Fits future local and deployed demo environments.

### Option 3: Dedicated Demo Page

Add a frontend route such as:

```text
/demo
```

It could show one primary button:

```text
Run Sample Demo
```

After completion, the page could display:

- Curves summary.
- Net exposure summary.
- Hedge result.
- Stress result.
- Download report link.
- Link to run detail.

This page could be useful after the backend demo endpoint exists.

### Option 4: Improved Manual Upload Guidance

Keep the current upload flow and improve instructions around where sample files live.

Benefits:

- Low risk.
- No backend or frontend feature work.
- Keeps explicit user file selection.

Limitations:

- Still slower than a one-click product demo.
- Less polished for external presentations.

## Recommended Approach

Use a backend-powered demo mode.

Recommended product shape:

- Use `POST /demo/run`.
- Use `GET /demo/sample-files`.
- Add a frontend button labeled **Run Sample Demo**.
- Keep sample data backend-owned under `data/sample/`.
- After completion, show `run_id`, summary metrics, and report download.
- Link to the Runs dashboard or run detail.
- Do not duplicate financial logic in the frontend.

This preserves FlowDeck's source-of-truth boundary: the backend owns data loading, validation, analytics, run metadata, and report generation. The frontend displays results and links.

## Proposed Backend Design

Backend endpoints implemented in Increment 12.0:

```text
GET /demo/sample-files
POST /demo/run
```

### GET /demo/sample-files

Purpose:

Return metadata about available synthetic demo files.

Example response:

```json
{
  "market_data_file": "data/sample/market_data/valid_brent_wti_futures.csv",
  "futures_positions_file": "data/sample/positions/valid_futures_positions.csv",
  "physical_cargoes_file": "data/sample/positions/valid_physical_cargoes.csv"
}
```

### POST /demo/run

Purpose:

Run the full sample workflow server-side.

It should:

1. Load sample market data.
2. Load sample futures positions.
3. Load sample physical cargoes.
4. Build curves and calendar spreads.
5. Compute net exposure.
6. Simulate hedge with default target hedge ratio `0.80`.
7. Run `PARALLEL_DOWN_5` stress.
8. Generate Excel report.
9. Create run metadata.
10. Return `run_id`, summary metrics, and report URL.

Example response shape:

```json
{
  "run_id": "FD-RUN-20260515-140000-ABC123",
  "status": "SUCCESS",
  "summary": {
    "number_of_curves": 2,
    "number_of_net_exposure_buckets": 4,
    "total_net_exposure_bbl": "406000",
    "total_post_hedge_absolute_exposure_bbl": "81000",
    "total_stress_pnl_usd": "-2030000"
  },
  "report_url": "/runs/FD-RUN-20260515-140000-ABC123/report"
}
```

## Proposed Frontend Design

Add a compact demo panel near the top of the Workspace:

```text
Run Sample Demo
Use synthetic Brent/WTI sample files to generate curves, exposure, hedge simulation, stress P&L, and an Excel report.
```

Controls:

- Primary button: **Run Sample Demo**
- Secondary link: **View sample file details** if `GET /demo/sample-files` exists.

Loading state:

- Disable the button.
- Show "Running sample workflow..."
- Keep manual upload controls visible below.

Success state:

- Show `run_id`.
- Show summary metrics:
  - Curves.
  - Net exposure buckets.
  - Total net exposure.
  - Post-hedge absolute exposure.
  - Total stress P&L.
- Show actions:
  - **View in Runs**
  - **Download Excel Report**

Error state:

- Show a clear message.
- Avoid raw JSON in the main UI.
- Provide a retry button.

## Safety And Constraints

- Use synthetic demo data only.
- Do not include real trade data.
- Do not include licensed Bloomberg, Refinitiv, ICE, or CME data.
- Do not execute trades.
- Do not present outputs as financial advice.
- Hedge recommendations require human review.
- Backend remains the source of truth.
- Frontend must not duplicate formulas.
- Do not bypass browser local-file security.

## Testing Plan

### Backend Tests

- `POST /demo/run` returns a `run_id`.
- Demo run creates `runs/<run_id>/run_metadata.json`.
- Demo run creates `runs/<run_id>/flowdeck_report.xlsx`.
- Response summary matches the workflow result.
- Report URL resolves to a downloadable workbook.
- Invalid or missing sample data returns a clear error.
- Demo service does not mutate source sample files.

### Frontend Tests

- **Run Sample Demo** button is visible.
- Clicking the button calls `POST /demo/run`.
- Loading state is displayed.
- Success state displays `run_id` and summary metrics.
- **View in Runs** link works.
- **Download Excel Report** link works.
- Error state is displayed if the endpoint fails.
- Manual upload workflow remains available.

### Visual Tests

- Workspace empty state with demo panel.
- Workspace demo success state.
- Error state for failed demo run.

## Implementation Plan

### Increment 12.0: Backend Demo Run Service And Endpoint

- Status: implemented.
- Added demo orchestration service using existing loaders and analytics modules.
- Added `GET /demo/sample-files`.
- Added `POST /demo/run`.
- Reused run metadata and report generation services.
- Added backend tests.

### Increment 12.1: Frontend Demo Button On Workspace

- Status: implemented.
- Added Workspace demo panel.
- Calls `POST /demo/run`.
- Displays loading, success, and error states.
- Links to Runs and report download.
- Added E2E coverage.

### Increment 12.2: Dedicated Demo Page And E2E Tests

- Status: implemented.
- Added `/demo`.
- Presents a focused demo workflow separate from manual upload.
- Added Playwright smoke, upload-flow, and visual coverage.

### Increment 12.3: Dynamic Run Detail Page

- Status: implemented.
- Added `/runs/[runId]`.
- Demo and Workspace generated runs link directly to the run detail page.
- Added Playwright and visual coverage for run detail navigation.
