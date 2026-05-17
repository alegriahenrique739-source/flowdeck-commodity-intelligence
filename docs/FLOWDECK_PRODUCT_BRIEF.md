# FlowDeck — Excel-native Commodity Trading Intelligence

FlowDeck is a local-first analytics platform that turns Brent/WTI CSV inputs into validated curves, exposure analytics, hedge simulation, stress P&L, and trader-ready Excel reports.

## Problem

Commodity desk workflows often still rely on Excel and CSV exports. Market data, physical cargo positions, futures hedges, and stress analysis can be fragmented across files, tabs, and manual calculations. Analysts need outputs that are quick, auditable, and desk-ready without losing compatibility with Excel-native workflows.

## Solution

FlowDeck provides a structured analytics layer above local Excel/CSV workflows. It validates CSV inputs, builds Brent/WTI forward curves, combines physical cargoes and futures positions, computes hedgeable net exposure, simulates hedge recommendations, runs synthetic stress P&L, generates professional Excel reports, tracks local runs, and exposes the workflow through a local web interface.

## Core Capabilities

- Market data validation for Brent/WTI futures curves.
- Forward curve analytics and curve shape classification.
- Calendar spread analytics.
- Futures position ingestion and exposure aggregation.
- Physical cargo exposure ingestion and aggregation.
- Net exposure by hedge index, exposure month, and book.
- Deterministic hedge simulation.
- Synthetic stress P&L.
- Professional Excel report export.
- FastAPI backend with documented local endpoints.
- Next.js frontend with upload-based Analytics Workspace.
- Local run metadata and report download.
- Automated backend, frontend, E2E, and visual regression tests.

## Example Demo Workflow

```text
Upload market data + futures + physical cargo CSVs
-> validate
-> build curves
-> calculate net exposure
-> simulate hedge
-> stress test
-> export Excel report
```

## Why It Matters For A Commodities Desk

- Faster analysis from standard CSV inputs.
- Fewer manual Excel errors through validation and repeatable calculations.
- Clearer combined physical plus paper exposure view.
- Trader-ready reporting that fits existing Excel workflows.
- Local-first design that can evolve toward bring-your-own-data / bring-your-own-license integrations.

## Technical Architecture

- Python/FastAPI backend for validation, analytics, reports, and local run metadata.
- Next.js, React, and TypeScript frontend for local workflow presentation.
- openpyxl-based Excel workbook export.
- pytest backend coverage.
- Playwright frontend E2E and visual regression coverage.
- Synthetic demo data only.

## Current Validation Status

The current repo includes:

- Backend pytest suite with 144 passing tests.
- Frontend typecheck, lint, and production build checks.
- Playwright E2E tests for smoke, Workspace upload flow, error states, and visual screenshots.

## Limitations

- Local/demo mode only.
- Synthetic demo data only.
- No Bloomberg, Refinitiv, ICE, or CME data redistribution.
- No authentication or database persistence yet.
- Not trade execution.
- Not financial advice.
- Hedge outputs require human review.

## Future Roadmap

- Demo mode / load sample data UX.
- Richer charts and dashboard views.
- Database persistence.
- Authentication.
- External market data connectors using bring-your-own-data / bring-your-own-license architecture.
- Deployment packaging.
- User and portfolio management.

Demo mode planning is documented in `docs/DEMO_MODE_UX_PLAN.md`.

Demo-ready presentation guidance is documented in `docs/DEMO_READY_CHECKPOINT.md`.
