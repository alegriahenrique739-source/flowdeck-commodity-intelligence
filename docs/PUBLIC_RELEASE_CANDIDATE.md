# Restricted Public Demo Release Candidate

## Scope

This branch is based on `be8eb76120c90a4048d492bf89dd26dc8714a888`, the previous
public demo checkpoint. It ports only the reviewed public API boundary, isolated
synthetic run storage, public navigation fixes, submitted-demo-settings narration,
opt-in search policy and release tests. It is not a customer/paid-pilot release.

Private pilot, identity providers, imported portfolios, intake, Desk, pricing and
reconciliation developments are deliberately absent. The original workspace is
not replaced. Financial services, sample CSVs, Excel generation and production
Python requirements remain identical to the base commit.

Public mode allows health, capabilities, API info, sample-file descriptions, demo
generation and read-only run/report endpoints only. All other routes are denied
before request-body parsing. Existing local API paths remain available in local
mode, which must never be deployed publicly.

679 historical generated test JSON files are removed from Git tracking, not from
local disk. This does not erase them from old Git history. No real data or secret
was identified by the targeted candidate scan; a scan is not a security guarantee.

## Dependencies

The release reuses the versions already tested in the development workspace:
Next/eslint-config-next 15.5.24, Playwright 1.63.0 and PostCSS 8.5.28 (override).
React stays at 18.3.1. No private OIDC or icon packages are included. The regenerated
lockfile belongs to this branch, not the development workspace.

`requirements-qa.txt` adds cryptography only to generate short-lived loopback TLS
certificates for tests. Render still installs `requirements.txt`; no private keys,
certificates, IdP fixture or private production dependency is shipped.

## Hosting Handoff

Do not push to an auto-deployed production branch before reviewing hosting settings.
Use the same reviewed commit for both applications, backend first:

- Render: `FLOWDECK_DEPLOYMENT_MODE=public_demo`,
  `FLOWDECK_ENABLE_LOCAL_IMPORTS=false`, `FLOWDECK_PUBLIC_MAX_RUNS=100`,
  `FLOWDECK_ALLOWED_ORIGINS=https://flowdeck-commodity-intelligence.vercel.app`.
- Render build: `pip install -r requirements.txt`. Python 3.11 or newer.
- Render start: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT --workers 1`.
  One instance only; changing `render.yaml` does not prove an existing service's
  environment changed. Confirm the environment before promotion.
- Vercel project root: `frontend`; install `npm ci`; build `npm run build`.
- Vercel: `NEXT_PUBLIC_FLOWDECK_PUBLIC_DEMO_MODE=true`,
  `NEXT_PUBLIC_FLOWDECK_API_BASE_URL=https://flowdeck-api.onrender.com`,
  `FLOWDECK_ALLOW_INDEXING=false`.
- Do not publish the loopback rehearsal's API URL or `.next` build. Vercel must
  rebuild from source with its own environment.

After deployment, run the GET-only gate:

```bash
python scripts/check_public_demo_gate.py --backend-url https://flowdeck-api.onrender.com --frontend-origin https://flowdeck-commodity-intelligence.vercel.app
```

Then manually verify `/demo -> Run Sample Demo -> View Run Detail -> Download Excel`,
direct upload denial, exact CORS, safe capacity errors and report noindex headers.
The gate returning green is not a security audit. Review storage and edge behavior
on the host. Old local-registry run links are not migrated into public storage.

Keep indexing off until this review passes. Search Console ownership, submission
and actual search-engine indexing are separate tasks, not outcomes of this commit.

## Reproduce Checks

```bash
python -m pip install -r requirements-qa.txt
python -m pytest
cd frontend
npm ci
npm run typecheck
npm run lint
npm run build
npm run test:unit
```

For the real restricted API/browser check, stop any server using this checkout's
`.next`, set the following environment in PowerShell, then run:

```powershell
$env:NEXT_PUBLIC_FLOWDECK_PUBLIC_DEMO_MODE='true'
$env:NEXT_PUBLIC_FLOWDECK_API_BASE_URL='https://localhost:8444'
$env:FLOWDECK_ALLOW_INDEXING='false'
npm run build
npm run test:e2e:public
```

Install the Playwright Chromium browser if missing. The harness owns HTTPS ports
3443/8444 and a temporary one-run store; it refuses occupied ports, blocks browser
requests to other origins, and cleans up only its own resources. It uses installed
Python via `FLOWDECK_TEST_PYTHON`, or uv with `requirements-qa.txt`. The TLS generator
file is test-only; its historical filename does not include any private-pilot code.

Restore local flags/API URL before local use. The ordinary smoke suite requires a
matching frontend server; the restricted HTTPS suite starts its own services.

## Verification (2026-09-13)

- Full candidate backend: **242 passed, 1 skipped**, 2 existing deprecation warnings.
  The Windows symlink-creation privilege test is the skip.
- Frontend typecheck and lint: passed. Local and public HTTPS production builds:
  passed. Search-policy tests: **26 passed**.
- Local smoke, Workspace upload/download and error-state browser tests: **19 passed**.
  An initial attempt on port 4310 had 6 CORS failures; rerunning on the backend's
  approved port-3000 origin passed without widening CORS or changing application code.
- Real restricted HTTPS browser tests: **5 passed**, including real demo generation,
  metadata, exact downloaded workbook bytes, denied uploads, 429/503 and isolation.
- `npm audit --omit=dev --audit-level=high`: **0 known runtime vulnerabilities**.
  This is not a complete source/security or development-dependency audit.
- Staged whitespace check passed; targeted staged key/token-pattern scan had no
  matches. Generated JSON is untracked and ignored. Visual snapshots unchanged.
- The development workspace's independent baseline remains **508 passed, 1 skipped**.
  It includes private/local modules deliberately absent from this release branch.
- Live GET gate: **BLOCKED**. Health and exact-origin CORS passed, but mode and
  allowlist contract did not. Render opened at its sign-in page. No hosting setting
  was changed, no branch was pushed and no deployment/indexing was performed.

## Remaining Limits

Shared synthetic data only; no authentication, customer uploads, durable storage,
distributed admission control or automatic cleanup. A full store returns 503
without deleting old reports. One process may generate one run at a time, with a
five-second start interval. Platform-level abuse controls and operations review
remain necessary. No licensed feed, trade execution or financial advice.

Rollback must never re-expose the old permissive backend publicly. If the new
boundary fails, restrict/suspend the public API and use the local demo fallback;
restore only a previously verified restricted revision and its matching frontend.
