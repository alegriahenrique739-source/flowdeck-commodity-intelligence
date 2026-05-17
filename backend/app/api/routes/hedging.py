from decimal import Decimal

from fastapi import APIRouter, File, Form, UploadFile

from backend.app.api.schemas.errors import ERROR_RESPONSES
from backend.app.api.schemas.hedging import HedgeSimulationResponse
from backend.app.api.routes._utils import api_json, cleanup_paths, save_upload_to_temp_csv
from backend.app.api.routes.exposure import _build_net_exposure_from_paths
from backend.app.services.hedging import (
    HedgeMode,
    HedgeSimulationRequest,
    simulate_hedges,
)


router = APIRouter(prefix="/hedging")


@router.post(
    "/simulate",
    response_model=HedgeSimulationResponse,
    tags=["Hedging"],
    summary="Simulate deterministic hedge recommendations",
    description=(
        "Build net exposure from uploaded futures and physical cargo CSVs, then "
        "simulate offsetting futures-equivalent hedge recommendations using a "
        "target hedge ratio."
    ),
    response_description="Net exposure result, hedge recommendations and summary.",
    responses=ERROR_RESPONSES,
)
async def simulate_hedging(
    futures_file: UploadFile = File(...),
    physical_file: UploadFile = File(...),
    target_hedge_ratio: Decimal = Form(Decimal("0.80")),
    contract_size_bbl: Decimal = Form(Decimal("1000")),
):
    futures_path = await save_upload_to_temp_csv(futures_file)
    physical_path = await save_upload_to_temp_csv(physical_file)
    try:
        net_exposure = _build_net_exposure_from_paths(futures_path, physical_path)
        hedge_result = simulate_hedges(
            HedgeSimulationRequest(
                exposure_buckets=net_exposure.buckets,
                hedge_mode=HedgeMode.TARGET_HEDGE_RATIO,
                target_hedge_ratio=target_hedge_ratio,
                contract_size_bbl=contract_size_bbl,
            )
        )
    finally:
        cleanup_paths(futures_path, physical_path)

    return api_json(
        {
            "net_exposure_result": net_exposure,
            "hedge_recommendations": hedge_result.recommendations,
            "hedge_summary": hedge_result.summary,
        }
    )
