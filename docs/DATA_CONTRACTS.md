# FlowDeck Data Contracts

This document defines input and output contracts for fake local CSV and Excel files.

## General Rules

- CSV and Excel imports should use the same column names.
- Column names should be snake_case.
- Dates should use ISO format: `YYYY-MM-DD`.
- Monthly maturities should use `YYYY-MM`.
- Commodities are limited to `BRENT` and `WTI`.
- Prices are in USD per barrel unless explicitly documented otherwise.
- Volumes are in barrels unless explicitly documented otherwise.

## Market Data

Status: implemented for oil futures CSV imports.

Sample directory:

```text
data/sample/market_data/
```

Columns:

| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| valuation_date | date | yes | Date the curve snapshot applies to, ISO `YYYY-MM-DD` |
| commodity | string | yes | `BRENT` or `WTI`; normalized to uppercase |
| contract_code | string | yes | Synthetic futures contract identifier |
| contract_month | string | yes | Monthly bucket, normalized to `YYYY-MM` |
| expiry_date | date | yes | Contract expiry date, ISO `YYYY-MM-DD` |
| price | decimal | yes | USD/bbl, must be positive |
| currency | string | yes | Must be `USD`; normalized to uppercase |
| unit | string | yes | Must be `bbl`; normalized to lowercase |
| source | string | yes | Synthetic source label, no vendor data |

Validation rules:

- All required columns must be present.
- `valuation_date` and `expiry_date` must parse as valid ISO dates.
- `contract_month` must represent a valid calendar month and is normalized to `YYYY-MM`.
- `price` must be positive.
- `commodity` must be `BRENT` or `WTI`.
- `currency` must be `USD`.
- `unit` must be `bbl`.
- Duplicate rows are rejected for `valuation_date + commodity + contract_month`.

## Forward Curve Output

Status: implemented for in-memory analytics output.

One forward curve is built per `valuation_date + commodity` from validated market data rows.

| Field | Type | Notes |
| --- | --- | --- |
| valuation_date | date | Curve snapshot date |
| commodity | string | `BRENT` or `WTI` |
| ordered_contracts | list | Contracts sorted by `contract_month`, then `expiry_date` |
| front_month_contract | string | Contract code for M1 |
| front_month_price | decimal | M1 price |
| back_month_contract | string | Last available contract in the curve |
| back_month_price | decimal | Last available contract price |
| front_to_back_spread | decimal | `front_month_price - back_month_price` |
| curve_shape | string | `BACKWARDATION`, `CONTANGO`, `FLAT`, or `MIXED` |
| calendar_spreads | object | Available spread analytics keyed by label |

Supported calendar spread labels:

| Label | Near/Far |
| --- | --- |
| M1_M2 | M1 price - M2 price |
| M2_M3 | M2 price - M3 price |
| M3_M6 | M3 price - M6 price |
| M6_M12 | M6 price - M12 price |

Missing maturities are allowed. A spread is only returned when both contracts exist.

## Futures Positions

Status: implemented for oil futures CSV imports.

Sample directory:

```text
data/sample/positions/
```

Columns:

| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| position_id | string | yes | Stable row identifier, must be unique |
| trade_date | date | yes | Trade date, ISO `YYYY-MM-DD` |
| book | string | yes | Synthetic trading book |
| commodity | string | yes | `BRENT` or `WTI`; normalized to uppercase |
| contract_code | string | yes | Synthetic futures contract identifier |
| contract_month | string | yes | Monthly bucket, normalized to `YYYY-MM` |
| direction | string | yes | `BUY` or `SELL`; normalized to uppercase |
| lots | decimal | yes | Strictly positive futures lot count |
| contract_size | decimal | yes | Strictly positive barrels per lot |
| entry_price | decimal | yes | Strictly positive USD/bbl entry price |
| currency | string | yes | Must be `USD`; normalized to uppercase |
| unit | string | yes | Must be `bbl`; normalized to lowercase |
| counterparty | string | yes | Synthetic counterparty name |

Validation rules:

- All required columns must be present.
- `position_id`, `book`, `contract_code`, and `counterparty` must not be blank.
- `trade_date` must parse as a valid ISO date.
- `commodity` must be `BRENT` or `WTI`.
- `direction` must be `BUY` or `SELL`.
- `lots`, `contract_size`, and `entry_price` must be strictly positive.
- `currency` must be `USD`.
- `unit` must be `bbl`.
- `contract_month` must represent a valid calendar month and is normalized to `YYYY-MM`.
- Duplicate `position_id` values are rejected.

## Futures Exposure Output

Status: implemented for in-memory aggregation output.

Exposure is aggregated by `commodity + contract_month + book`.

| Field | Type | Notes |
| --- | --- | --- |
| commodity | string | `BRENT` or `WTI` |
| contract_month | string | Monthly bucket, `YYYY-MM` |
| book | string | Synthetic trading book |
| gross_exposure_bbl | decimal | Sum of absolute signed exposure |
| net_exposure_bbl | decimal | Sum of signed exposure |
| long_exposure_bbl | decimal | Sum of positive signed exposure |
| short_exposure_bbl | decimal | Sum of negative signed exposure |

## Physical Cargo Exposures

Status: implemented for simplified physical cargo CSV imports.

Sample directory:

```text
data/sample/positions/
```

Columns:

| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| cargo_id | string | yes | Stable row identifier, must be unique |
| trade_date | date | yes | Trade date, ISO `YYYY-MM-DD` |
| book | string | yes | Synthetic physical book |
| commodity | string | yes | Physical commodity, `BRENT` or `WTI`; normalized to uppercase |
| buy_sell | string | yes | `BUY` or `SELL`; normalized to uppercase |
| volume_bbl | decimal | yes | Strictly positive physical volume |
| pricing_index | string | yes | Pricing index, `BRENT` or `WTI`; normalized to uppercase |
| pricing_month | string | yes | Monthly pricing bucket, normalized to `YYYY-MM` |
| fixed_price | decimal | yes | Optional; blank allowed, positive when provided |
| differential | decimal | yes | Optional; blank allowed, may be positive, zero, or negative |
| delivery_start | date | yes | Delivery window start, ISO `YYYY-MM-DD` |
| delivery_end | date | yes | Delivery window end, ISO `YYYY-MM-DD` |
| location | string | yes | Synthetic delivery location |
| freight_cost_per_bbl | decimal | yes | Optional; blank allowed, zero or positive when provided |
| storage_cost_per_bbl | decimal | yes | Optional; blank allowed, zero or positive when provided |
| currency | string | yes | Must be `USD`; normalized to uppercase |
| unit | string | yes | Must be `bbl`; normalized to lowercase |
| counterparty | string | yes | Synthetic counterparty name |

Validation rules:

- All required columns must be present.
- `cargo_id`, `book`, `location`, and `counterparty` must not be blank.
- `trade_date`, `delivery_start`, and `delivery_end` must parse as valid ISO dates.
- `delivery_end` must be on or after `delivery_start`.
- `commodity` must be `BRENT` or `WTI`.
- `buy_sell` must be `BUY` or `SELL`.
- `volume_bbl` must be strictly positive.
- `pricing_index` must be `BRENT` or `WTI`.
- `pricing_month` must represent a valid calendar month and is normalized to `YYYY-MM`.
- `fixed_price` may be blank, but must be positive when provided.
- `differential` may be blank, positive, zero, or negative.
- `freight_cost_per_bbl` and `storage_cost_per_bbl` may be blank, but must be zero or positive when provided.
- `currency` must be `USD`.
- `unit` must be `bbl`.
- Duplicate `cargo_id` values are rejected.

## Physical Exposure Output

Status: implemented for in-memory aggregation output.

Exposure is aggregated by `commodity + pricing_index + pricing_month + book`.

| Field | Type | Notes |
| --- | --- | --- |
| commodity | string | Physical commodity, `BRENT` or `WTI` |
| pricing_index | string | Pricing index, `BRENT` or `WTI` |
| pricing_month | string | Monthly bucket, `YYYY-MM` |
| book | string | Synthetic physical book |
| gross_physical_exposure_bbl | decimal | Sum of absolute signed physical exposure |
| net_physical_exposure_bbl | decimal | Sum of signed physical exposure |
| long_physical_exposure_bbl | decimal | Sum of positive signed physical exposure |
| short_physical_exposure_bbl | decimal | Sum of negative signed physical exposure |

## Net Exposure Output

Status: implemented for in-memory aggregation output.

Net exposure combines aggregated physical exposure and aggregated futures exposure into one hedgeable monthly view.

Common exposure key:

```text
hedge_index + exposure_month + book
```

Mapping rules:

| Source | hedge_index | exposure_month | book |
| --- | --- | --- | --- |
| Futures exposure | `commodity` | `contract_month` | `book` |
| Physical exposure | `pricing_index` | `pricing_month` | `book` |

Bucket fields:

| Field | Type | Notes |
| --- | --- | --- |
| hedge_index | string | Hedgeable index, `BRENT` or `WTI` |
| exposure_month | string | Monthly bucket, `YYYY-MM` |
| book | string | Trading or physical book |
| label | string | Human-readable label, for example `BRENT 2026-09 / CRUDE_BOOK` |
| physical_exposure_bbl | decimal | Signed physical exposure mapped by pricing index/month |
| paper_exposure_bbl | decimal | Signed futures exposure mapped by commodity/contract month |
| net_exposure_bbl | decimal | `physical_exposure_bbl + paper_exposure_bbl` |
| absolute_net_exposure_bbl | decimal | `abs(net_exposure_bbl)` |
| gross_component_exposure_bbl | decimal | `abs(physical_exposure_bbl) + abs(paper_exposure_bbl)` |
| long_exposure_bbl | decimal | Positive net exposure, otherwise zero |
| short_exposure_bbl | decimal | Negative net exposure, otherwise zero |

Compatibility note: `gross_exposure_bbl` may still appear as an alias for `absolute_net_exposure_bbl`. New code should use the explicit preferred fields above.

Portfolio summary fields:

| Field | Type | Notes |
| --- | --- | --- |
| total_physical_exposure_bbl | decimal | Sum of bucket physical exposure |
| total_paper_exposure_bbl | decimal | Sum of bucket paper exposure |
| total_net_exposure_bbl | decimal | Sum of bucket net exposure |
| total_absolute_net_exposure_bbl | decimal | Sum of bucket absolute net exposure |
| total_gross_component_exposure_bbl | decimal | Sum of bucket gross component exposure |
| total_long_exposure_bbl | decimal | Sum of bucket long exposure |
| total_short_exposure_bbl | decimal | Sum of bucket short exposure |
| number_of_exposure_buckets | integer | Count of net exposure buckets |
| largest_long_bucket | object or null | Bucket label and net exposure for the largest positive net exposure |
| largest_short_bucket | object or null | Bucket label and net exposure for the most negative net exposure |

Compatibility note: `total_gross_exposure_bbl` may still appear as an alias for `total_absolute_net_exposure_bbl`.

## Hedge Simulation

Status: implemented for in-memory analytics output.

FlowDeck hedge simulation is analytics only. It does not execute trades, and recommendations require human review.

Request fields:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| exposure_buckets | list | yes | Net exposure buckets from the net exposure engine |
| hedge_mode | string | yes | `TARGET_HEDGE_RATIO` or `TARGET_RESIDUAL_EXPOSURE` |
| target_hedge_ratio | decimal | conditional | Required for `TARGET_HEDGE_RATIO`; must be between 0 and 1 inclusive |
| target_residual_exposure_bbl | decimal | conditional | Required for `TARGET_RESIDUAL_EXPOSURE` |
| contract_size_bbl | decimal | no | Defaults to `1000`; must be strictly positive |
| rounding_method | string | no | `NEAREST`, `FLOOR`, or `CEIL`; defaults to `NEAREST` |

Recommendation fields:

| Field | Type | Notes |
| --- | --- | --- |
| hedge_index | string | Hedgeable index, `BRENT` or `WTI` |
| exposure_month | string | Monthly bucket, `YYYY-MM` |
| book | string | Trading or physical book |
| current_net_exposure_bbl | decimal | Starting signed net exposure |
| target_residual_exposure_bbl | decimal | Desired signed residual exposure |
| required_hedge_exposure_bbl | decimal | Signed hedge exposure before lot rounding |
| contract_size_bbl | decimal | Barrels per futures-equivalent lot |
| recommended_direction | string | `BUY`, `SELL`, or `NO_ACTION` |
| recommended_lots_exact | decimal | Absolute exact lot count |
| recommended_lots_rounded | integer | Absolute rounded lot count |
| rounded_hedge_exposure_bbl | decimal | Signed hedge exposure after lot rounding |
| post_hedge_net_exposure_bbl | decimal | Net exposure after rounded hedge |
| residual_difference_vs_target_bbl | decimal | `post_hedge_net_exposure_bbl - target_residual_exposure_bbl` |
| recommendation_label | string | Human-readable recommendation |

Portfolio summary fields:

| Field | Type | Notes |
| --- | --- | --- |
| total_current_absolute_net_exposure_bbl | decimal | Sum of absolute current net exposure |
| total_post_hedge_absolute_net_exposure_bbl | decimal | Sum of absolute post-hedge net exposure |
| total_required_hedge_abs_bbl | decimal | Sum of absolute required hedge exposure before rounding |
| total_recommended_lots_abs | integer | Sum of absolute rounded recommended lots |
| number_of_recommendations | integer | Count of buckets with `BUY` or `SELL` recommendation |
| number_of_no_action_buckets | integer | Count of buckets with `NO_ACTION` |
| largest_required_hedge_bucket | object or null | Label and absolute required hedge exposure for the largest hedge bucket |

## Stress P&L Scenarios

Status: implemented for in-memory synthetic scenario analytics.

FlowDeck stress P&L is analytics only. It is not financial advice, trade execution, VaR, or a full risk model.

Request fields:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| exposure_buckets | list | yes | Net exposure buckets from the net exposure engine |
| scenario_name | string | yes | Scenario label |
| scenario_type | string | yes | `INDEX_ABSOLUTE_SHOCK`, `INDEX_PERCENTAGE_SHOCK`, `PARALLEL_SHIFT`, `FRONT_END_SHOCK`, or `BASIS_SHOCK` |
| index_price_deltas_usd_per_bbl | object | conditional | Required for `INDEX_ABSOLUTE_SHOCK` and `BASIS_SHOCK`; explicit USD/bbl deltas keyed by `BRENT` or `WTI` |
| index_percentage_shocks | object | conditional | Required for `INDEX_PERCENTAGE_SHOCK`; decimal percentage shocks keyed by index, for example `-0.05` |
| current_prices_usd_per_bbl | object | conditional | Required for `INDEX_PERCENTAGE_SHOCK`; current USD/bbl prices keyed by index |
| parallel_shift_usd_per_bbl | decimal | conditional | Required for `PARALLEL_SHIFT` |
| front_end_month_count | integer | no | Defaults to `3`; earliest N exposure months per hedge index |
| front_end_shift_usd_per_bbl | decimal | conditional | Required for `FRONT_END_SHOCK` |

Bucket result fields:

| Field | Type | Notes |
| --- | --- | --- |
| hedge_index | string | `BRENT` or `WTI` |
| exposure_month | string | Monthly bucket, `YYYY-MM` |
| book | string | Trading or physical book |
| net_exposure_bbl | decimal | Signed net exposure used for stress P&L |
| price_delta_usd_per_bbl | decimal | Scenario price delta |
| stress_pnl_usd | decimal | `net_exposure_bbl * price_delta_usd_per_bbl` |
| pnl_direction | string | `GAIN`, `LOSS`, or `FLAT` |
| scenario_name | string | Scenario label |
| label | string | Human-readable bucket label |

Portfolio summary fields:

| Field | Type | Notes |
| --- | --- | --- |
| scenario_name | string | Scenario label |
| scenario_type | string | Scenario type |
| total_stress_pnl_usd | decimal | Sum of bucket stress P&L |
| total_gain_usd | decimal | Sum of positive bucket stress P&L |
| total_loss_usd | decimal | Sum of negative bucket stress P&L |
| worst_bucket | object or null | Bucket with lowest stress P&L |
| best_bucket | object or null | Bucket with highest stress P&L |
| number_of_buckets | integer | Count of stressed buckets |
| number_of_gain_buckets | integer | Count of `GAIN` buckets |
| number_of_loss_buckets | integer | Count of `LOSS` buckets |
| number_of_flat_buckets | integer | Count of `FLAT` buckets |

Predefined scenario helper names:

- `BRENT_DOWN_5`
- `BRENT_UP_5`
- `WTI_DOWN_5`
- `PARALLEL_DOWN_5`
- `PARALLEL_UP_5`
- `BRENT_WTI_BASIS_WIDENS_2_WTI_FIXED`
- `FRONT_END_DOWN_5`

## Excel Report Export

Status: implemented for local `.xlsx` workbook generation.

The Excel report service accepts optional analytics sections and writes a workbook to a local output path. Missing optional sections create an empty sheet with a clear note instead of failing.

Input sections:

| Section | Required | Notes |
| --- | --- | --- |
| market_data_rows | no | Validated market data rows |
| curve_summaries | no | Forward curve summaries |
| calendar_spreads | no | Calendar spreads; can be derived from curve summaries when omitted |
| futures_positions | no | Validated futures position rows |
| physical_cargoes | no | Validated physical cargo rows |
| net_exposure_result | no | Net exposure engine output |
| hedge_simulation_result | no | Hedge simulator output |
| stress_result | no | Stress P&L output |
| assumptions | no | Optional override notes for the assumptions sheet |

Workbook sheets:

| Sheet | Purpose |
| --- | --- |
| Executive Summary | Report title, timestamp, scope note, and key metrics |
| Market Curves | Validated market futures curve rows |
| Calendar Spreads | Available M1/M2, M2/M3, M3/M6, and M6/M12 spreads |
| Futures Positions | Futures position details with signed exposure |
| Physical Cargoes | Physical cargo details with signed physical exposure |
| Net Exposure | Common hedgeable exposure view |
| Hedge Simulation | Futures-equivalent hedge recommendations |
| Stress P&L | Bucket-level synthetic stress results |
| Assumptions | Scope, data, sign convention, and human-review notes |

Formatting conventions:

- Top row frozen on data sheets.
- Autofilters on populated data sheets.
- Bold headers.
- Readable column widths.
- Barrels formatted as `#,##0`.
- USD/bbl values formatted as `$#,##0.00`.
- Stress P&L formatted as `$#,##0;[Red]-$#,##0`.
- Positive stress P&L highlighted green and negative stress P&L highlighted red.
- Styling is intentionally restrained and institutional.

## Validation Output

Validation should produce structured messages with:

| Field | Notes |
| --- | --- |
| dataset | Source dataset name |
| severity | `error`, `warning`, or `info` |
| row_number | Source row number when applicable |
| column | Source column when applicable |
| code | Stable machine-readable code |
| message | Human-readable explanation |
