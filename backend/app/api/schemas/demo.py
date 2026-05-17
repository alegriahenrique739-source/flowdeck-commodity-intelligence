from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import ConfigDict, Field

from backend.app.api.schemas.common import ApiModel
from backend.app.services.workflows import RunStatus


class DemoSampleFilesResponse(ApiModel):
    market_data_file: str = Field(
        ...,
        examples=["data/sample/market_data/valid_brent_wti_futures.csv"],
    )
    futures_positions_file: str = Field(
        ...,
        examples=["data/sample/positions/valid_futures_positions.csv"],
    )
    physical_cargoes_file: str = Field(
        ...,
        examples=["data/sample/positions/valid_physical_cargoes.csv"],
    )
    descriptions: dict[str, str]
    note: str = Field(
        ...,
        examples=[
            "Synthetic demo files only. No real trade or licensed market data."
        ],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "market_data_file": (
                    "data/sample/market_data/valid_brent_wti_futures.csv"
                ),
                "futures_positions_file": (
                    "data/sample/positions/valid_futures_positions.csv"
                ),
                "physical_cargoes_file": (
                    "data/sample/positions/valid_physical_cargoes.csv"
                ),
                "descriptions": {
                    "market_data_file": (
                        "Synthetic Brent/WTI futures curve market data."
                    ),
                    "futures_positions_file": "Synthetic oil futures positions.",
                    "physical_cargoes_file": (
                        "Synthetic simplified physical cargoes."
                    ),
                },
                "note": (
                    "Synthetic demo files only. No real trade or licensed "
                    "market data."
                ),
            }
        }
    )


class DemoRunSummaryResponse(ApiModel):
    number_of_curves: int = Field(..., examples=[2])
    number_of_net_exposure_buckets: int = Field(..., examples=[4])
    total_net_exposure_bbl: Decimal = Field(..., examples=["406000"])
    total_post_hedge_absolute_exposure_bbl: Decimal = Field(
        ...,
        examples=["81000"],
    )
    total_stress_pnl_usd: Decimal = Field(..., examples=["-2030000"])


class DemoRunResponse(ApiModel):
    run_id: str = Field(..., examples=["FD-RUN-20260515-140000-ABC123"])
    status: RunStatus = Field(..., examples=["SUCCESS"])
    created_at: datetime
    completed_at: datetime
    summary: DemoRunSummaryResponse
    report_url: str = Field(
        ...,
        examples=["/runs/FD-RUN-20260515-140000-ABC123/report"],
    )
    run_detail_url: str = Field(
        ...,
        examples=["/runs/FD-RUN-20260515-140000-ABC123"],
    )
    assumptions: tuple[str, ...] = Field(
        ...,
        examples=[
            [
                "Synthetic demo data only.",
                "Analytics only.",
                "Not trade execution.",
                "No licensed market data.",
            ]
        ],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "run_id": "FD-RUN-20260515-140000-ABC123",
                "status": "SUCCESS",
                "created_at": "2026-05-15T14:00:00Z",
                "completed_at": "2026-05-15T14:00:03Z",
                "summary": {
                    "number_of_curves": 2,
                    "number_of_net_exposure_buckets": 4,
                    "total_net_exposure_bbl": "406000",
                    "total_post_hedge_absolute_exposure_bbl": "81000",
                    "total_stress_pnl_usd": "-2030000",
                },
                "report_url": "/runs/FD-RUN-20260515-140000-ABC123/report",
                "run_detail_url": "/runs/FD-RUN-20260515-140000-ABC123",
                "assumptions": [
                    "Synthetic demo data only.",
                    "Analytics only.",
                    "Not trade execution.",
                    "No licensed market data.",
                    "Hedge recommendations require human review.",
                ],
            }
        }
    )
