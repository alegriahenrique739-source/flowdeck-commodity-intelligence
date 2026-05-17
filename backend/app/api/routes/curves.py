from fastapi import APIRouter, File, UploadFile

from backend.app.api.schemas.curves import CurvesBuildResponse
from backend.app.api.schemas.errors import ERROR_RESPONSES
from backend.app.api.routes._utils import (
    api_json,
    cleanup_paths,
    save_upload_to_temp_csv,
    validation_error_response,
)
from backend.app.services.curves import build_forward_curves
from backend.app.services.market_data import (
    MarketDataValidationError,
    load_market_data_csv,
)


router = APIRouter(prefix="/curves")


@router.post(
    "/build",
    response_model=CurvesBuildResponse,
    tags=["Curves"],
    summary="Build forward curves",
    description=(
        "Load validated oil futures market data and build ordered Brent/WTI "
        "forward curve summaries with available calendar spreads."
    ),
    response_description="Curve summaries and calendar spread analytics.",
    responses=ERROR_RESPONSES,
)
async def build_curves(file: UploadFile = File(...)):
    path = await save_upload_to_temp_csv(file)
    try:
        rows = load_market_data_csv(path)
        curves = build_forward_curves(rows)
    except MarketDataValidationError as exc:
        raise validation_error_response(exc.issues) from exc
    finally:
        cleanup_paths(path)

    spreads = []
    for curve in curves:
        for spread_name, spread in curve.calendar_spreads.items():
            spreads.append(
                {
                    "valuation_date": curve.valuation_date,
                    "commodity": curve.commodity,
                    "spread_name": spread_name,
                    "near_contract": spread.near_contract,
                    "far_contract": spread.far_contract,
                    "spread_usd_per_bbl": spread.spread,
                }
            )

    return {
        "curve_summaries": api_json(curves),
        "calendar_spreads": api_json(spreads),
    }
