# FlowDeck Local Demo Guide

This guide walks through a local demo using only synthetic sample data.

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Run tests:

```bash
python -m pytest
```

Start the API:

```bash
python -m uvicorn backend.app.main:app --reload
```

Open Swagger docs:

```text
http://127.0.0.1:8000/docs
```

For a future local frontend, the backend allows these origins by default:

```text
http://localhost:3000
http://127.0.0.1:3000
```

## Sample Data

Use these fake local files:

```text
data/sample/market_data/valid_brent_wti_futures.csv
data/sample/positions/valid_futures_positions.csv
data/sample/positions/valid_physical_cargoes.csv
```

No real trade data, API keys, secrets, or licensed market data are used.

## Demo Story

FlowDeck takes a crude desk workflow from raw spreadsheet-style inputs to a trader-ready workbook:

1. Validate Brent and WTI futures market data.
2. Build ordered forward curves and calendar spreads.
3. Validate paper futures positions and physical cargoes.
4. Convert both into signed exposures.
5. Combine futures and physical exposure into a hedgeable net exposure view.
6. Generate deterministic hedge recommendations.
7. Run a synthetic stress P&L scenario.
8. Export a clean Excel workbook for desk review.

For a trader or analyst, the key message is: FlowDeck makes local commodity exposure work reproducible, inspectable, and Excel-native.

## Endpoint Walkthrough

Health:

```bash
curl http://127.0.0.1:8000/health
```

Capabilities:

```bash
curl http://127.0.0.1:8000/capabilities
```

API frontend-readiness metadata:

```bash
curl http://127.0.0.1:8000/api/info
```

Market data validation:

```bash
curl -F "file=@data/sample/market_data/valid_brent_wti_futures.csv" ^
  http://127.0.0.1:8000/market-data/validate
```

Build curves:

```bash
curl -F "file=@data/sample/market_data/valid_brent_wti_futures.csv" ^
  http://127.0.0.1:8000/curves/build
```

Analyze futures positions:

```bash
curl -F "file=@data/sample/positions/valid_futures_positions.csv" ^
  http://127.0.0.1:8000/positions/futures/analyze
```

Analyze physical cargoes:

```bash
curl -F "file=@data/sample/positions/valid_physical_cargoes.csv" ^
  http://127.0.0.1:8000/positions/physical/analyze
```

Build net exposure:

```bash
curl -F "futures_file=@data/sample/positions/valid_futures_positions.csv" ^
  -F "physical_file=@data/sample/positions/valid_physical_cargoes.csv" ^
  http://127.0.0.1:8000/exposure/net
```

Run hedge simulation:

```bash
curl -F "futures_file=@data/sample/positions/valid_futures_positions.csv" ^
  -F "physical_file=@data/sample/positions/valid_physical_cargoes.csv" ^
  -F "target_hedge_ratio=0.80" ^
  http://127.0.0.1:8000/hedging/simulate
```

Run stress P&L:

```bash
curl -F "futures_file=@data/sample/positions/valid_futures_positions.csv" ^
  -F "physical_file=@data/sample/positions/valid_physical_cargoes.csv" ^
  -F "scenario_name=PARALLEL_DOWN_5" ^
  http://127.0.0.1:8000/risk/stress
```

Generate Excel report:

```bash
curl -o reports/flowdeck_api_report.xlsx ^
  -F "market_data_file=@data/sample/market_data/valid_brent_wti_futures.csv" ^
  -F "futures_file=@data/sample/positions/valid_futures_positions.csv" ^
  -F "physical_file=@data/sample/positions/valid_physical_cargoes.csv" ^
  -F "target_hedge_ratio=0.80" ^
  -F "stress_scenario=PARALLEL_DOWN_5" ^
  http://127.0.0.1:8000/reports/excel
```

## Internal Demo Script

Run the end-to-end service workflow without HTTP:

```bash
python scripts/run_demo_workflow.py
```

Expected run outputs:

```text
runs/<run_id>/run_metadata.json
runs/<run_id>/flowdeck_report.xlsx
```

The terminal summary prints the `run_id`, status, core metrics, report path, and metadata path.

Run metadata contains:

- run ID and run type
- status: `RUNNING`, `SUCCESS`, or `FAILED`
- created and completed timestamps
- input sample file paths
- Excel output path
- summary metrics
- error messages if the workflow fails

This is local file-based metadata for repeatable demos. It is not database persistence and is not intended as production audit storage.

## Inspect Local Runs Through The API

After running the demo workflow, start the API:

```bash
python -m uvicorn backend.app.main:app --reload
```

List recent local runs:

```bash
curl http://127.0.0.1:8000/runs
```

Limit or filter returned runs:

```bash
curl "http://127.0.0.1:8000/runs?limit=5"
curl "http://127.0.0.1:8000/runs?status=SUCCESS"
curl "http://127.0.0.1:8000/runs?run_type=DEMO_WORKFLOW"
```

Inspect one run:

```bash
curl http://127.0.0.1:8000/runs/FD-RUN-20260512-235500-ABC123
```

Download the Excel report for one run:

```bash
curl -o reports/downloaded_flowdeck_report.xlsx ^
  http://127.0.0.1:8000/runs/FD-RUN-20260512-235500-ABC123/report
```

These endpoints are read-only and inspect local JSON metadata under `runs/`. The report download endpoint only serves the workbook when the metadata report path resolves inside the expected run folder.
