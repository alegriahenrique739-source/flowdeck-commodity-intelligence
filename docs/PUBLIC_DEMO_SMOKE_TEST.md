# Public Demo Smoke Test

Use this checklist after every public demo deployment.

Backend URL:

```text
https://flowdeck-api.onrender.com
```

Frontend URL:

```text
https://flowdeck-commodity-intelligence.vercel.app
```

Demo entry:

```text
https://flowdeck-commodity-intelligence.vercel.app/demo
```

Current Public Demo V1 pass status:

- Backend health works.
- `/demo` opens.
- **Run Sample Demo** works.
- Generated `/runs/[runId]` detail page opens.
- Excel report downloads successfully.
- Render CORS includes the Vercel frontend origin.

## Test URLs

| Check | URL | Expected result | Pass/Fail | Notes |
| --- | --- | --- | --- | --- |
| Backend health | `/health` | JSON status `ok` |  |  |
| Backend docs | `/docs` | Swagger UI loads |  |  |
| Frontend home | `/` | FlowDeck page loads |  |  |
| Demo page | `/demo` | Demo page loads and shows Run Sample Demo |  |  |
| Runs dashboard | `/runs` | Runs page loads |  |  |

## Current Deployed URL Checks

| Check | URL | Current status |
| --- | --- | --- |
| Backend health | `https://flowdeck-api.onrender.com/health` | Pass |
| Backend docs | `https://flowdeck-api.onrender.com/docs` | Available for review |
| Frontend home | `https://flowdeck-commodity-intelligence.vercel.app` | Pass |
| Demo page | `https://flowdeck-commodity-intelligence.vercel.app/demo` | Pass |
| Demo workflow | `/demo -> Run Sample Demo -> /runs/[runId] -> Download Excel Report` | Pass |

## Demo Flow

| Step | Expected result | Pass/Fail | Notes |
| --- | --- | --- | --- |
| Click **Run Sample Demo** | Loading state appears, then success state |  |  |
| Confirm `run_id` | Run ID begins with `FD-RUN-` |  |  |
| Click **View Run Detail** | Browser opens `/runs/[runId]` |  |  |
| Confirm run detail metrics | Curves, exposure buckets, total net, hedge, and stress metrics visible |  |  |
| Click **Download Excel Report** | `.xlsx` downloads |  |  |
| Open workbook | Workbook opens and contains FlowDeck sheets |  |  |

## Safety Checks

| Check | Expected result | Pass/Fail | Notes |
| --- | --- | --- | --- |
| Synthetic disclaimer | Demo/product copy states synthetic data only |  |  |
| Workspace not promoted | Top-level public nav emphasizes Demo, not Workspace |  |  |
| CORS | Browser calls to backend succeed from frontend origin |  |  |
| Error handling | No stack traces visible during normal demo failures |  |  |

## Notes

Record deployment URL, commit, date, and any failures here before sharing the public link.
