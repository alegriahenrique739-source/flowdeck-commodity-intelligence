# Stabilization Checklist

Run this checklist before major increments or before changing financial behavior.

## Pre-Change Checks

- [ ] Back up the project folder.
- [ ] Run `python -m pytest`.
- [ ] Confirm the current test count and full result.
- [ ] Review the requested scope and avoid unrelated refactors.
- [ ] Confirm no real trade data, licensed market data, API keys, or secrets are being added.

## Demo And Report Checks

- [ ] Run `python scripts/run_demo_workflow.py`.
- [ ] Confirm `runs/<run_id>/run_metadata.json` is created.
- [ ] Confirm `runs/<run_id>/flowdeck_report.xlsx` is created.
- [ ] Run `python scripts/build_sample_excel_report.py`.
- [ ] Confirm generated workbook paths under `reports/`.
- [ ] Review the Excel report manually after export, chart, or formatting changes.

## API Checks

- [ ] Run `python -m uvicorn backend.app.main:app --reload`.
- [ ] Open `http://127.0.0.1:8000/health`.
- [ ] Open `http://127.0.0.1:8000/docs`.
- [ ] Confirm existing endpoint paths are unchanged unless explicitly requested.
- [ ] Confirm API route handlers remain thin and call service modules.

## Financial Logic Checks

- [ ] Avoid changing formulas without tests.
- [ ] Confirm sign conventions remain consistent.
- [ ] Confirm hedge recommendations use `net_exposure_bbl`.
- [ ] Confirm stress P&L uses `net_exposure_bbl * price_delta_usd_per_bbl`.
- [ ] Confirm gross component exposure and absolute net exposure remain distinct.

## Finish Criteria

- [ ] Files created are listed.
- [ ] Files modified are listed.
- [ ] Tests run are listed.
- [ ] Full test result is reported.
- [ ] Limitations are noted.
- [ ] Next recommended increment is stated.
