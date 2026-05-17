from __future__ import annotations

from typing import Any

from backend.app.api.schemas.common import ApiModel


class CurvesBuildResponse(ApiModel):
    curve_summaries: list[dict[str, Any]]
    calendar_spreads: list[dict[str, Any]]

