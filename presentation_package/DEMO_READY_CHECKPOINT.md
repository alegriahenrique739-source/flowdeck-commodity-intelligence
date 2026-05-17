# Demo-Ready Checkpoint

Use this before presenting FlowDeck.

## Start The App

Backend:

```powershell
cd C:\Users\alegr\Documents\Codex\FlowDeck
python -m uvicorn backend.app.main:app --reload
```

Frontend:

```powershell
cd C:\Users\alegr\Documents\Codex\FlowDeck\frontend
npm run dev
```

Open:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
http://localhost:3000
http://localhost:3000/demo
```

## Fastest Demo Path

1. Open `/demo`.
2. Click **Run Sample Demo**.
3. Review summary metrics.
4. Click **View Run Detail**.
5. Click **Download Excel Report**.
6. Open the downloaded workbook.
7. Mention `/workspace` for manual CSV upload.

## Pre-Demo QA

```powershell
python -m pytest
cd frontend
npm run typecheck
npm run lint
npm run build
npm run test:e2e
```

## Do Not Touch Before Demo

- Financial formulas.
- API endpoint behavior.
- Synthetic demo data.
- Visual snapshots without reviewing the UI.
- Dependencies.
- Large frontend refactors.
- Excel report structure.

## Backup Name

```text
FlowDeck_demo_ready_2026-05-17_increment_13
```

