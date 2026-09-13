from fastapi import APIRouter, Request

from backend.app.api.schemas.api_info import ApiInfoResponse
from backend.app.api.schemas.errors import ERROR_RESPONSES

router = APIRouter(prefix="/api")


@router.get(
    "/info",
    response_model=ApiInfoResponse,
    tags=["Capabilities"],
    summary="Get API frontend readiness metadata",
    description=(
        "Return lightweight local API metadata for future frontend clients, "
        "including docs locations and expected local development origins."
    ),
    response_description="Frontend-friendly local API metadata.",
    responses=ERROR_RESPONSES,
)
def api_info(request: Request):
    return {
        "service": "FlowDeck API",
        "version": "0.1.0",
        "environment": request.app.state.deployment_policy.mode,
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
        "frontend_expected_origin_examples": [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
    }
