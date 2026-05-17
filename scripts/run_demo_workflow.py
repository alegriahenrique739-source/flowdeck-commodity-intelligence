from __future__ import annotations

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.demo import run_sample_demo


def run_demo_workflow(
    output_path: str | Path | None = None,
    runs_root: str | Path | None = None,
) -> dict[str, object]:
    result = run_sample_demo(output_path=output_path, runs_root=runs_root)
    return {
        "run_id": result.run_id,
        "status": result.status.value,
        "curve_count": result.summary.number_of_curves,
        "net_exposure_bucket_count": result.summary.number_of_net_exposure_buckets,
        "total_net_exposure_bbl": result.summary.total_net_exposure_bbl,
        "total_post_hedge_absolute_exposure_bbl": (
            result.summary.total_post_hedge_absolute_exposure_bbl
        ),
        "total_stress_pnl_usd": result.summary.total_stress_pnl_usd,
        "excel_output_path": result.excel_output_path,
        "metadata_output_path": result.metadata_output_path,
    }


def main() -> None:
    summary = run_demo_workflow()
    print("FlowDeck demo workflow complete")
    print(f"Run ID: {summary['run_id']}")
    print(f"Status: {summary['status']}")
    print(f"Curves: {summary['curve_count']}")
    print(f"Net exposure buckets: {summary['net_exposure_bucket_count']}")
    print(f"Total net exposure bbl: {summary['total_net_exposure_bbl']}")
    print(
        "Total post-hedge absolute exposure bbl: "
        f"{summary['total_post_hedge_absolute_exposure_bbl']}"
    )
    print(f"Total stress P&L USD: {summary['total_stress_pnl_usd']}")
    print(f"Report path: {summary['excel_output_path']}")
    print(f"Metadata path: {summary['metadata_output_path']}")


if __name__ == "__main__":
    main()
