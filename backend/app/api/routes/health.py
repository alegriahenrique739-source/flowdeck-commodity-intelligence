from fastapi import APIRouter

from backend.app.api.schemas.errors import ERROR_RESPONSES
from backend.app.api.schemas.health import HealthResponse


router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check",
    description="Confirm that the local FlowDeck API process is available.",
    response_description="Service health status.",
    responses=ERROR_RESPONSES,
)
def health_check():
    return {
        "status": "ok",
        "service": "FlowDeck API",
        "version": "0.1.0",
    }
