# FlowDeck

Release candidate: [restricted public deployment handoff](docs/PUBLIC_RELEASE_CANDIDATE.md).
This branch excludes private/local advanced development. Deploy only in explicit
public-demo mode; keep search indexing off pending live review.

Excel-native Commodity Trading Intelligence for Brent/WTI oil desks.

FlowDeck is a Python/FastAPI plus Next.js analytics product that validates synthetic market and position data, builds Brent/WTI forward curves, combines physical cargoes and futures positions, simulates hedges, stress-tests P&L, tracks demo runs, and exports trader-ready Excel reports.

Public Demo V1 flow:

```text
/demo -> Run Sample Demo -> /runs/[runId] -> Download Excel Report
```

Live Public Demo V1:

```text
Frontend: https://flowdeck-commodity-intelligence.vercel.app
Demo:     https://flowdeck-commodity-intelligence.vercel.app/demo
Backend:  https://flowdeck-api.onrender.com
Health:   https://flowdeck-api.onrender.com/health
```

Local demo commands:

```bash
python -m uvicorn backend.app.main:app --reload
cd frontend
npm run dev
```

Start at:

```text
http://localhost:3000/demo
```

FlowDeck uses synthetic demo data only. It does not include licensed market data, real trade data, API keys, or secrets. It is analytics-only, not trade execution and not financial advice.

Quick review links:

- `presentation_package/`
- `docs/FLOWDECK_PRODUCT_BRIEF.md`
- `docs/PUBLIC_DEMO_V1_RELEASE_NOTES.md`
- `docs/GITHUB_READINESS_CHECKLIST.md`
- `docs/PUBLIC_DEMO_V1_TAG_NOTE.md`
- `docs/GITHUB_REPO_DESCRIPTION.md`
- `docs/DEPLOYMENT_GUIDE.md`
- `docs/PUBLIC_DEMO_DEPLOYMENT_RUNBOOK.md`

## V1 Scope

- Commodities: Brent and WTI only
- Data input: backend-owned synthetic sample data for public demo; local CSV upload for development Workspace
- Market data: forward prices by commodity and contract maturity
- Positions: paper futures positions
- Physical exposure: simplified cargo exposures
- Analytics:
  - market data validation
  - forward curve construction
  - calendar spread calculation
  - net exposure by commodity and maturity
  - hedge simulation for physical exposure
  - stress P&L scenarios
- Output: Excel reports for traders

## Preferred Stack

- Backend: Python, FastAPI, Pydantic, pandas, openpyxl
- Tests: pytest
- Frontend: Next.js, React, TypeScript, Tailwind CSS
- Browser tests: Playwright
- Reports: Excel files generated with openpyxl
- Future database: not implemented yet

## Repository Layout

```text
.
├── backend/
│   └── app/
│       ├── api/          # FastAPI routers, added later
│       ├── core/         # settings, app configuration
│       ├── db/           # SQLAlchemy models/session, added later
│       ├── domain/       # pure financial/domain logic
│       ├── schemas/      # Pydantic request/response/data schemas
│       └── services/     # orchestration around domain logic
├── data/
│   └── sample/           # fake realistic CSV/XLSX inputs
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DATA_CONTRACTS.md
│   ├── FORMULAS.md
│   └── ROADMAP.md
├── reports/              # generated Excel reports, gitignored later if needed
├── scripts/              # local utilities and sample data generation
└── tests/
    ├── fixtures/         # stable fake test data
    └── unit/             # calculation and validation tests
```

## Development Status

FlowDeck Public Demo V1 is deployed. The intended public entry point is `/demo`; the manual `/workspace` CSV upload flow should remain local/development-only until authentication, upload security, rate limiting, and storage review are implemented.

## Project Guardrails

Future Codex sessions should read:

- `AGENTS.md` for product identity, sign conventions, data rules, required commands, and engineering rules.
- `docs/PROJECT_STATUS.md` for the current stable product state.
- `docs/STABILIZATION_CHECKLIST.md` before major increments or financial behavior changes.

## Local Tests

Install dependencies:

```bash
pip install -r requirements.txt
```

Run tests:

```bash
pytest
```

Generate the sample Excel report:

```bash
python scripts/build_sample_excel_report.py
```

Close the existing workbook first if it is open in Excel; Windows will block overwriting an open `.xlsx` file.

Expected output:

```text
reports/flowdeck_sample_report.xlsx
```

The workbook includes:

- Executive Summary with key metrics, risk/hedge summary, and assumptions note
- Market Curves with a forward-curve line chart
- Calendar Spreads
- Futures Positions
- Physical Cargoes
- Net Exposure with a net exposure bar chart
- Hedge Simulation
- Stress P&L with a stress P&L bar chart
- Assumptions and controls

## Local API

Run the API locally:

```bash
python -m uvicorn backend.app.main:app --reload
```

For local frontend development, the backend allows these origins by default:

```text
http://localhost:3000
http://127.0.0.1:3000
```

Override them with:

```text
FLOWDECK_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

Available endpoints:

```text
GET  /health
GET  /capabilities
GET  /api/info
GET  /demo/sample-files
POST /demo/run
POST /market-data/validate
POST /curves/build
POST /positions/futures/analyze
POST /positions/physical/analyze
POST /exposure/net
POST /hedging/simulate
POST /risk/stress
POST /reports/excel
GET  /runs
GET  /runs/{run_id}
GET  /runs/{run_id}/report
```

Swagger docs:

```text
http://127.0.0.1:8000/docs
```

OpenAPI JSON:

```text
http://127.0.0.1:8000/openapi.json
```

The Swagger UI includes formal response models, product-area tags, example responses, and documented JSON error schemas. The Excel report endpoint is documented as a downloadable `.xlsx` file response.

API contract:

```text
docs/API_CONTRACT.md
```

Demo guide:

```text
docs/DEMO_GUIDE.md
```

Product brief:

```text
docs/FLOWDECK_PRODUCT_BRIEF.md
```

Product demo script:

```text
docs/PRODUCT_DEMO_SCRIPT.md
```

Demo mode UX plan:

```text
docs/DEMO_MODE_UX_PLAN.md
```

Frontend QA guide:

```text
docs/FRONTEND_QA_GUIDE.md
```

Demo-ready checkpoint:

```text
docs/DEMO_READY_CHECKPOINT.md
```

Presentation package:

```text
presentation_package/
```

The presentation package contains concise review docs, selected frontend screenshots, and a synthetic sample Excel report for professor, recruiter, commodities, or technical review conversations.

Deployment readiness:

```text
docs/DEPLOYMENT_READINESS.md
```

Deployment guide:

```text
docs/DEPLOYMENT_GUIDE.md
```

Public deployment QA:

```text
https://flowdeck-api.onrender.com/health works
https://flowdeck-commodity-intelligence.vercel.app/demo opens
Run Sample Demo works
/runs/[runId] opens from the generated run
Excel report downloads successfully
Render CORS includes https://flowdeck-commodity-intelligence.vercel.app
```

Public demo deployment runbook:

```text
docs/PUBLIC_DEMO_DEPLOYMENT_RUNBOOK.md
docs/PUBLIC_DEMO_SMOKE_TEST.md
docs/ENVIRONMENT_VARIABLES.md
docs/PUBLIC_DEMO_RELEASE_CHECKLIST.md
docs/PUBLIC_DEMO_V1_RELEASE_NOTES.md
docs/GITHUB_READINESS_CHECKLIST.md
```

FlowDeck Public Demo V1 is deployed. The intended public entry point is `/demo`: a reviewer can run the backend-owned synthetic sample workflow, view the generated run detail, and download the Excel report from a public link. The `/workspace` CSV upload workflow should remain local/development-only until it receives explicit upload security, authentication, rate limiting, and storage review.

Target first public demo stack:

```text
Frontend: https://flowdeck-commodity-intelligence.vercel.app
Backend: https://flowdeck-api.onrender.com
Frontend env: NEXT_PUBLIC_FLOWDECK_API_BASE_URL=https://flowdeck-api.onrender.com, NEXT_PUBLIC_FLOWDECK_PUBLIC_DEMO_MODE=true
Backend env: FLOWDECK_ALLOWED_ORIGINS=https://flowdeck-commodity-intelligence.vercel.app
```

Example health check:

```bash
curl http://127.0.0.1:8000/health
```

Example frontend-readiness metadata:

```bash
curl http://127.0.0.1:8000/api/info
```

Example backend-powered sample demo run:

```bash
curl -X POST "http://127.0.0.1:8000/demo/run?target_hedge_ratio=0.80&stress_scenario=PARALLEL_DOWN_5"
```

The response includes a `run_id`, summary metrics, `/runs/{run_id}` metadata link, and `/runs/{run_id}/report` Excel download link. Demo mode uses only backend-owned synthetic sample data.

Example market data validation:

```bash
curl -F "file=@data/sample/market_data/valid_brent_wti_futures.csv" ^
  http://127.0.0.1:8000/market-data/validate
```

Example Excel report generation:

```bash
curl -o reports/flowdeck_api_report.xlsx ^
  -F "market_data_file=@data/sample/market_data/valid_brent_wti_futures.csv" ^
  -F "futures_file=@data/sample/positions/valid_futures_positions.csv" ^
  -F "physical_file=@data/sample/positions/valid_physical_cargoes.csv" ^
  -F "target_hedge_ratio=0.80" ^
  -F "stress_scenario=PARALLEL_DOWN_5" ^
  http://127.0.0.1:8000/reports/excel
```

Example local run metadata listing:

```bash
curl http://127.0.0.1:8000/runs
```

Example local run filters:

```bash
curl "http://127.0.0.1:8000/runs?status=SUCCESS"
curl "http://127.0.0.1:8000/runs?run_type=DEMO_WORKFLOW"
curl "http://127.0.0.1:8000/runs?limit=5&status=SUCCESS"
```

Example local run report download:

```bash
curl -o reports/downloaded_flowdeck_report.xlsx ^
  http://127.0.0.1:8000/runs/FD-RUN-20260512-235500-ABC123/report
```

Frontend run detail page:

```text
http://localhost:3000/runs/<run_id>
```

Demo and Workspace generated runs link directly to this page.

## Local Frontend

The first frontend shell lives under `frontend/`. It is a read-only Next.js dashboard that calls the FastAPI backend and does not duplicate financial logic.

Run backend from the repository root:

```bash
python -m uvicorn backend.app.main:app --reload
```

Create at least one run for the dashboard:

```bash
python scripts/run_demo_workflow.py
```

Run frontend:

```bash
cd frontend
npm install
npm run dev
```

Frontend URL:

```text
http://localhost:3000
```

Demo page:

```text
http://localhost:3000/demo
```

Use the dedicated Demo page for presentations. It tells the FlowDeck workflow
story, calls backend-owned `/demo` endpoints, creates a run record, and returns
an Excel report download link without manual CSV selection.

Analytics Workspace:

```text
http://localhost:3000/workspace
```

The Workspace now includes a **Run Sample Demo** panel. It calls the backend-owned
`POST /demo/run` endpoint, uses synthetic sample files on the backend, creates a
run record, and returns an Excel report download link without manual CSV
selection.

Manual upload remains available. The workspace uploads the three sample CSV files
to existing FastAPI endpoints:

```text
data/sample/market_data/valid_brent_wti_futures.csv
data/sample/positions/valid_futures_positions.csv
data/sample/positions/valid_physical_cargoes.csv
```

The Workspace shows step-by-step status, disabled-action helper text, readable
validation errors, preview tables, collapsible raw JSON, and Excel report
download feedback. It also renders lightweight visual analytics for forward
curves, net exposure, hedge impact, and stress P&L from existing API responses.
Financial calculations remain backend-only.

Frontend API configuration:

```text
NEXT_PUBLIC_FLOWDECK_API_BASE_URL=http://127.0.0.1:8000
NEXT_PUBLIC_FLOWDECK_PUBLIC_DEMO_MODE=false
```

For a public demo deployment, set `NEXT_PUBLIC_FLOWDECK_PUBLIC_DEMO_MODE=true` so the top navigation emphasizes Demo and keeps Workspace out of the top-level public navigation. The `/workspace` route still exists for local/development use.

Frontend quality checks:

```bash
cd frontend
npm run typecheck
npm run lint
npm run build
npm run test:e2e
```

Workspace upload-flow browser test:

```bash
cd frontend
npm run test:e2e:workspace
```

The upload-flow test requires the backend at `http://127.0.0.1:8000` and uses
the synthetic CSV files under `data/sample/`.

Frontend error-state browser tests:

```bash
cd frontend
npm run test:e2e:errors
```

These tests cover API offline messaging, disabled Workspace actions, non-CSV
warnings, invalid backend validation responses, mocked sample-demo failure, and
mocked Excel report export failure. The invalid-validation case requires the
backend to be running.

Frontend visual regression screenshots:

```bash
cd frontend
npm run test:e2e:visual
```

The visual suite captures Overview, Runs dashboard empty state, Workspace empty
state, and Workspace analytics charts. If a visual change is intentional,
refresh baselines with:

```bash
npm run test:e2e:visual -- --update-snapshots
```

Install Playwright Chromium once if needed:

```bash
cd frontend
npx playwright install chromium
```

Run the internal end-to-end demo workflow without HTTP:

```bash
python scripts/run_demo_workflow.py
```

Expected demo workflow outputs:

```text
runs/<run_id>/run_metadata.json
runs/<run_id>/flowdeck_report.xlsx
```

The run metadata is local JSON only. It records the run ID, timestamps, input files, output report path, status, summary metrics, and any errors. This is lightweight local tracking, not database persistence.

Example REST Client requests:

```text
examples/api_requests.http
```

Current product capabilities:

- CSV validation for market data, futures positions, and physical cargoes
- Forward curves and calendar spreads
- Futures and physical exposure aggregation
- Net exposure by hedge index, month, and book
- Deterministic hedge simulation
- Synthetic stress P&L
- Professional Excel workbook generation
- Local FastAPI endpoints for the same service chain
- OpenAPI/Swagger contract documentation with response models
- Local demo workflow run metadata under `runs/`
- Read-only API endpoints for local run metadata
- Read-only API endpoint for run-scoped Excel report downloads
- Local CORS configuration for a future frontend
- `/api/info` metadata for local frontend clients
- Local Next.js frontend shell and read-only runs dashboard
- Dedicated frontend Demo page for presentation-oriented synthetic workflows
- Dynamic frontend run detail page at `/runs/[runId]`
- Upload-based Analytics Workspace for existing backend endpoints
- Polished Workspace UX with step status and readable validation feedback
- Workspace visual analytics for curves, exposure, hedge impact, and stress P&L
- Backend-powered demo mode endpoints for running the synthetic sample workflow
- Frontend Workspace "Run Sample Demo" panel for one-click synthetic demos
- Deployment readiness audit for a future public demo V1.0
- Playwright smoke tests for Overview, Runs, Workspace, and navigation
- Playwright Workspace upload-flow tests using synthetic sample CSVs
- Playwright frontend error-state tests for offline/error handling
- Playwright visual regression screenshots for stabilized frontend states

Current limitations:

- Synthetic/local data workflows only
- No authentication
- No database persistence
- Local run metadata is JSON-on-disk only
- Frontend is local-only and sends uploaded CSV files to the backend; no persistence or auth yet
- Public demo target should expose `/demo` first; `/workspace` upload remains local/development until secured
- Run detail pages are read-only views of local JSON metadata
- No deployment packaging
- No real market data integration

## Next Recommended Task

Prepare FlowDeck Public Demo V1.0:

1. Choose public frontend and backend hosting targets.
2. Add minimal deployment configuration for the chosen platforms.
3. Keep `/demo` as the public entry point and keep `/workspace` local/development-only until secured.
