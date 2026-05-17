# FlowDeck Agent Guide

## Product Identity

- Project name: FlowDeck.
- Product: Excel-native Commodity Trading Intelligence platform for oil desks.
- Current scope: Brent/WTI oil analytics using synthetic demo data.
- Positioning: analytics layer above Excel/CSV workflows. FlowDeck is not trade execution and is not a CTRM replacement yet.

## Current Stable State

The repository currently includes:

- Market data validation.
- Forward curve builder.
- Calendar spread analytics.
- Futures position ingestion.
- Physical cargo ingestion.
- Net exposure engine.
- Hedge simulator.
- Stress P&L engine.
- Professional Excel report export.
- Excel chart polish.
- FastAPI service layer.
- API docs and demo workflow.
- Lightweight local workflow run metadata.
- Read-only run metadata API endpoints.
- Read-only run report download endpoint.
- Frontend readiness metadata and local CORS configuration.
- Minimal Next.js frontend shell and read-only runs dashboard.
- Frontend analytics workspace for CSV uploads to existing API endpoints.
- Workspace UI polish with step status, validation display, and report download UX.
- Playwright frontend smoke tests for Overview, Runs, Workspace, and navigation.
- Playwright Workspace upload-flow tests using synthetic sample CSVs and the real local backend.
- Playwright frontend error-state tests for API offline, disabled actions, validation failures, and report failure handling.
- Workspace visual analytics for forward curves, net exposure, hedge impact, and stress P&L using existing API responses.
- Playwright visual regression screenshots for Overview, Runs, Workspace empty state, and Workspace analytics charts.
- Frontend QA guide at `docs/FRONTEND_QA_GUIDE.md`.
- Product demo script at `docs/PRODUCT_DEMO_SCRIPT.md`.
- Product brief at `docs/FLOWDECK_PRODUCT_BRIEF.md`.
- Demo mode UX plan at `docs/DEMO_MODE_UX_PLAN.md`.
- Backend demo mode service and `/demo` API endpoints for running the synthetic sample workflow.
- Frontend Workspace "Run Sample Demo" panel using backend-owned synthetic demo mode.
- Dedicated frontend `/demo` page for presentation-oriented sample workflow demos.
- Dynamic frontend `/runs/[runId]` page for direct local run detail navigation.
- Polished demo handoff from `/demo` or Workspace to run detail and Excel report download.
- Demo-ready checkpoint guide at `docs/DEMO_READY_CHECKPOINT.md`.
- Presentation package at `presentation_package/` with concise docs, screenshots, and synthetic sample output.
- Deployment readiness audit at `docs/DEPLOYMENT_READINESS.md`.
- Deployment guide at `docs/DEPLOYMENT_GUIDE.md`.
- Public demo deployment runbook at `docs/PUBLIC_DEMO_DEPLOYMENT_RUNBOOK.md`.
- Public demo smoke checklist at `docs/PUBLIC_DEMO_SMOKE_TEST.md`.
- Environment variable reference at `docs/ENVIRONMENT_VARIABLES.md`.
- Public demo release checklist at `docs/PUBLIC_DEMO_RELEASE_CHECKLIST.md`.
- Public Demo V1 release notes at `docs/PUBLIC_DEMO_V1_RELEASE_NOTES.md`.
- GitHub readiness checklist at `docs/GITHUB_READINESS_CHECKLIST.md`.
- Public Demo V1 tag note at `docs/PUBLIC_DEMO_V1_TAG_NOTE.md`.
- GitHub repository description guidance at `docs/GITHUB_REPO_DESCRIPTION.md`.

## Required Commands

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run tests:

```bash
python -m pytest
```

Generate sample Excel report:

```bash
python scripts/build_sample_excel_report.py
```

Run demo workflow:

```bash
python scripts/run_demo_workflow.py
```

Run API locally:

```bash
python -m uvicorn backend.app.main:app --reload
```

Frontend QA guide:

```text
docs/FRONTEND_QA_GUIDE.md
```

Product demo script:

```text
docs/PRODUCT_DEMO_SCRIPT.md
```

Product brief:

```text
docs/FLOWDECK_PRODUCT_BRIEF.md
```

Demo mode UX plan:

```text
docs/DEMO_MODE_UX_PLAN.md
```

Demo-ready checkpoint:

```text
docs/DEMO_READY_CHECKPOINT.md
```

Deployment readiness:

```text
docs/DEPLOYMENT_READINESS.md
```

Deployment guide:

```text
docs/DEPLOYMENT_GUIDE.md
```

Public demo deployment runbook:

```text
docs/PUBLIC_DEMO_DEPLOYMENT_RUNBOOK.md
docs/PUBLIC_DEMO_SMOKE_TEST.md
docs/ENVIRONMENT_VARIABLES.md
docs/PUBLIC_DEMO_RELEASE_CHECKLIST.md
docs/PUBLIC_DEMO_V1_RELEASE_NOTES.md
docs/GITHUB_READINESS_CHECKLIST.md
docs/PUBLIC_DEMO_V1_TAG_NOTE.md
docs/GITHUB_REPO_DESCRIPTION.md
```

## Critical Financial Sign Conventions

- BUY physical = long exposure.
- SELL physical = short exposure.
- BUY futures = long exposure.
- SELL futures = short exposure.
- Positive net exposure = long price exposure.
- Negative net exposure = short price exposure.
- Long exposure loses when price falls.
- Short exposure gains when price falls.
- Stress P&L = `net_exposure_bbl * price_delta_usd_per_bbl`.
- Hedge recommendations must use `net_exposure_bbl`, not `gross_component_exposure_bbl`.
- `gross_component_exposure_bbl = abs(physical_exposure_bbl) + abs(paper_exposure_bbl)`.
- `absolute_net_exposure_bbl = abs(net_exposure_bbl)`.

## Data And Licensing Rules

- Use synthetic demo data only.
- Do not include real trade data.
- Do not include licensed Bloomberg, Refinitiv, ICE, or CME data.
- Do not include API keys or secrets.
- Design future market data integrations as bring-your-own-data / bring-your-own-license.
- Keep `presentation_package/` synthetic-data-only.

## Engineering Rules

- Keep route handlers thin.
- Keep financial logic in service modules.
- Add or update tests for every behavioral change.
- Existing tests must pass before and after work.
- Prefer small increments.
- Avoid broad refactors unless explicitly requested.
- Do not hardcode absolute local paths.
- Preserve existing API paths unless explicitly instructed.
- Preserve existing sample scripts unless explicitly instructed.
- Keep Excel output clean and institutional.
- Future frontend code must call the FastAPI backend and must not duplicate financial logic.
- Keep frontend features display-only unless backend API contracts are added first.
- Deployment/public demo changes must not expose upload workflows publicly without explicit security review.
- For Public Demo V1.0, prefer `/demo` as the public entry point and keep `/workspace` local/development-only until secured.
- Use `NEXT_PUBLIC_FLOWDECK_PUBLIC_DEMO_MODE=true` for public frontend deployments.

## Review Checklist

Before finishing any task, Codex must report:

- Files created.
- Files modified.
- Tests run.
- Full test result.
- Limitations.
- Next recommended increment.
