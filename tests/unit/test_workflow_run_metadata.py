from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from backend.app.services.workflows import (
    LocalRunRegistry,
    RunInputFiles,
    RunMetadata,
    RunOutputFiles,
    RunStatus,
    RunSummary,
    RunType,
    generate_run_id,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEST_OUTPUT_ROOT = PROJECT_ROOT / "reports" / "test_outputs" / "workflow_metadata"


def _test_runs_root() -> Path:
    path = TEST_OUTPUT_ROOT / uuid4().hex / "runs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_run_id_is_generated_with_readable_prefix() -> None:
    run_id = generate_run_id(datetime(2026, 5, 12, 23, 55, tzinfo=UTC))

    assert run_id.startswith("FD-RUN-20260512-235500-")
    assert len(run_id.rsplit("-", maxsplit=1)[-1]) == 6


def test_run_metadata_serializes_to_json() -> None:
    metadata = RunMetadata(
        run_id="FD-RUN-20260512-235500-ABC123",
        run_type=RunType.DEMO_WORKFLOW,
        status=RunStatus.SUCCESS,
        created_at=datetime(2026, 5, 12, 23, 55, tzinfo=UTC),
        completed_at=datetime(2026, 5, 12, 23, 56, tzinfo=UTC),
        input_files=RunInputFiles(market_data_file="data/sample/market.csv"),
        output_files=RunOutputFiles(
            excel_report_path="runs/FD-RUN-20260512-235500-ABC123/flowdeck_report.xlsx"
        ),
        summary=RunSummary(
            number_of_curves=2,
            number_of_net_exposure_buckets=4,
            total_net_exposure_bbl=Decimal("100000"),
            total_post_hedge_absolute_exposure_bbl=Decimal("20000"),
            total_stress_pnl_usd=Decimal("-500000"),
        ),
    )

    payload = metadata.model_dump_json()

    assert "FD-RUN-20260512-235500-ABC123" in payload
    assert "SUCCESS" in payload
    assert "total_stress_pnl_usd" in payload


def test_run_registry_creates_run_folder() -> None:
    runs_root = _test_runs_root()
    registry = LocalRunRegistry(runs_root=runs_root, project_root=PROJECT_ROOT)
    run_id = "FD-RUN-20260512-235500-ABC123"

    run_dir = registry.create_run_dir(run_id)

    assert run_dir.exists()
    assert run_dir == runs_root / run_id


def test_run_registry_writes_run_metadata_json() -> None:
    registry = LocalRunRegistry(runs_root=_test_runs_root(), project_root=PROJECT_ROOT)
    metadata = RunMetadata(
        run_id="FD-RUN-20260512-235500-ABC123",
        run_type=RunType.DEMO_WORKFLOW,
        status=RunStatus.SUCCESS,
        created_at=datetime(2026, 5, 12, 23, 55, tzinfo=UTC),
    )

    path = registry.write_metadata(metadata)
    loaded = registry.read_metadata(metadata.run_id)

    assert path.exists()
    assert path.name == "run_metadata.json"
    assert loaded.run_id == metadata.run_id
    assert loaded.status == RunStatus.SUCCESS


def test_failed_run_metadata_can_be_recorded() -> None:
    registry = LocalRunRegistry(runs_root=_test_runs_root(), project_root=PROJECT_ROOT)
    metadata = RunMetadata(
        run_id="FD-RUN-20260512-235500-ABC123",
        run_type=RunType.DEMO_WORKFLOW,
        status=RunStatus.FAILED,
        created_at=datetime(2026, 5, 12, 23, 55, tzinfo=UTC),
        completed_at=datetime(2026, 5, 12, 23, 56, tzinfo=UTC),
        errors=("Synthetic failure for test coverage.",),
    )

    registry.write_metadata(metadata)
    loaded = registry.read_metadata(metadata.run_id)

    assert loaded.status == RunStatus.FAILED
    assert loaded.errors == ("Synthetic failure for test coverage.",)
