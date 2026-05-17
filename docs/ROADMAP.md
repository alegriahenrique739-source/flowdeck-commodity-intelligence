# FlowDeck Roadmap

## Increment 0: Repository Foundation

Status: current.

Deliverables:

- repository structure
- architecture notes
- data contracts
- formula documentation
- empty package and test placeholders

## Increment 1: Market Data Validation

Deliverables:

- Pydantic schemas for market data
- fake Brent and WTI sample curves
- CSV loader
- validation service
- pytest coverage for required fields, unsupported commodities, duplicate maturities, invalid prices, and malformed maturities

## Increment 2: Forward Curves and Calendar Spreads

Deliverables:

- curve construction module
- spread calculation module
- documented formulas
- unit tests for normal, contango, backwardation, missing maturity, and mixed commodity cases

## Increment 3: Futures and Physical Exposures

Deliverables:

- futures position schema and loader
- physical exposure schema and loader
- exposure aggregation module
- net exposure calculation
- test fixtures and calculation tests

## Increment 4: Hedge Simulation

Deliverables:

- hedge request schema
- hedge calculation module
- configurable hedge ratio
- contract-size conversion
- rounding policy
- tests for long/short physical exposure and partial hedges

## Increment 5: Stress P&L

Deliverables:

- scenario schema and loader
- stress P&L module
- scenario result tables
- tests for commodity-specific, maturity-specific, and parallel shocks

## Increment 6: Excel Reports

Deliverables:

- report workbook generator
- summary sheets for validation, curves, spreads, exposure, hedges, and stress P&L
- report smoke tests

## Increment 7: FastAPI Workflow

Deliverables:

- local FastAPI app
- endpoints for upload, validate, calculate, and export
- Docker development environment

## Later: Web Dashboard

Deliverables:

- Next.js application
- React/TypeScript/Tailwind UI
- dashboard views for curves, spreads, exposure, and stress P&L
- PostgreSQL-backed persistence
