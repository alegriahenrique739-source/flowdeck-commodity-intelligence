from fastapi import APIRouter, File, UploadFile

from backend.app.api.schemas.errors import ERROR_RESPONSES
from backend.app.api.schemas.market_data import MarketDataValidationResponse
from backend.app.api.routes._utils import (
    api_json,
    cleanup_paths,
    save_upload_to_temp_csv,
    validation_error_response,
)
from backend.app.services.market_data import (
    MarketDataValidationError,
    load_market_data_csv,
)


router = APIRouter(prefix="/market-data")


@router.post(
    "/validate",
    response_model=MarketDataValidationResponse,
    tags=["Market Data"],
    summary="Validate market data CSV",
    description=(
        "Validate an uploaded oil futures market data CSV and return a small "
        "preview of normalized rows when the file is valid."
    ),
    response_description="Validation result and preview rows.",
    responses=ERROR_RESPONSES,
)
async def validate_market_data(file: UploadFile = File(...)):
    path = await save_upload_to_temp_csv(file)
    try:
        rows = load_market_data_csv(path)
    except MarketDataValidationError as exc:
        raise validation_error_response(exc.issues) from exc
    finally:
        cleanup_paths(path)

    return {
        "valid": True,
        "row_count": len(rows),
        "errors": [],
        "preview_rows": api_json(rows[:5]),
    }
