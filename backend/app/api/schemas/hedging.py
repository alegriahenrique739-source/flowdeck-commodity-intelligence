from __future__ import annotations

from typing import Any

from pydantic import ConfigDict

from backend.app.api.schemas.common import ApiModel, SummaryObject


class HedgeSimulationResponse(ApiModel):
    net_exposure_result: dict[str, Any]
    hedge_recommendations: list[dict[str, Any]]
    hedge_summary: SummaryObject

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "net_exposure_result": {
                    "buckets": [
                        {
                            "hedge_index": "BRENT",
                            "exposure_month": "2026-09",
                            "book": "CRUDE_BOOK",
                            "net_exposure_bbl": "600000",
                        }
                    ]
                },
                "hedge_recommendations": [
                    {
                        "hedge_index": "BRENT",
                        "exposure_month": "2026-09",
                        "book": "CRUDE_BOOK",
                        "recommended_direction": "SELL",
                        "recommended_lots_rounded": 480,
                        "post_hedge_net_exposure_bbl": "120000",
                        "recommendation_label": (
                            "SELL 480 BRENT 2026-09 futures-equivalent lots "
                            "for CRUDE_BOOK"
                        ),
                    }
                ],
                "hedge_summary": {
                    "total_current_absolute_net_exposure_bbl": "600000",
                    "total_post_hedge_absolute_net_exposure_bbl": "120000",
                    "number_of_recommendations": 1,
                },
            }
        }
    )

