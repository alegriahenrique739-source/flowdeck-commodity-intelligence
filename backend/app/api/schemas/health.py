from __future__ import annotations

from pydantic import ConfigDict

from backend.app.api.schemas.common import ApiModel


class HealthResponse(ApiModel):
    status: str
    service: str
    version: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "ok",
                "service": "FlowDeck API",
                "version": "0.1.0",
            }
        }
    )

