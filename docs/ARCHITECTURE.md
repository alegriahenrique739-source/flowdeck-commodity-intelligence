# FlowDeck Architecture

## Design Goals

FlowDeck should behave like a serious early-stage B2B analytics product:

- Correct financial calculations before UI polish
- Clear separation between pure calculations, data loading, validation, and reporting
- Deterministic fake data suitable for demos and tests
- Excel-native workflows for traders
- No dependency on real market data vendors, API keys, or secrets

## System Shape

V1 is a local backend prototype with future web and database expansion in mind.

```text
CSV/XLSX inputs
    ↓
Data loaders
    ↓
Pydantic schema validation
    ↓
Domain calculations
    ↓
Scenario and hedge services
    ↓
Excel report export
```

## Backend Layers

### API Layer

Location: `backend/app/api/`

FastAPI routers will eventually expose workflows such as:

- upload market data
- validate input files
- build curves
- calculate exposures
- run hedge simulations
- export Excel reports

The API layer should not contain financial formulas.

### Schema Layer

Location: `backend/app/schemas/`

Pydantic models should define external and internal data contracts:

- market data rows
- futures position rows
- physical cargo exposure rows
- scenario definitions
- report requests and responses

Schema validation should catch structural issues. Business quality checks belong in services or domain validators.

### Domain Layer

Location: `backend/app/domain/`

Pure financial logic lives here. Functions should be deterministic, side-effect free, and easy to test.

Expected modules:

- `curves.py`
- `spreads.py`
- `exposure.py`
- `hedging.py`
- `stress.py`

Every formula implemented here must be documented in `docs/FORMULAS.md` and covered by pytest.

### Service Layer

Location: `backend/app/services/`

Services coordinate loaders, validation, domain calculations, and report generation. They may use pandas DataFrames, but should avoid burying formulas inside procedural transformations.

### Database Layer

Location: `backend/app/db/`

PostgreSQL and SQLAlchemy are planned later. V1 can run from files first. When persistence is added, database models should not replace schema or domain models.

## Data Philosophy

All sample data must be fake but realistic:

- plausible Brent and WTI price levels
- recognizable monthly futures maturities
- realistic but synthetic cargo sizes and dates
- no vendor-identifying symbols, settlement data, or proprietary reference data

## Testing Strategy

Each financial calculation gets focused unit tests:

- one normal case
- one sign convention case
- one edge case
- one invalid input case where applicable

Data validation receives separate tests using small fixture files. Report export should be covered with smoke tests once implemented.

## Docker Strategy

Docker will be added after the first executable backend slice. The initial target should be:

- one backend service
- mounted local data directory
- pytest command available inside the container

PostgreSQL should wait until persistence is needed.
