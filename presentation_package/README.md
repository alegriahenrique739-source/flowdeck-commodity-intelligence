# FlowDeck Presentation Package

FlowDeck is an Excel-native Commodity Trading Intelligence platform for Brent/WTI oil desks. It turns local CSV-style inputs into validated market curves, physical plus futures exposure analytics, hedge simulation, stress P&L, local run records, and trader-ready Excel reports.

This package is a lightweight review bundle for professors, recruiters, commodities professionals, and technical reviewers. It uses synthetic demo data only.

## Who It Is For

- Commodities professors reviewing applied trading analytics.
- Trading desks or recruiters looking for a serious desk workflow prototype.
- Technical reviewers inspecting FastAPI, Next.js, Excel reporting, and E2E coverage.
- Finance contacts who need a concise explanation of what the product does.

## Fastest Local Demo

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

Open:

```text
http://localhost:3000/demo
```

Fastest flow:

```text
/demo -> Run Sample Demo -> View Run Detail -> Download Excel Report
```

The Workspace page remains available for manual CSV upload:

```text
http://localhost:3000/workspace
```

For Public Demo V1.0, `/demo` is the intended public entry point. The Workspace upload flow should remain local/development-only until upload security and authentication are reviewed.

## Package Index

- `FLOWDECK_PRODUCT_BRIEF.md` - concise one-page product overview.
- `DEMO_SCRIPT.md` - short presentation script and demo flow.
- `DEMO_READY_CHECKPOINT.md` - pre-demo runbook and troubleshooting.
- `ARCHITECTURE_SUMMARY.md` - technical architecture summary.
- `LIMITATIONS_AND_ROADMAP.md` - current constraints and future roadmap.
- `screenshots/` - selected frontend screenshots from Playwright visual baselines.
- `sample_outputs/flowdeck_sample_demo_report.xlsx` - synthetic sample Excel report.

Deployment planning docs live in the main repository under:

```text
docs/DEPLOYMENT_GUIDE.md
docs/PUBLIC_DEMO_DEPLOYMENT_RUNBOOK.md
docs/PUBLIC_DEMO_SMOKE_TEST.md
docs/ENVIRONMENT_VARIABLES.md
docs/PUBLIC_DEMO_RELEASE_CHECKLIST.md
docs/PUBLIC_DEMO_V1_RELEASE_NOTES.md
docs/GITHUB_READINESS_CHECKLIST.md
docs/PUBLIC_DEMO_V1_TAG_NOTE.md
docs/GITHUB_REPO_DESCRIPTION.md
```

## Synthetic Data Disclaimer

All included screenshots and sample outputs are based on fake synthetic Brent/WTI demo data. FlowDeck does not include real trade data, licensed Bloomberg/Refinitiv/ICE/CME data, API keys, or secrets. It is analytics-only and does not execute trades.

## Current Limitations

- Local/demo mode only.
- Synthetic sample data only.
- No authentication.
- No database persistence.
- No production deployment packaging yet.
- Hedge recommendations require human review.
