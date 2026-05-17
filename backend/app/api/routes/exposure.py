from fastapi import APIRouter, File, UploadFile

from backend.app.api.schemas.errors import ERROR_RESPONSES
from backend.app.api.schemas.exposure import NetExposureResponse
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
    build_net_exposure,
    load_futures_positions_csv,
    load_physical_cargoes_csv,
)


router = APIRouter(prefix="/exposure")


@router.post(
    "/net",
    response_model=NetExposureResponse,
    tags=["Exposure"],
    summary="Build net exposure",
    description=(
        "Combine physical cargo and futures position exposures into a common "
        "monthly hedge-index view by book."
    ),
    response_description="Net exposure buckets and portfolio summary metrics.",
    responses=ERROR_RESPONSES,
)
async def build_net_exposure_endpoint(
    futures_file: UploadFile = File(...),
    physical_file: UploadFile = File(...),
):
    futures_path = await save_upload_to_temp_csv(futures_file)
    physical_path = await save_upload_to_temp_csv(physical_file)
    try:
        net_exposure = _build_net_exposure_from_paths(futures_path, physical_path)
    finally:
        cleanup_paths(futures_path, physical_path)

    return api_json(
        {
            "net_exposure_buckets": net_exposure.buckets,
            "summary": net_exposure.summary,
        }
    )


def _build_net_exposure_from_paths(futures_path, physical_path):
    try:
        futures_positions = load_futures_positions_csv(futures_path)
        physical_cargoes = load_physical_cargoes_csv(physical_path)
        futures_exposure = aggregate_futures_exposure(futures_positions)
        physical_exposure = aggregate_physical_exposure(physical_cargoes)
        return build_net_exposure(physical_exposure, futures_exposure)
    except FuturesPositionValidationError as exc:
        raise validation_error_response(exc.issues) from exc
    except PhysicalCargoValidationError as exc:
        raise validation_error_response(exc.issues) from exc
