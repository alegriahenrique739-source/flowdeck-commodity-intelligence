from __future__ import annotations

from pydantic import ConfigDict

from backend.app.api.schemas.common import ApiModel


class ApiInfoResponse(ApiModel):
    service: str
    version: str
    environment: str
    docs_url: str
    openapi_url: str
    frontend_expected_origin_examples: list[str]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "service": "FlowDeck API",
                "version": "0.1.0",
                "environment": "local",
                "docs_url": "/docs",
                "openapi_url": "/openapi.json",
                "frontend_expected_origin_examples": [
                    "http://localhost:3000",
                    "http://127.0.0.1:3000",
                ],
            }
        }
    )

