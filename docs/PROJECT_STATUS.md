# Project Status

FlowDeck is a deployed Public Demo V1 plus local development workflow for Brent/WTI oil desk analytics. It uses synthetic demo data only and exposes service-level Python modules, a FastAPI backend, and a Next.js frontend.

## Public Demo V1 Deployment

Public Frontend:

```text
https://flowdeck-commodity-intelligence.vercel.app
```

Public Demo Entry:

```text
https://flowdeck-commodity-intelligence.vercel.app/demo
```

Backend API:

```text
https://flowdeck-api.onrender.com
```

Public deployment QA status:

- `https://flowdeck-api.onrender.com/health` works.
- `https://flowdeck-commodity-intelligence.vercel.app/demo` opens.
- **Run Sample Demo** works.
- Generated `/runs/[runId]` detail page opens.
- Excel report downloads successfully.
- Render CORS includes the Vercel frontend origin.

Public scope remains:

```text
/demo -> Run Sample Demo -> /runs/[runId] -> Download Excel Report
```

The `/workspace` CSV upload workflow remains local/development-only until public upload security, authentication, rate limiting, storage, and abuse controls are implemented.

## Current Capabilities

- Validate oil futures market data CSV files.
- Build ordered Brent and WTI forward curves.
- Calculate calendar spreads.
- Validate and aggregate futures positions.
- Validate and aggregate simplified physical cargoes.
- Combine physical and paper exposure into hedgeable net exposure buckets.
- Simulate deterministic hedge recommendations from net exposure.
- Run synthetic stress P&L scenarios.
- Generate a professional Excel workbook with charts and assumptions.
- Validate generated workbook structure with a lightweight QA helper.
- Run an internal end-to-end demo workflow.
- Write local workflow run metadata as JSON files.
- Serve analytics through a local FastAPI layer with OpenAPI/Swagger documentation.
- Provide local frontend readiness metadata and CORS support for localhost Next.js-style clients.
- Provide a minimal local Next.js frontend shell with a read-only runs dashboard.
- Provide an upload-based frontend analytics workspace that calls existing API endpoints.
- Provide polished Workspace step states, readable validation errors, preview tables, and Excel report download UX.
- Provide a Workspace "Run Sample Demo" panel that calls backend-owned demo mode without manual CSV selection.
- Provide a dedicated frontend `/demo` page for presentation-oriented sample workflow demos.
- Provide a dynamic frontend `/runs/[runId]` page for direct read-only run metadata review.
- Provide a polished demo handoff from generated runs to run detail pages and Excel report downloads.
- Provide lightweight Workspace visual analytics for forward curves, net exposure, hedge impact, and stress P&L.
- Provide a lightweight `presentation_package/` with concise docs, selected screenshots, and a synthetic sample Excel output.
- Provide a deployment readiness audit for FlowDeck Public Demo V1.0.
- Provide minimal deployment guide and Render-style backend configuration for Public Demo V1.0 planning.
- Provide public demo deployment runbook, smoke checklist, and environment variable reference.
- Provide public demo release checklist and read-only repository hygiene checker.
- Provide Public Demo V1 release notes and GitHub readiness checklist.
- Provide Public Demo V1 tag note and GitHub repository description guidance.
- Provide deployed Public Demo V1 on Vercel and Render.
- Provide lightweight Playwright smoke tests for the main frontend pages.
- Provide Playwright Workspace upload-flow tests using synthetic CSV samples and the local backend.
- Provide Playwright frontend error-state coverage for API offline handling, disabled Workspace actions, backend validation failures, and report-generation failures.
- Provide lightweight Playwright visual regression screenshots for stabilized frontend states.
- Provide a frontend QA guide for test categories, commands, required services, visual snapshots, and troubleshooting.
- Provide a product demo script and manual presentation checklist for end-to-end FlowDeck demos.
- Provide a one-page product brief for professors, recruiters, commodities professionals, and technical reviewers.
- Provide a demo mode UX plan for the backend-powered "Run Sample Demo" workflow.
- Provide backend-owned demo mode endpoints that run the synthetic sample workflow without manual CSV upload.

## Current Endpoints

- `GET /health`
- `GET /capabilities`
- `GET /api/info`
- `GET /demo/sample-files`
- `POST /demo/run`
- `POST /market-data/validate`
- `POST /curves/build`
- `POST /positions/futures/analyze`
- `POST /positions/physical/analyze`
- `POST /exposure/net`
- `POST /hedging/simulate`
- `POST /risk/stress`
- `POST /reports/excel`
- `GET /runs`
- `GET /runs/{run_id}`
- `GET /runs/{run_id}/report`

Swagger documentation is available locally at:

```text
http://127.0.0.1:8000/docs
```

OpenAPI JSON is available locally at:

```text
http://127.0.0.1:8000/openapi.json
```

Frontend QA and test guidance is documented at:

```text
docs/FRONTEND_QA_GUIDE.md
```

Product demo guidance is documented at:

```text
docs/PRODUCT_DEMO_SCRIPT.md
```

Product brief is documented at:

```text
docs/FLOWDECK_PRODUCT_BRIEF.md
```

Demo mode UX plan is documented at:

```text
docs/DEMO_MODE_UX_PLAN.md
```

Demo-ready checkpoint guidance is documented at:

```text
docs/DEMO_READY_CHECKPOINT.md
```

Presentation package:

```text
presentation_package/
```

Deployment readiness:

```text
docs/DEPLOYMENT_READINESS.md
```

Deployment guide:

```text
docs/DEPLOYMENT_GUIDE.md
```

Public demo deployment procedure:

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

## Current Generated Artifacts

- `reports/flowdeck_sample_report.xlsx` from `scripts/build_sample_excel_report.py`.
- `runs/<run_id>/run_metadata.json` from `scripts/run_demo_workflow.py` or `POST /demo/run`.
- `runs/<run_id>/flowdeck_report.xlsx` from `scripts/run_demo_workflow.py` or `POST /demo/run`.
- Temporary API report files under `reports/api_tmp/`, cleaned up after API responses when possible.

Generated reports and local run records are ignored by git.

## Current Known Limitations

- Synthetic/local data workflows only.
- No real market data integration.
- No licensed market data redistribution.
- No authentication.
- No database persistence.
- Run metadata is local JSON only, not production persistence.
- Run metadata API endpoints are read-only and local-file based.
- Run report download is read-only and limited to the expected run folder.
- CORS is configured for local frontend origins only by default.
- Public Demo V1 is deployed on Vercel with a Render-hosted backend.
- Public Demo V1 target is `/demo` first, with run detail and Excel report download.
- Public demo mode can be enabled with `NEXT_PUBLIC_FLOWDECK_PUBLIC_DEMO_MODE=true`.
- `/workspace` upload flow should remain local/development-only until explicit upload security review.
- Workspace calculations remain backend-only; the UI displays API outputs.
- Workspace charts are frontend presentation components only and use existing API response fields.
- Frontend smoke tests verify rendering/navigation.
- Workspace upload-flow tests require the local backend and verify the CSV-driven workflow through Excel download.
- Frontend error-state E2E tests cover offline API messaging, disabled actions, non-CSV selection warnings, invalid market data validation, and mocked report export failure.
- Visual screenshot tests cover Overview, Demo, run detail, Runs empty state, Workspace empty state, and Workspace analytics chart state.
- Frontend QA guidance is documentation-only and does not replace manual review for material UI or workflow changes.
- Product demo guidance is documentation-only and assumes the local backend and frontend are running.
- Product brief is documentation-only and should be refreshed as capabilities or validation status changes.
- Demo mode has backend endpoints, a Workspace panel, a dedicated `/demo` page, and direct run detail pages.
- Demo-ready checkpoint guidance is documentation-only and should be reviewed before presentations or major increments.
- Presentation package artifacts are synthetic-data-only and should not include real trade data, licensed market data, API keys, or secrets.
- Minimal deployment packaging exists for the public demo, but not production operations.
- No trade execution.
- No CTRM replacement workflow yet.
- No VaR, scenario library management, or historical analytics.

## Next Possible Increments

- Keep the deployed Public Demo V1 healthy and smoke-test after each deployment.
- Use `docs/PUBLIC_DEMO_SMOKE_TEST.md` after each deployment attempt.
- Run `scripts/check_repo_hygiene.py` and review `docs/PUBLIC_DEMO_RELEASE_CHECKLIST.md` before GitHub/public release.
- Review `docs/GITHUB_READINESS_CHECKLIST.md` and `docs/PUBLIC_DEMO_V1_RELEASE_NOTES.md` before the first GitHub share.
- Use `docs/PUBLIC_DEMO_V1_TAG_NOTE.md` for the first stable tag and backup name.
- Use `docs/GITHUB_REPO_DESCRIPTION.md` when creating or polishing the GitHub repository page.
- Keep `/demo` public-facing and keep `/workspace` local/development-only until secured.
- Add deployment monitoring, cleanup policy, and durable storage planning if public usage grows.
- Add a richer run comparison or recent-runs summary later if useful for demos.
- Add bring-your-own-data market data integration design.
- Add authentication and database persistence only after the local workflow contract is stable.
