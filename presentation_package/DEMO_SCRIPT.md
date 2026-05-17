# Demo Script

## Demo Objective

Show how FlowDeck turns synthetic Brent/WTI market data, futures positions, and physical cargoes into a repeatable commodity analytics workflow with Excel output.

## Two-Minute Version

1. Open `http://localhost:3000/demo`.
2. Say: "FlowDeck is an Excel-native commodity trading intelligence platform for oil desks."
3. Click **Run Sample Demo**.
4. Show the returned run ID and summary metrics.
5. Click **View Run Detail**.
6. Click **Download Excel Report**.
7. Open the workbook and explain that Excel remains the desk-ready output.

Talking line:

```text
FlowDeck validates Brent/WTI inputs, builds curves, combines physical and futures exposure, simulates hedge impact, stress-tests the book, and exports a clean Excel report. The backend owns the formulas; the frontend displays the workflow.
```

## Five-Minute Walkthrough

1. Open the Overview page and confirm the API is connected.
2. Open `/demo` and explain the synthetic backend-owned workflow.
3. Run the sample demo with hedge ratio `0.80` and stress scenario `PARALLEL_DOWN_5`.
4. Explain curves, exposure buckets, total net exposure, post-hedge absolute exposure, and stress P&L.
5. Open the generated run detail page.
6. Download and open the Excel workbook.
7. Mention `/workspace` for manual CSV upload using the same backend services.

## Audience Notes

- Professor: emphasize applied commodity analytics, sign conventions, and testable formulas.
- Recruiter or trading house: emphasize desk workflow realism, validation, and Excel output.
- Technical reviewer: emphasize modular backend services, thin API routes, typed frontend calls, tests, and local run metadata.
- Non-technical finance contact: emphasize fewer manual steps and clearer review output.

