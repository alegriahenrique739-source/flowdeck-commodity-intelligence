from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from backend.app.api.routes.runs import get_run_registry
from backend.app.main import app
from backend.app.services.workflows import (
    LocalRunRegistry,
    RunMetadata,
    RunOutputFiles,
    RunStatus,
    RunSummary,
    RunType,
)


client = TestClient(app)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEST_OUTPUT_ROOT = PROJECT_ROOT / "reports" / "test_outputs" / "runs_api"


def test_get_runs_returns_200() -> None:
    with _override_registry(_new_registry()):
        response = client.get("/runs")

    assert response.status_code == 200
    assert response.json()["runs"] == []
    assert response.json()["count"] == 0


def test_get_runs_returns_empty_list_when_no_valid_runs_exist() -> None:
    registry = _new_registry()
    invalid_dir = registry.runs_root / "FD-RUN-20260512-235500-BAD999"
    invalid_dir.mkdir(parents=True)
    (invalid_dir / "run_metadata.json").write_text("not valid json", encoding="utf-8")

    with _override_registry(registry):
        response = client.get("/runs")

    assert response.status_code == 200
    assert response.json() == {"runs": [], "count": 0}


def test_get_runs_returns_created_run_metadata() -> None:
    registry = _new_registry()
    metadata = _metadata(
        run_id="FD-RUN-20260512-235500-ABC123",
        created_at=datetime(2026, 5, 12, 23, 55, tzinfo=UTC),
    )
    registry.write_metadata(metadata)

    with _override_registry(registry):
        response = client.get("/runs")

    payload = response.json()
    assert response.status_code == 200
    assert payload["count"] == 1
    assert payload["runs"][0]["run_id"] == metadata.run_id
    assert payload["runs"][0]["status"] == "SUCCESS"


def test_get_runs_respects_limit_and_sorts_newest_first() -> None:
    registry = _new_registry()
    older = _metadata(
        run_id="FD-RUN-20260512-235500-ABC123",
        created_at=datetime(2026, 5, 12, 23, 55, tzinfo=UTC),
    )
    newer = _metadata(
        run_id="FD-RUN-20260513-001500-DEF456",
        created_at=datetime(2026, 5, 13, 0, 15, tzinfo=UTC),
    )
    registry.write_metadata(older)
    registry.write_metadata(newer)

    with _override_registry(registry):
        response = client.get("/runs", params={"limit": 1})

    payload = response.json()
    assert response.status_code == 200
    assert payload["count"] == 1
    assert payload["runs"][0]["run_id"] == newer.run_id


def test_get_runs_filters_by_status() -> None:
    registry = _new_registry()
    success = _metadata(
        run_id="FD-RUN-20260512-235500-ABC123",
        created_at=datetime(2026, 5, 12, 23, 55, tzinfo=UTC),
        status=RunStatus.SUCCESS,
    )
    failed = _metadata(
        run_id="FD-RUN-20260513-001500-DEF456",
        created_at=datetime(2026, 5, 13, 0, 15, tzinfo=UTC),
        status=RunStatus.FAILED,
    )
    registry.write_metadata(success)
    registry.write_metadata(failed)

    with _override_registry(registry):
        response = client.get("/runs", params={"status": "SUCCESS"})

    payload = response.json()
    assert response.status_code == 200
    assert payload["count"] == 1
    assert payload["runs"][0]["run_id"] == success.run_id


def test_get_runs_filters_by_run_type() -> None:
    registry = _new_registry()
    metadata = _metadata(
        run_id="FD-RUN-20260512-235500-ABC123",
        created_at=datetime(2026, 5, 12, 23, 55, tzinfo=UTC),
        run_type=RunType.DEMO_WORKFLOW,
    )
    registry.write_metadata(metadata)

    with _override_registry(registry):
        response = client.get("/runs", params={"run_type": "DEMO_WORKFLOW"})

    payload = response.json()
    assert response.status_code == 200
    assert payload["count"] == 1
    assert payload["runs"][0]["run_type"] == "DEMO_WORKFLOW"


def test_get_runs_invalid_status_returns_400() -> None:
    with _override_registry(_new_registry()):
        response = client.get("/runs", params={"status": "NOT_A_STATUS"})

    assert response.status_code == 400
    assert response.json()["detail"]["error_code"] == "REQUEST_VALIDATION_ERROR"


def test_get_runs_invalid_run_type_returns_400() -> None:
    with _override_registry(_new_registry()):
        response = client.get("/runs", params={"run_type": "NOT_A_RUN_TYPE"})

    assert response.status_code == 400
    assert response.json()["detail"]["error_code"] == "REQUEST_VALIDATION_ERROR"


def test_get_run_by_id_returns_correct_metadata() -> None:
    registry = _new_registry()
    metadata = _metadata(
        run_id="FD-RUN-20260512-235500-ABC123",
        created_at=datetime(2026, 5, 12, 23, 55, tzinfo=UTC),
    )
    registry.write_metadata(metadata)

    with _override_registry(registry):
        response = client.get(f"/runs/{metadata.run_id}")

    payload = response.json()
    assert response.status_code == 200
    assert payload["run_id"] == metadata.run_id
    assert payload["summary"]["number_of_curves"] == 2
    assert payload["output_files"]["excel_report_path"].endswith("flowdeck_report.xlsx")


def test_get_run_report_returns_xlsx_file() -> None:
    registry = _new_registry()
    report_path = _write_report_file(registry, "FD-RUN-20260512-235500-ABC123")
    metadata = _metadata(
        run_id="FD-RUN-20260512-235500-ABC123",
        created_at=datetime(2026, 5, 12, 23, 55, tzinfo=UTC),
        excel_report_path=report_path,
    )
    registry.write_metadata(metadata)

    with _override_registry(registry):
        response = client.get(f"/runs/{metadata.run_id}/report")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert response.content.startswith(b"PK")


def test_get_run_report_has_download_filename() -> None:
    registry = _new_registry()
    report_path = _write_report_file(registry, "FD-RUN-20260512-235500-ABC123")
    metadata = _metadata(
        run_id="FD-RUN-20260512-235500-ABC123",
        created_at=datetime(2026, 5, 12, 23, 55, tzinfo=UTC),
        excel_report_path=report_path,
    )
    registry.write_metadata(metadata)

    with _override_registry(registry):
        response = client.get(f"/runs/{metadata.run_id}/report")

    assert response.status_code == 200
    assert "attachment" in response.headers["content-disposition"]
    assert f"flowdeck_report_{metadata.run_id}.xlsx" in response.headers[
        "content-disposition"
    ]


def test_get_report_for_unknown_valid_run_id_returns_404() -> None:
    with _override_registry(_new_registry()):
        response = client.get("/runs/FD-RUN-20260512-235500-ABC123/report")

    assert response.status_code == 404
    assert response.json()["detail"]["error_code"] == "RUN_NOT_FOUND"


def test_get_report_for_run_with_missing_report_returns_404() -> None:
    registry = _new_registry()
    metadata = _metadata(
        run_id="FD-RUN-20260512-235500-ABC123",
        created_at=datetime(2026, 5, 12, 23, 55, tzinfo=UTC),
        excel_report_path=registry.report_path("FD-RUN-20260512-235500-ABC123"),
    )
    registry.write_metadata(metadata)

    with _override_registry(registry):
        response = client.get(f"/runs/{metadata.run_id}/report")

    assert response.status_code == 404
    assert response.json()["detail"]["error_code"] == "RUN_REPORT_NOT_FOUND"


def test_get_report_with_unsafe_run_id_is_rejected() -> None:
    with _override_registry(_new_registry()):
        response = client.get("/runs/bad..id/report")

    assert response.status_code == 400
    assert response.json()["detail"]["error_code"] == "INVALID_RUN_ID"


def test_get_report_rejects_metadata_path_outside_run_folder() -> None:
    registry = _new_registry()
    outside_report = registry.runs_root / "outside.xlsx"
    outside_report.write_bytes(b"PK fake xlsx")
    metadata = _metadata(
        run_id="FD-RUN-20260512-235500-ABC123",
        created_at=datetime(2026, 5, 12, 23, 55, tzinfo=UTC),
        excel_report_path=outside_report,
    )
    registry.write_metadata(metadata)

    with _override_registry(registry):
        response = client.get(f"/runs/{metadata.run_id}/report")

    assert response.status_code == 400
    assert response.json()["detail"]["error_code"] == "INVALID_RUN_REPORT_PATH"


def test_get_unknown_run_id_returns_404() -> None:
    with _override_registry(_new_registry()):
        response = client.get("/runs/FD-RUN-20260512-235500-ABC123")

    assert response.status_code == 404
    assert response.json()["detail"]["error_code"] == "RUN_NOT_FOUND"


def test_path_traversal_attempt_is_rejected() -> None:
    with _override_registry(_new_registry()):
        response = client.get("/runs/bad..id")

    assert response.status_code == 400
    assert response.json()["detail"]["error_code"] == "INVALID_RUN_ID"


def test_openapi_includes_runs_endpoints() -> None:
    schema = client.get("/openapi.json").json()

    assert "/runs" in schema["paths"]
    assert "/runs/{run_id}" in schema["paths"]
    assert "/runs/{run_id}/report" in schema["paths"]
    assert schema["paths"]["/runs"]["get"]["tags"] == ["Runs"]
    assert schema["paths"]["/runs/{run_id}"]["get"]["tags"] == ["Runs"]
    assert schema["paths"]["/runs/{run_id}/report"]["get"]["tags"] == ["Runs"]
    parameter_names = {
        parameter["name"] for parameter in schema["paths"]["/runs"]["get"]["parameters"]
    }
    assert {"limit", "status", "run_type"}.issubset(parameter_names)


class _override_registry:
    def __init__(self, registry: LocalRunRegistry) -> None:
        self.registry = registry

    def __enter__(self):
        app.dependency_overrides[get_run_registry] = lambda: self.registry

    def __exit__(self, *_exc_info):
        app.dependency_overrides.pop(get_run_registry, None)


def _new_registry() -> LocalRunRegistry:
    root = TEST_OUTPUT_ROOT / uuid4().hex / "runs"
    root.mkdir(parents=True, exist_ok=True)
    return LocalRunRegistry(runs_root=root, project_root=PROJECT_ROOT)


def _write_report_file(registry: LocalRunRegistry, run_id: str) -> Path:
    report_path = registry.report_path(run_id)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_bytes(b"PK fake xlsx content")
    return report_path


def _metadata(
    run_id: str,
    created_at: datetime,
    excel_report_path: str | Path | None = None,
    status: RunStatus = RunStatus.SUCCESS,
    run_type: RunType = RunType.DEMO_WORKFLOW,
) -> RunMetadata:
    return RunMetadata(
        run_id=run_id,
        run_type=run_type,
        status=status,
        created_at=created_at,
        completed_at=created_at,
        output_files=RunOutputFiles(
            excel_report_path=(
                str(excel_report_path)
                if excel_report_path is not None
                else f"runs/{run_id}/flowdeck_report.xlsx"
            )
        ),
        summary=RunSummary(
            number_of_curves=2,
            number_of_net_exposure_buckets=6,
            total_net_exposure_bbl=Decimal("406000"),
            total_post_hedge_absolute_exposure_bbl=Decimal("83000"),
            total_stress_pnl_usd=Decimal("-2030000"),
        ),
    )
