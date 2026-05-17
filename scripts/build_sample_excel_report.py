from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.curves import build_forward_curves
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


DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "reports" / "flowdeck_sample_report.xlsx"


def build_sample_report(output_path: str | Path = DEFAULT_OUTPUT_PATH) -> Path:
    market_data_rows = load_market_data_csv(
        PROJECT_ROOT / "data" / "sample" / "market_data" / "valid_brent_wti_futures.csv"
    )
    curve_summaries = build_forward_curves(market_data_rows)

    futures_positions = load_futures_positions_csv(
        PROJECT_ROOT / "data" / "sample" / "positions" / "valid_futures_positions.csv"
    )
    physical_cargoes = load_physical_cargoes_csv(
        PROJECT_ROOT / "data" / "sample" / "positions" / "valid_physical_cargoes.csv"
    )

    futures_exposure = aggregate_futures_exposure(futures_positions)
    physical_exposure = aggregate_physical_exposure(physical_cargoes)
    net_exposure_result = build_net_exposure(physical_exposure, futures_exposure)

    hedge_result = simulate_hedges(
        HedgeSimulationRequest(
            exposure_buckets=net_exposure_result.buckets,
            hedge_mode=HedgeMode.TARGET_HEDGE_RATIO,
            target_hedge_ratio=Decimal("0.80"),
        )
    )
    stress_result = run_stress_pnl(
        predefined_stress_request(
            PredefinedStressScenario.PARALLEL_DOWN_5,
            net_exposure_result.buckets,
        )
    )

    report_input = ExcelReportInput(
        market_data_rows=tuple(market_data_rows),
        curve_summaries=tuple(curve_summaries),
        futures_positions=tuple(futures_positions),
        physical_cargoes=tuple(physical_cargoes),
        net_exposure_result=net_exposure_result,
        hedge_simulation_result=hedge_result,
        stress_result=stress_result,
    )
    return build_excel_report(report_input, output_path)


if __name__ == "__main__":
    output = build_sample_report()
    print(output)
