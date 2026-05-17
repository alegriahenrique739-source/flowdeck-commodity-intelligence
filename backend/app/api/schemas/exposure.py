from __future__ import annotations

from typing import Any

from pydantic import ConfigDict

from backend.app.api.schemas.common import ApiModel, SummaryObject


class NetExposureResponse(ApiModel):
    net_exposure_buckets: list[dict[str, Any]]
    summary: SummaryObject

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "net_exposure_buckets": [
                    {
                        "hedge_index": "BRENT",
                        "exposure_month": "2026-09",
                        "book": "CRUDE_BOOK",
                        "physical_exposure_bbl": "600000",
                        "paper_exposure_bbl": "-500000",
                        "net_exposure_bbl": "100000",
                        "absolute_net_exposure_bbl": "100000",
                        "gross_component_exposure_bbl": "1100000",
                        "label": "BRENT 2026-09 / CRUDE_BOOK",
                    }
                ],
                "summary": {
                    "total_net_exposure_bbl": "100000",
                    "total_absolute_net_exposure_bbl": "100000",
                    "number_of_exposure_buckets": 1,
                },
            }
        }
    )

