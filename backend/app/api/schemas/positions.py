from __future__ import annotations

from typing import Any

from backend.app.api.schemas.common import ApiModel, SummaryObject


class FuturesAnalyzeResponse(ApiModel):
    valid: bool
    row_count: int
    exposure_aggregation: list[dict[str, Any]]
    summary: SummaryObject


class PhysicalAnalyzeResponse(ApiModel):
    valid: bool
    row_count: int
    physical_exposure_aggregation: list[dict[str, Any]]
    summary: SummaryObject

