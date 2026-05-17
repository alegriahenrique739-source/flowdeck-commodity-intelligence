# FlowDeck Financial Formulas

This document is the source of truth for every financial calculation implemented in FlowDeck.

No financial formula should be added to code without adding or updating a matching section here and adding pytest coverage.

## Conventions

### Commodities

V1 supports:

- Brent
- WTI

### Maturity

Maturity should be represented as a monthly contract bucket in `YYYY-MM` format unless a later module requires exact exchange contract codes.

### Quantity

Paper futures quantities should use lots or barrels consistently within a calculation. Physical exposures should use barrels. If lots are used, a contract-size conversion must be explicit.

### Sign Convention

Long exposure is positive.

Short exposure is negative.

Examples:

- Long futures: positive quantity
- Short futures: negative quantity
- BUY physical cargo: positive physical exposure
- SELL physical cargo: negative physical exposure

The simplified physical sign convention is commercial direction based. More advanced inventory ownership and pricing-status conventions can be added in later increments.

## Forward Curve

Status: implemented for validated oil futures market data.

Expected inputs:

- valuation_date
- commodity
- contract_month
- contract_code
- expiry_date
- price
- currency
- unit

Expected output:

- one ordered curve per `valuation_date + commodity`
- front month contract and price
- back month contract and price
- front-to-back spread
- curve shape
- supported calendar spreads

Formula:

```text
curve[valuation_date, commodity] =
    validated market prices for that valuation date and commodity,
    ordered by contract_month, then expiry_date
```

Front-to-back spread:

```text
front_to_back_spread = front_month_price - back_month_price
```

Curve shape classification uses a tolerance of `0.0001` USD/bbl for equality.

```text
BACKWARDATION = prices are monotonic non-increasing and front price > back price
CONTANGO = prices are monotonic non-decreasing and front price < back price
FLAT = all adjacent price differences are within tolerance
MIXED = the ordered curve has both upward and downward moves beyond tolerance
```

Validation requirements:

- commodity is supported
- maturity is parseable and monthly
- price is positive
- duplicate `valuation_date + commodity + contract_month` rows are rejected by market data validation
- missing maturities are not inferred; unavailable spreads are omitted

## Calendar Spread

Status: implemented for standard month offsets where both contracts exist.

Calendar spread is the price difference between two maturities on the same commodity curve.

Formula:

```text
spread = price_near_maturity - price_far_maturity
```

Example:

```text
Brent Jun/Jul spread = Brent Jun price - Brent Jul price
```

Positive spread indicates backwardation between the selected maturities. Negative spread indicates contango.

Implemented spread labels:

| Label | Formula |
| --- | --- |
| M1_M2 | M1 price - M2 price |
| M2_M3 | M2 price - M3 price |
| M3_M6 | M3 price - M6 price |
| M6_M12 | M6 price - M12 price |

If the far maturity is unavailable, the spread is omitted instead of inferred.

## Futures Exposure

Status: implemented for validated futures position rows.

Paper futures exposure aggregates signed futures quantities by commodity, contract month, and book.

Formula:

```text
direction_sign = 1 for BUY
direction_sign = -1 for SELL

signed_exposure_bbl = lots * contract_size * direction_sign
```

Aggregation key:

```text
futures_exposure_key = commodity + contract_month + book
```

Bucket metrics:

```text
long_exposure_bbl = sum(signed_exposure_bbl where signed_exposure_bbl > 0)
short_exposure_bbl = sum(signed_exposure_bbl where signed_exposure_bbl < 0)
net_exposure_bbl = sum(signed_exposure_bbl)
gross_exposure_bbl = long_exposure_bbl + abs(short_exposure_bbl)
```

Short exposure is retained as a negative signed value. Gross exposure is always non-negative.

## Physical Exposure

Status: implemented for validated physical cargo rows.

Physical cargo exposure aggregates signed physical volume by commodity, pricing index, pricing month, and book.

Expected fields:

- cargo_id
- book
- commodity
- buy_sell
- pricing_month
- pricing_index
- volume_bbl

Formula:

```text
physical_direction_sign = 1 for BUY
physical_direction_sign = -1 for SELL

signed_physical_exposure_bbl = volume_bbl * physical_direction_sign
```

Aggregation key:

```text
physical_exposure_key = commodity + pricing_index + pricing_month + book
```

Bucket metrics:

```text
long_physical_exposure_bbl =
    sum(signed_physical_exposure_bbl where signed_physical_exposure_bbl > 0)

short_physical_exposure_bbl =
    sum(signed_physical_exposure_bbl where signed_physical_exposure_bbl < 0)

net_physical_exposure_bbl = sum(signed_physical_exposure_bbl)

gross_physical_exposure_bbl =
    long_physical_exposure_bbl + abs(short_physical_exposure_bbl)
```

Short physical exposure is retained as a negative signed value. Gross physical exposure is always non-negative.

## Net Exposure

Status: implemented for aggregated physical and futures exposure buckets.

Net exposure combines futures and physical exposure into a shared hedgeable monthly view.

Common exposure key:

```text
net_exposure_key = hedge_index + exposure_month + book
```

Mapping rules:

```text
futures hedge_index = futures commodity
futures exposure_month = futures contract_month
futures book = futures book

physical hedge_index = physical pricing_index
physical exposure_month = physical pricing_month
physical book = physical book
```

This means a physical cargo with `commodity = BRENT` and `pricing_index = WTI` contributes to WTI hedgeable exposure.

Bucket formula:

```text
net_exposure_bbl = physical_exposure_bbl + paper_exposure_bbl
absolute_net_exposure_bbl = abs(net_exposure_bbl)
gross_component_exposure_bbl =
    abs(physical_exposure_bbl) + abs(paper_exposure_bbl)
long_exposure_bbl = net_exposure_bbl if net_exposure_bbl > 0 else 0
short_exposure_bbl = net_exposure_bbl if net_exposure_bbl < 0 else 0
```

Example:

```text
physical_exposure_bbl = 600000
paper_exposure_bbl = -500000
net_exposure_bbl = 100000
absolute_net_exposure_bbl = 100000
gross_component_exposure_bbl = 1100000
```

Portfolio summary:

```text
total_physical_exposure_bbl = sum(physical_exposure_bbl)
total_paper_exposure_bbl = sum(paper_exposure_bbl)
total_net_exposure_bbl = sum(net_exposure_bbl)
total_absolute_net_exposure_bbl = sum(absolute_net_exposure_bbl)
total_gross_component_exposure_bbl = sum(gross_component_exposure_bbl)
total_long_exposure_bbl = sum(long_exposure_bbl)
total_short_exposure_bbl = sum(short_exposure_bbl)
```

Positive net exposure means long price exposure. Negative net exposure means short price exposure. Zero means fully offset at the `hedge_index + exposure_month + book` level.

Compatibility note: old `gross_exposure_bbl` names are aliases for absolute net exposure, not gross component exposure. New formulas and tests should use `absolute_net_exposure_bbl` or `gross_component_exposure_bbl` explicitly.

## Hedge Simulation

Status: implemented for deterministic futures-equivalent hedge recommendations.

The hedge simulator proposes futures-equivalent trades from net exposure buckets. This is analytics only. FlowDeck does not execute trades, and all recommendations require human review.

Sign convention:

```text
positive net_exposure_bbl = long price exposure
negative net_exposure_bbl = short price exposure

required_hedge_exposure_bbl < 0 => recommend SELL futures
required_hedge_exposure_bbl > 0 => recommend BUY futures
required_hedge_exposure_bbl = 0 => NO_ACTION
```

Target hedge ratio mode:

```text
0 <= hedge_ratio <= 1

target_residual_exposure_bbl =
    net_exposure_bbl * (1 - target_hedge_ratio)

required_hedge_exposure_bbl =
    target_residual_exposure_bbl - net_exposure_bbl
```

Target residual exposure mode:

```text
required_hedge_exposure_bbl =
    target_residual_exposure_bbl - net_exposure_bbl
```

Lot sizing:

```text
recommended_lots_exact =
    abs(required_hedge_exposure_bbl) / contract_size_bbl

recommended_lots_rounded =
    round recommended_lots_exact using NEAREST, FLOOR, or CEIL

rounded_hedge_exposure_bbl =
    recommended_lots_rounded * contract_size_bbl * trade_sign

trade_sign = 1 for BUY
trade_sign = -1 for SELL
trade_sign = 0 for NO_ACTION

post_hedge_net_exposure_bbl =
    net_exposure_bbl + rounded_hedge_exposure_bbl

residual_difference_vs_target_bbl =
    post_hedge_net_exposure_bbl - target_residual_exposure_bbl
```

Portfolio summary:

```text
total_current_absolute_net_exposure_bbl =
    sum(abs(current_net_exposure_bbl))

total_post_hedge_absolute_net_exposure_bbl =
    sum(abs(post_hedge_net_exposure_bbl))

total_required_hedge_abs_bbl =
    sum(abs(required_hedge_exposure_bbl))

total_recommended_lots_abs =
    sum(recommended_lots_rounded)
```

## Stress P&L

Status: implemented for synthetic commodity price shocks.

Stress P&L estimates mark-to-market impact from synthetic price shocks. This is analytics only, not financial advice, trade execution, or a risk model such as VaR.

Bucket formula:

```text
stress_pnl_usd = net_exposure_bbl * price_delta_usd_per_bbl
```

Sign convention:

```text
positive net_exposure_bbl gains when price_delta_usd_per_bbl is positive
positive net_exposure_bbl loses when price_delta_usd_per_bbl is negative

negative net_exposure_bbl gains when price_delta_usd_per_bbl is negative
negative net_exposure_bbl loses when price_delta_usd_per_bbl is positive
```

Scenario delta definitions:

```text
INDEX_ABSOLUTE_SHOCK:
    price_delta_usd_per_bbl = explicit delta for hedge_index

INDEX_PERCENTAGE_SHOCK:
    price_delta_usd_per_bbl =
        current_price_usd_per_bbl * index_percentage_shock

PARALLEL_SHIFT:
    price_delta_usd_per_bbl = parallel_shift_usd_per_bbl

FRONT_END_SHOCK:
    price_delta_usd_per_bbl = front_end_shift_usd_per_bbl
    only for the earliest N exposure months per hedge_index

BASIS_SHOCK:
    price_delta_usd_per_bbl = explicit delta for hedge_index
```

Basis shocks are explicit index deltas, not inferred spread semantics. Example:

```text
BRENT_WTI_BASIS_WIDENS_2_WTI_FIXED:
    BRENT price_delta_usd_per_bbl = 2
    WTI price_delta_usd_per_bbl = 0
```

Portfolio summary:

```text
total_stress_pnl_usd = sum(stress_pnl_usd)
total_gain_usd = sum(stress_pnl_usd where stress_pnl_usd > 0)
total_loss_usd = sum(stress_pnl_usd where stress_pnl_usd < 0)
worst_bucket = bucket with lowest stress_pnl_usd
best_bucket = bucket with highest stress_pnl_usd
```

Currency and unit must match between exposure and shock: USD and bbl.

## Excel Report Outputs

Status: planned.

Trader-ready Excel exports should include:

- input validation summary
- forward curves
- calendar spreads
- futures positions
- physical exposures
- net exposure table
- hedge simulation
- stress P&L scenarios

Reports should be reproducible from the same input files.
