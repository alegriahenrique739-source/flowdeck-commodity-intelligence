"""Loopback-only release rehearsal with the real public factory and temporary store."""

import os
import sys
from datetime import UTC, datetime
from pathlib import Path

import uvicorn

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

if __name__ == "__main__":
    if os.getenv("FLOWDECK_PUBLIC_TEST_FIXTURE") != "true":
        raise SystemExit("Test fixture only; never use as a deployment command.")
    from backend.app.main import create_app
    from backend.app.services.workflows import (
        LocalRunRegistry,
        RunMetadata,
        RunStatus,
        RunType,
    )

    root = Path(os.environ["FLOWDECK_TEST_ROOT"])
    # A local synthetic sentinel must never appear in the public registry.
    local = LocalRunRegistry(runs_root=root / "runs", project_root=root)
    local.write_metadata(
        RunMetadata(
            run_id="FD-RUN-20260913-000000-ABCDEF",
            run_type=RunType.DEMO_WORKFLOW,
            status=RunStatus.SUCCESS,
            created_at=datetime.now(UTC),
            notes="LOCAL_REHEARSAL_SENTINEL",
        )
    )
    uvicorn.run(
        create_app(project_root=root),
        host="127.0.0.1",
        port=8444,
        ssl_certfile=str(root / "cert.pem"),
        ssl_keyfile=str(root / "key.pem"),
        log_level="error",
        access_log=False,
    )
