from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from shutil import copy2

from backend.app.services.curves import build_forward_curves
from backend.app.services.demo.demo_schemas import (
    DemoRunResult,
    DemoRunSummary,
    DemoSampleFiles,
    DemoStressScenario,
)
from backend.app.services.hedging import (
    HedgeMode,
    HedgeSimulationRequest,
    simulate_hedges,
)
from backend.app.services.market_data import load_market_data_csv
from backend.app.services.positions import (
    aggregate_futures_exposure,
    aggregate_physical_exposure,
    build_net_exposure,
    load_futures_positions_csv,
    load_physical_cargoes_csv,
)
from backend.app.services.reports import ExcelReportInput, build_excel_report
from backend.app.services.risk import (
    PredefinedStressScenario,
    predefined_stress_request,
    run_stress_pnl,
)
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


PROJECT_ROOT = Path(__file__).resolve().parents[4]
MARKET_DATA_PATH = (
    PROJECT_ROOT / "data" / "sample" / "market_data" / "valid_brent_wti_futures.csv"
)
FUTURES_POSITIONS_PATH = (
    PROJECT_ROOT / "data" / "sample" / "positions" / "valid_futures_positions.csv"
)
PHYSICAL_CARGOES_PATH = (
    PROJECT_ROOT / "data" / "sample" / "positions" / "valid_physical_cargoes.csv"
)

DEMO_ASSUMPTIONS = (
    "Synthetic demo data only.",
    "Analytics only.",
    "Not trade execution.",
    "No licensed market data.",
    "Hedge recommendations require human review.",
)


def get_demo_sample_files(
    registry: LocalRunRegistry | None = None,
) -> DemoSampleFiles:
    _validate_sample_files_exist()
    run_registry = registry or LocalRunRegistry(project_root=PROJECT_ROOT)
    return DemoSampleFiles(
        market_data_file=run_registry.project_relative_path(MARKET_DATA_PATH),
        futures_positions_file=run_registry.project_relative_path(
            FUTURES_POSITIONS_PATH
        ),
        physical_cargoes_file=run_registry.project_relative_path(
            PHYSICAL_CARGOES_PATH
        ),
        descriptions={
            "market_data_file": "Synthetic Brent/WTI futures curve market data.",
            "futures_positions_file": "Synthetic oil futures positions.",
            "physical_cargoes_file": "Synthetic simplified physical cargoes.",
        },
        note="Synthetic demo files only. No real trade or licensed market data.",
    )


def run_sample_demo(
    target_hedge_ratio: Decimal = Decimal("0.80"),
    stress_scenario: DemoStressScenario = DemoStressScenario.PARALLEL_DOWN_5,
    output_path: str | Path | None = None,
    runs_root: str | Path | None = None,
    registry: LocalRunRegistry | None = None,
) -> DemoRunResult:
    _validate_target_hedge_ratio(target_hedge_ratio)
    _validate_sample_files_exist()

    run_registry = registry or LocalRunRegistry(
        runs_root=runs_root, project_root=PROJECT_ROOT
    )
    run_id = generate_run_id()
    run_registry.create_run_dir(run_id)
    run_report_path = run_registry.report_path(run_id)
    report_build_path = Path(output_path) if output_path is not None else run_report_path

    metadata = RunMetadata(
        run_id=run_id,
        run_type=RunType.DEMO_WORKFLOW,
        status=RunStatus.RUNNING,
        created_at=datetime.now(UTC),
        input_files=RunInputFiles(
            market_data_file=run_registry.project_relative_path(MARKET_DATA_PATH),
            futures_positions_file=run_registry.project_relative_path(
                FUTURES_POSITIONS_PATH
            ),
            physical_cargoes_file=run_registry.project_relative_path(
                PHYSICAL_CARGOES_PATH
            ),
        ),
        notes="Backend-powered synthetic sample demo workflow.",
    )
    metadata_path = run_registry.write_metadata(metadata)

    try:
        market_data_rows = load_market_data_csv(MARKET_DATA_PATH)
        curves = build_forward_curves(market_data_rows)

        futures_positions = load_futures_positions_csv(FUTURES_POSITIONS_PATH)
        physical_cargoes = load_physical_cargoes_csv(PHYSICAL_CARGOES_PATH)

        futures_exposure = aggregate_futures_exposure(futures_positions)
        physical_exposure = aggregate_physical_exposure(physical_cargoes)
        net_exposure = build_net_exposure(physical_exposure, futures_exposure)

        hedge_result = simulate_hedges(
            HedgeSimulationRequest(
                exposure_buckets=net_exposure.buckets,
                hedge_mode=HedgeMode.TARGET_HEDGE_RATIO,
                target_hedge_ratio=target_hedge_ratio,
            )
        )
        stress_result = run_stress_pnl(
            predefined_stress_request(
                PredefinedStressScenario(stress_scenario.value),
                net_exposure.buckets,
            )
        )

        output = build_excel_report(
            ExcelReportInput(
                market_data_rows=tuple(market_data_rows),
                curve_summaries=tuple(curves),
                futures_positions=tuple(futures_positions),
                physical_cargoes=tuple(physical_cargoes),
                net_exposure_result=net_exposure,
                hedge_simulation_result=hedge_result,
                stress_result=stress_result,
                assumptions=DEMO_ASSUMPTIONS,
            ),
            report_build_path,
        )

        if Path(output).resolve() != run_report_path.resolve():
            run_report_path.parent.mkdir(parents=True, exist_ok=True)
            copy2(output, run_report_path)

        workflow_summary = RunSummary(
            number_of_curves=len(curves),
            number_of_net_exposure_buckets=(
                net_exposure.summary.number_of_exposure_buckets
            ),
            total_net_exposure_bbl=net_exposure.summary.total_net_exposure_bbl,
            total_post_hedge_absolute_exposure_bbl=(
                hedge_result.summary.total_post_hedge_absolute_net_exposure_bbl
            ),
            total_stress_pnl_usd=stress_result.summary.total_stress_pnl_usd,
        )
        completed_at = datetime.now(UTC)
        metadata = metadata.model_copy(
            update={
                "status": RunStatus.SUCCESS,
                "completed_at": completed_at,
                "output_files": RunOutputFiles(
                    excel_report_path=run_registry.project_relative_path(
                        run_report_path
                    )
                ),
                "summary": workflow_summary,
            }
        )
        metadata_path = run_registry.write_metadata(metadata)
    except Exception as exc:
        metadata = metadata.model_copy(
            update={
                "status": RunStatus.FAILED,
                "completed_at": datetime.now(UTC),
                "errors": (str(exc),),
            }
        )
        run_registry.write_metadata(metadata)
        raise

    return DemoRunResult(
        run_id=run_id,
        status=metadata.status,
        created_at=metadata.created_at,
        completed_at=metadata.completed_at,
        summary=DemoRunSummary(
            number_of_curves=workflow_summary.number_of_curves,
            number_of_net_exposure_buckets=(
                workflow_summary.number_of_net_exposure_buckets
            ),
            total_net_exposure_bbl=workflow_summary.total_net_exposure_bbl,
            total_post_hedge_absolute_exposure_bbl=(
                workflow_summary.total_post_hedge_absolute_exposure_bbl
            ),
            total_stress_pnl_usd=workflow_summary.total_stress_pnl_usd,
        ),
        report_url=f"/runs/{run_id}/report",
        run_detail_url=f"/runs/{run_id}",
        assumptions=DEMO_ASSUMPTIONS,
        excel_output_path=run_report_path,
        metadata_output_path=metadata_path,
    )


def _validate_target_hedge_ratio(target_hedge_ratio: Decimal) -> None:
    if target_hedge_ratio < 0 or target_hedge_ratio > 1:
        raise ValueError("target_hedge_ratio must be between 0 and 1 inclusive.")


def _validate_sample_files_exist() -> None:
    missing = [
        path
        for path in (MARKET_DATA_PATH, FUTURES_POSITIONS_PATH, PHYSICAL_CARGOES_PATH)
        if not path.exists()
    ]
    if missing:
        missing_list = ", ".join(
            path.relative_to(PROJECT_ROOT).as_posix() for path in missing
        )
        raise FileNotFoundError(f"Missing demo sample file(s): {missing_list}")
