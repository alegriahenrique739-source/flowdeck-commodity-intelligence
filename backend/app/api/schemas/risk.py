from __future__ import annotations

from typing import Any

from pydantic import ConfigDict

from backend.app.api.schemas.common import ApiModel, SummaryObject


class StressPnlResponse(ApiModel):
    net_exposure_result: dict[str, Any]
    stress_bucket_results: list[dict[str, Any]]
    stress_summary: SummaryObject

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "net_exposure_result": {
                    "buckets": [
                        {
                            "hedge_index": "BRENT",
                            "exposure_month": "2026-09",
                            "book": "CRUDE_BOOK",
                            "net_exposure_bbl": "100000",
                        }
                    ]
                },
                "stress_bucket_results": [
                    {
                        "scenario_name": "PARALLEL_DOWN_5",
                        "hedge_index": "BRENT",
                        "exposure_month": "2026-09",
                        "book": "CRUDE_BOOK",
                        "net_exposure_bbl": "100000",
                        "price_delta_usd_per_bbl": "-5",
                        "stress_pnl_usd": "-500000",
                        "pnl_direction": "LOSS",
                    }
                ],
                "stress_summary": {
                    "scenario_name": "PARALLEL_DOWN_5",
                    "total_stress_pnl_usd": "-500000",
                    "number_of_buckets": 1,
                    "number_of_loss_buckets": 1,
                },
            }
        }
    )

