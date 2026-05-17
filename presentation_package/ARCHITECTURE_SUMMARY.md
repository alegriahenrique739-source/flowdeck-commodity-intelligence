# Architecture Summary

FlowDeck is a local-first analytics application with a Python/FastAPI backend, a Next.js frontend, and Excel report output.

## Backend

- FastAPI service layer exposes local endpoints for health, capabilities, demo runs, CSV validation, curves, positions, exposure, hedging, stress P&L, reports, and local run metadata.
- Route handlers stay thin and call service modules.
- Pydantic schemas validate inputs and outputs.
- pandas supports CSV loading.
- openpyxl generates professional Excel workbooks.

## Analytics Services

- Market data validation.
- Forward curve and calendar spread analytics.
- Futures position ingestion and exposure aggregation.
- Physical cargo ingestion and exposure aggregation.
- Net exposure engine.
- Hedge simulator.
- Stress P&L engine.

Financial logic remains in backend service modules. The frontend does not duplicate formulas.

## Frontend

- Next.js, React, TypeScript, and Tailwind.
- Overview, Demo, Runs dashboard, dynamic Run Detail, and Workspace pages.
- Demo page calls backend-owned `/demo/run`.
- Workspace uploads CSV files to existing FastAPI endpoints.
- Charts are presentation-only and use API response fields.

## Local Run Metadata

- Demo workflows create `runs/<run_id>/run_metadata.json`.
- Excel reports are stored as `runs/<run_id>/flowdeck_report.xlsx`.
- Run metadata is local JSON only, not database persistence.

## Data

- Synthetic Brent/WTI demo data only.
- No real trade data.
- No licensed Bloomberg/Refinitiv/ICE/CME redistribution.
- Future integrations should be bring-your-own-data / bring-your-own-license.

## Test Coverage

- Backend pytest tests.
- Frontend TypeScript typecheck.
- Next.js lint and production build.
- Playwright smoke tests.
- Workspace upload-flow E2E tests.
- Error-state E2E tests.
- Visual regression screenshots.

