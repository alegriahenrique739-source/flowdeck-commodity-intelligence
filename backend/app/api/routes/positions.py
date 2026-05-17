from fastapi import APIRouter, File, UploadFile

from backend.app.api.schemas.errors import ERROR_RESPONSES
from backend.app.api.schemas.positions import (
    FuturesAnalyzeResponse,
    PhysicalAnalyzeResponse,
)
from backend.app.api.routes._utils import (
    api_json,
    cleanup_paths,
    save_upload_to_temp_csv,
    validation_error_response,
)
from backend.app.services.positions import (
    FuturesPositionValidationError,
    PhysicalCargoValidationError,
    aggregate_futures_exposure,
    aggregate_physical_exposure,
    load_futures_positions_csv,
    load_physical_cargoes_csv,
)


router = APIRouter(prefix="/positions")


@router.post(
    "/futures/analyze",
    response_model=FuturesAnalyzeResponse,
    tags=["Positions"],
    summary="Analyze futures positions",
    description=(
        "Validate an uploaded futures positions CSV and aggregate signed paper "
        "exposure by commodity, contract month and book."
    ),
    response_description="Futures validation status, exposure buckets and summary.",
    responses=ERROR_RESPONSES,
)
async def analyze_futures_positions(file: UploadFile = File(...)):
    path = await save_upload_to_temp_csv(file)
    try:
        rows = load_futures_positions_csv(path)
        exposure = aggregate_futures_exposure(rows)
    except FuturesPositionValidationError as exc:
        raise validation_error_response(exc.issues) from exc
    finally:
        cleanup_paths(path)

    return {
        "valid": True,
        "row_count": len(rows),
        "exposure_aggregation": api_json(exposure),
        "summary": _futures_summary(exposure),
    }


@router.post(
    "/physical/analyze",
    response_model=PhysicalAnalyzeResponse,
    tags=["Positions"],
    summary="Analyze physical cargoes",
    description=(
        "Validate an uploaded physical cargo CSV and aggregate signed physical "
        "exposure by commodity, pricing index, pricing month and book."
    ),
    response_description="Physical cargo validation status, exposure buckets and summary.",
    responses=ERROR_RESPONSES,
)
async def analyze_physical_cargoes(file: UploadFile = File(...)):
    path = await save_upload_to_temp_csv(file)
    try:
        rows = load_physical_cargoes_csv(path)
        exposure = aggregate_physical_exposure(rows)
    except PhysicalCargoValidationError as exc:
        raise validation_error_response(exc.issues) from exc
    finally:
        cleanup_paths(path)

    return {
        "valid": True,
        "row_count": len(rows),
        "physical_exposure_aggregation": api_json(exposure),
        "summary": _physical_summary(exposure),
    }


def _futures_summary(exposure):
    return api_json(
        {
            "number_of_buckets": len(exposure),
            "total_gross_exposure_bbl": sum(
                bucket.gross_exposure_bbl for bucket in exposure
            ),
            "total_net_exposure_bbl": sum(
                bucket.net_exposure_bbl for bucket in exposure
            ),
            "total_long_exposure_bbl": sum(
                bucket.long_exposure_bbl for bucket in exposure
            ),
            "total_short_exposure_bbl": sum(
                bucket.short_exposure_bbl for bucket in exposure
            ),
        }
    )


def _physical_summary(exposure):
    return api_json(
        {
            "number_of_buckets": len(exposure),
            "total_gross_physical_exposure_bbl": sum(
                bucket.gross_physical_exposure_bbl for bucket in exposure
            ),
            "total_net_physical_exposure_bbl": sum(
                bucket.net_physical_exposure_bbl for bucket in exposure
            ),
            "total_long_physical_exposure_bbl": sum(
                bucket.long_physical_exposure_bbl for bucket in exposure
            ),
            "total_short_physical_exposure_bbl": sum(
                bucket.short_physical_exposure_bbl for bucket in exposure
            ),
        }
    )
