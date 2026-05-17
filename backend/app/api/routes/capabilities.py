from fastapi import APIRouter

from backend.app.api.schemas.capabilities import CapabilitiesResponse
from backend.app.api.schemas.errors import ERROR_RESPONSES

router = APIRouter()


@router.get(
    "/capabilities",
    response_model=CapabilitiesResponse,
    tags=["Capabilities"],
    summary="List API capabilities",
    description=(
        "Return the supported commodities, currency, unit and analytics modules "
        "currently exposed by FlowDeck."
    ),
    response_description="Supported FlowDeck analytics capabilities.",
    responses=ERROR_RESPONSES,
)
def capabilities():
    return {
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
