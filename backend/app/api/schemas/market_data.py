from __future__ import annotations

from typing import Any

from pydantic import ConfigDict

from backend.app.api.schemas.common import ApiModel


class MarketDataValidationResponse(ApiModel):
    valid: bool
    row_count: int
    errors: list[Any]
    preview_rows: list[dict[str, Any]]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "valid": True,
                "row_count": 6,
                "errors": [],
                "preview_rows": [
                    {
                        "valuation_date": "2026-05-01",
                        "commodity": "BRENT",
                        "contract_code": "COU26",
                        "contract_month": "2026-09",
                        "expiry_date": "2026-08-31",
                        "price": "82.15",
                        "currency": "USD",
                        "unit": "bbl",
                        "source": "synthetic_demo",
                    }
                ],
            }
        }
    )

