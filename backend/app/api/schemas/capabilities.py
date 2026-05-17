from __future__ import annotations

from pydantic import ConfigDict

from backend.app.api.schemas.common import ApiModel


class CapabilitiesResponse(ApiModel):
    commodities: list[str]
    currency: str
    unit: str
    modules: list[str]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "commodities": ["BRENT", "WTI"],
                "currency": "USD",
                "unit": "bbl",
                "modules": [
                    "market_data",
                    "curves",
                    "futures_positions",
                    "physical_cargoes",
                    "net_exposure",
                    "hedging",
                    "stress_pnl",
                    "excel_export",
                ],
            }
        }
    )

