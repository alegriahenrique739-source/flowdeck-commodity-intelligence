# FlowDeck API Contract

Base URL for local development:

```text
http://127.0.0.1:8000
```

All upload endpoints currently accept local CSV files only. The API is file-based, local-first, unauthenticated, and does not persist uploaded files.

Interactive documentation:

```text
http://127.0.0.1:8000/docs
```

OpenAPI JSON:

```text
http://127.0.0.1:8000/openapi.json
```

The API publishes formal FastAPI response models for JSON endpoints and documented binary file responses for Excel export and run report download endpoints. Swagger groups endpoints by product area: Health, Capabilities, Demo, Market Data, Curves, Positions, Exposure, Hedging, Risk, Reports, and Runs.

For local frontend development, the backend allows these origins by default:

```text
http://localhost:3000
http://127.0.0.1:3000
```

Override with:

```text
FLOWDECK_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## GET /health

Purpose: basic service health check.

Inputs: none.

Success response:

```json
{
  "status": "ok",
  "service": "FlowDeck API",
  "version": "0.1.0"
}
```

Error response: not expected for normal operation.

## GET /capabilities

Purpose: disclose supported commodities, units, and available analytics modules.

Inputs: none.

Success response:

```json
{
  "commodities": ["BRENT", "WTI"],
  "currency": "USD",
  "unit": "bbl",
  "modules": ["market_data", "curves", "futures_positions", "physical_cargoes", "net_exposure", "hedging", "stress_pnl", "excel_export"]
}
```

## GET /api/info

Purpose: provide frontend-friendly local API metadata.

Inputs: none.

Success response:

```json
{
  "service": "FlowDeck API",
  "version": "0.1.0",
  "environment": "local",
  "docs_url": "/docs",
  "openapi_url": "/openapi.json",
  "frontend_expected_origin_examples": [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
  ]
}
```

## GET /demo/sample-files

Purpose: describe the backend-owned synthetic CSV files used by demo mode.

Inputs: none.

Success response:

```json
{
  "market_data_file": "data/sample/market_data/valid_brent_wti_futures.csv",
  "futures_positions_file": "data/sample/positions/valid_futures_positions.csv",
  "physical_cargoes_file": "data/sample/positions/valid_physical_cargoes.csv",
  "descriptions": {
    "market_data_file": "Synthetic Brent/WTI futures curve market data.",
    "futures_positions_file": "Synthetic oil futures positions.",
    "physical_cargoes_file": "Synthetic simplified physical cargoes."
  },
  "note": "Synthetic demo files only. No real trade or licensed market data."
}
```

Notes:

- Files are resolved by the backend relative to the project root.
- These are synthetic demo files only.
- The endpoint does not read or return file contents.

## POST /demo/run

Purpose: run the full backend-owned synthetic sample workflow without CSV uploads.

Inputs:

- `target_hedge_ratio`: optional query parameter, default `0.80`, between `0` and `1`.
- `stress_scenario`: optional query parameter, default `PARALLEL_DOWN_5`.

Supported demo stress scenarios:

- `PARALLEL_DOWN_5`
- `PARALLEL_UP_5`
- `BRENT_DOWN_5`
- `BRENT_UP_5`
- `WTI_DOWN_5`

Success response:

```json
{
  "run_id": "FD-RUN-20260515-140000-ABC123",
  "status": "SUCCESS",
  "created_at": "2026-05-15T14:00:00Z",
  "completed_at": "2026-05-15T14:00:03Z",
  "summary": {
    "number_of_curves": 2,
    "number_of_net_exposure_buckets": 4,
    "total_net_exposure_bbl": "406000",
    "total_post_hedge_absolute_exposure_bbl": "81000",
    "total_stress_pnl_usd": "-2030000"
  },
  "report_url": "/runs/FD-RUN-20260515-140000-ABC123/report",
  "run_detail_url": "/runs/FD-RUN-20260515-140000-ABC123",
  "assumptions": [
    "Synthetic demo data only.",
    "Analytics only.",
    "Not trade execution.",
    "No licensed market data.",
    "Hedge recommendations require human review."
  ]
}
```

Example usage:

```bash
curl -X POST "http://127.0.0.1:8000/demo/run?target_hedge_ratio=0.80&stress_scenario=PARALLEL_DOWN_5"
```

Behavior:

- Uses only sample files under `data/sample/`.
- Calls existing FlowDeck services for validation, curves, exposure, hedging, stress P&L, Excel export, and run metadata.
- Creates `runs/<run_id>/run_metadata.json`.
- Creates `runs/<run_id>/flowdeck_report.xlsx`.
- Returns links for `GET /runs/{run_id}` and `GET /runs/{run_id}/report`.
- Does not execute trades and does not persist data to a database.

Error response for invalid demo request:

```json
{
  "detail": {
    "error": "target_hedge_ratio must be between 0 and 1 inclusive.",
    "error_code": "DEMO_RUN_VALIDATION_ERROR",
    "message": "target_hedge_ratio must be between 0 and 1 inclusive.",
    "details": null
  }
}
```

## POST /market-data/validate

Purpose: validate oil futures market data CSV.

Input: multipart form upload field `file`.

Success response:

```json
{
  "valid": true,
  "row_count": 6,
  "errors": [],
  "preview_rows": [
    {
      "valuation_date": "2026-05-08",
      "commodity": "BRENT",
      "contract_code": "BRTM26",
      "contract_month": "2026-06"
    }
  ]
}
```

Error response:

```json
{
  "detail": {
    "valid": false,
    "row_count": 0,
    "error_code": "VALIDATION_ERROR",
    "message": "Validation failed.",
    "errors": [
      {
        "code": "invalid_price",
        "message": "Row 2: price must be positive."
      }
    ],
    "details": {
      "errors": [
        {
          "code": "invalid_price",
          "message": "Row 2: price must be positive."
        }
      ]
    }
  }
}
```

Notes: rejects non-CSV and empty uploads.

## POST /curves/build

Purpose: load validated market data, build forward curves, and return calendar spreads.

Input: multipart form upload field `file`.

Success response:

```json
{
  "curve_summaries": [
    {
      "valuation_date": "2026-05-08",
      "commodity": "BRENT",
      "front_month_contract": "BRTM26",
      "curve_shape": "BACKWARDATION"
    }
  ],
  "calendar_spreads": [
    {
      "valuation_date": "2026-05-08",
      "commodity": "BRENT",
      "spread_name": "M1_M2",
      "spread_usd_per_bbl": "0.36"
    }
  ]
}
```

Error response: same validation shape as `/market-data/validate`.

## POST /positions/futures/analyze

Purpose: validate futures positions and aggregate signed paper exposure.

Input: multipart form upload field `file`.

Success response includes:

```json
{
  "valid": true,
  "row_count": 6,
  "exposure_aggregation": [],
  "summary": {
    "number_of_buckets": 4,
    "total_net_exposure_bbl": 6000
  }
}
```

## POST /positions/physical/analyze

Purpose: validate physical cargoes and aggregate signed physical exposure.

Input: multipart form upload field `file`.

Success response includes:

```json
{
  "valid": true,
  "row_count": 5,
  "physical_exposure_aggregation": [],
  "summary": {
    "number_of_buckets": 2,
    "total_net_physical_exposure_bbl": 400000
  }
}
```

## POST /exposure/net

Purpose: combine aggregated futures and physical exposure into a hedgeable monthly net exposure view.

Inputs:

- `futures_file`: futures positions CSV
- `physical_file`: physical cargoes CSV

Success response includes:

```json
{
  "net_exposure_buckets": [
    {
      "hedge_index": "BRENT",
      "exposure_month": "2026-06",
      "book": "Crude Alpha",
      "net_exposure_bbl": 7000
    }
  ],
  "summary": {
    "number_of_exposure_buckets": 6,
    "total_net_exposure_bbl": 406000
  }
}
```

## POST /hedging/simulate

Purpose: compute deterministic futures-equivalent hedge recommendations from net exposure.

Inputs:

- `futures_file`: futures positions CSV
- `physical_file`: physical cargoes CSV
- `target_hedge_ratio`: optional, default `0.80`
- `contract_size_bbl`: optional, default `1000`

Success response includes:

```json
{
  "net_exposure_result": {},
  "hedge_recommendations": [
    {
      "recommended_direction": "SELL",
      "recommended_lots_rounded": 480
    }
  ],
  "hedge_summary": {
    "number_of_recommendations": 4
  }
}
```

Notes: analytics only. FlowDeck does not execute trades.

## POST /risk/stress

Purpose: run predefined synthetic stress P&L scenarios from net exposure.

Inputs:

- `futures_file`: futures positions CSV
- `physical_file`: physical cargoes CSV
- `scenario_name`: optional, default `PARALLEL_DOWN_5`

Supported first-version scenarios:

- `PARALLEL_DOWN_5`
- `PARALLEL_UP_5`
- `BRENT_DOWN_5`
- `BRENT_UP_5`
- `WTI_DOWN_5`

Success response includes:

```json
{
  "net_exposure_result": {},
  "stress_bucket_results": [
    {
      "hedge_index": "BRENT",
      "stress_pnl_usd": -35000,
      "pnl_direction": "LOSS"
    }
  ],
  "stress_summary": {
    "scenario_name": "PARALLEL_DOWN_5",
    "total_stress_pnl_usd": -2030000
  }
}
```

## POST /reports/excel

Purpose: generate a downloadable Excel workbook from uploaded CSV inputs and analytics outputs.

Inputs:

- `market_data_file`: market data CSV
- `futures_file`: futures positions CSV
- `physical_file`: physical cargoes CSV
- `target_hedge_ratio`: optional, default `0.80`
- `stress_scenario`: optional, default `PARALLEL_DOWN_5`

Success response: `.xlsx` file response with content type:

```text
application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
```

Notes:

- Generated report files are temporary.
- Uploaded files are not persisted.
- Workbook contains charts, assumptions, curves, positions, exposures, hedging, and stress P&L.

## GET /runs

Purpose: list recent local workflow run metadata records from the file-based `runs/` directory.

Inputs:

- `limit`: optional, default `20`, minimum `1`, maximum `100`.
- `status`: optional, one of `SUCCESS`, `FAILED`, `RUNNING`.
- `run_type`: optional, currently `DEMO_WORKFLOW`.

Filtering is applied before `limit`. Default behavior is unchanged when no filters are supplied.

Success response:

```json
{
  "runs": [
    {
      "run_id": "FD-RUN-20260512-235500-ABC123",
      "run_type": "DEMO_WORKFLOW",
      "status": "SUCCESS",
      "created_at": "2026-05-12T23:55:00Z",
      "completed_at": "2026-05-12T23:55:04Z",
      "summary": {
        "number_of_curves": 2,
        "number_of_net_exposure_buckets": 6,
        "total_net_exposure_bbl": "406000",
        "total_post_hedge_absolute_exposure_bbl": "83000",
        "total_stress_pnl_usd": "-2030000"
      },
      "output_files": {
        "excel_report_path": "runs/FD-RUN-20260512-235500-ABC123/flowdeck_report.xlsx"
      }
    }
  ],
  "count": 1
}
```

Notes:

- Invalid `run_metadata.json` files are ignored.
- If no valid local runs exist, the endpoint returns `{"runs": [], "count": 0}`.
- This is local file-based metadata, not database persistence.
- Invalid `status` or `run_type` values return HTTP 400 using the common error schema.

## GET /runs/{run_id}

Purpose: return full metadata for one local workflow run.

Input: path parameter `run_id`, for example `FD-RUN-20260512-235500-ABC123`.

Success response: one run metadata record.

Error response for missing run:

```json
{
  "detail": {
    "error": "Run metadata not found.",
    "error_code": "RUN_NOT_FOUND",
    "message": "Run metadata not found.",
    "details": null
  }
}
```

Notes:

- `run_id` is validated before file lookup to prevent path traversal.
- No delete or update endpoints exist yet.
- The endpoint only reads `runs/<run_id>/run_metadata.json`.

## GET /runs/{run_id}/report

Purpose: download the Excel report associated with one local workflow run.

Input: path parameter `run_id`, for example `FD-RUN-20260512-235500-ABC123`.

Success response: `.xlsx` file response with content type:

```text
application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
```

Suggested browser/download filename:

```text
flowdeck_report_<run_id>.xlsx
```

Example usage:

```bash
curl -o reports/downloaded_flowdeck_report.xlsx ^
  http://127.0.0.1:8000/runs/FD-RUN-20260512-235500-ABC123/report
```

Behavior:

- `run_id` is validated before file lookup to prevent path traversal.
- The endpoint reads `runs/<run_id>/run_metadata.json`.
- Metadata must include `output_files.excel_report_path`.
- The resolved report path must remain inside `runs/<run_id>/`.
- Missing metadata returns `RUN_NOT_FOUND`.
- Missing report files return `RUN_REPORT_NOT_FOUND`.
- Report paths outside the expected run folder return `INVALID_RUN_REPORT_PATH`.

## Common Error Shapes

Preferred error fields:

- `error_code`
- `message`
- `details`

Some validation responses also preserve legacy convenience keys such as `valid`, `row_count`, `errors`, or `error` for compatibility with earlier local clients.

Invalid upload:

```json
{
  "detail": {
    "error": "Only .csv uploads are supported.",
    "error_code": "INVALID_FILE_TYPE",
    "message": "Only .csv uploads are supported.",
    "details": {
      "filename": "bad.txt"
    }
  }
}
```

Unexpected internal error:

```json
{
  "detail": {
    "error": "Internal server error.",
    "error_code": "INTERNAL_ERROR",
    "message": "Internal server error.",
    "details": null
  }
}
```
