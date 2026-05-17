from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ApiModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class SummaryObject(ApiModel):
    """Flexible summary container for service-level analytics outputs."""


JsonDict = dict[str, Any]


class FileResponseDescription(ApiModel):
    filename: str = Field(..., examples=["flowdeck_report.xlsx"])
    media_type: str = Field(
        ...,
        examples=[
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ],
    )

