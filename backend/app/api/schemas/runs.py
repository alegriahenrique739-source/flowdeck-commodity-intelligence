from __future__ import annotations

from pydantic import ConfigDict

from backend.app.api.schemas.common import ApiModel
from backend.app.services.workflows import RunMetadata


class RunsListResponse(ApiModel):
    runs: list[RunMetadata]
    count: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "runs": [
                    {
                        "run_id": "FD-RUN-20260512-235500-ABC123",
                        "run_type": "DEMO_WORKFLOW",
                        "status": "SUCCESS",
                        "created_at": "2026-05-12T23:55:00Z",
                        "completed_at": "2026-05-12T23:55:04Z",
                        "summary": {
                            "number_of_curves": 2,
                            "number_of_net_exposure_buckets": 6,
                            "total_net_exposure_bbl": "406000",
                            "total_post_hedge_absolute_exposure_bbl": "83000",
                            "total_stress_pnl_usd": "-2030000",
                        },
                        "output_files": {
                            "excel_report_path": (
                                "runs/FD-RUN-20260512-235500-ABC123/"
                                "flowdeck_report.xlsx"
                            )
                        },
                    }
                ],
                "count": 1,
            }
        }
    )

