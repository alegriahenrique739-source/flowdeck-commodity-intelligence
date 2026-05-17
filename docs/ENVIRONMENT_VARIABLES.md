# Environment Variables

Current FlowDeck environment variable reference.

## Backend

| Variable | Where used | Local example | Production example | Required | Notes |
| --- | --- | --- | --- | --- | --- |
| `FLOWDECK_ALLOWED_ORIGINS` | FastAPI CORS configuration | `http://localhost:3000,http://127.0.0.1:3000` | `https://your-flowdeck-demo.vercel.app` | Yes for frontend calls | Use exact origins. Avoid `*` by default. |
| `PORT` | Public backend host start command | Platform provided | Platform provided | Yes on Render-style hosts | Used by `uvicorn ... --port $PORT`; not usually set manually for local dev. |

No backend secrets are currently required for synthetic public demo mode.

Future storage variables are not implemented yet, but likely candidates include:

| Variable | Status | Notes |
| --- | --- | --- |
| `FLOWDECK_STORAGE_BACKEND` | Not implemented | Future switch from local files to durable storage. |
| `FLOWDECK_REPORT_RETENTION_HOURS` | Not implemented | Future cleanup/retention policy. |

## Frontend

| Variable | Where used | Local example | Production example | Required | Notes |
| --- | --- | --- | --- | --- | --- |
| `NEXT_PUBLIC_FLOWDECK_API_BASE_URL` | Frontend API client | `http://127.0.0.1:8000` | `https://your-flowdeck-api.onrender.com` | Yes | Public because browser code needs the API URL. Do not put secrets here. |
| `NEXT_PUBLIC_FLOWDECK_PUBLIC_DEMO_MODE` | Frontend navigation/CTA behavior | `false` | `true` | Recommended for public demo | Emphasizes `/demo`; keeps Workspace out of top-level public nav. |

## Safety Rules

- Do not commit `.env` or `.env.local`.
- Do not put secrets in `NEXT_PUBLIC_*` variables.
- Do not use real trade data or licensed market data in env-driven public demos.
- Keep public CORS origins explicit.

