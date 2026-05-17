# FlowDeck - Excel-native Commodity Trading Intelligence

FlowDeck is a local-first analytics platform that turns Brent/WTI CSV inputs into validated curves, exposure analytics, hedge simulation, stress P&L, and trader-ready Excel reports.

## Problem

Commodity desk workflows often rely on Excel and CSV exports. Market data, physical cargo positions, futures hedges, and stress analysis can be fragmented across files, tabs, and manual calculations. Analysts need fast, auditable, desk-ready outputs without losing compatibility with Excel-native workflows.

## Solution

FlowDeck provides a structured analytics layer above local Excel/CSV workflows:

- Validates Brent/WTI market data and position CSVs.
- Builds forward curves and calendar spreads.
- Combines physical cargo and futures positions into hedgeable net exposure.
- Simulates deterministic hedge recommendations.
- Runs synthetic stress P&L.
- Generates professional Excel workbooks.
- Tracks local demo runs and report downloads.
- Provides a local FastAPI backend and Next.js frontend.

## Why It Matters

- Reduces manual spreadsheet errors.
- Speeds up repeated exposure and stress reviews.
- Makes physical plus paper exposure easier to explain.
- Keeps output compatible with Excel-native desk workflows.
- Establishes a bring-your-own-data / bring-your-own-license architecture for future integrations.

## Validation Status

The current repo includes backend pytest coverage, frontend typecheck/lint/build checks, Playwright E2E tests, Workspace upload-flow tests, error-state tests, and visual regression screenshots.

## Honest Constraints

FlowDeck is local/demo mode only. It uses synthetic data, has no authentication or database persistence yet, does not redistribute licensed market data, does not execute trades, and is not financial advice.

