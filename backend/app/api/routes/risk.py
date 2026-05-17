from fastapi import APIRouter, File, Form, UploadFile

from backend.app.api.schemas.errors import ERROR_RESPONSES
from backend.app.api.schemas.risk import StressPnlResponse
from backend.app.api.routes._utils import (
    api_json,
    cleanup_paths,
    error_response,
    save_upload_to_temp_csv,
)
from backend.app.api.routes.exposure import _build_net_exposure_from_paths
from backend.app.services.risk import (
    PredefinedStressScenario,
    StressScenarioValidationError,
    predefined_stress_request,
    run_stress_pnl,
)


router = APIRouter(prefix="/risk")


SUPPORTED_API_SCENARIOS = {
    PredefinedStressScenario.PARALLEL_DOWN_5,
    PredefinedStressScenario.PARALLEL_UP_5,
    PredefinedStressScenario.BRENT_DOWN_5,
    PredefinedStressScenario.BRENT_UP_5,
    PredefinedStressScenario.WTI_DOWN_5,
}


@router.post(
    "/stress",
    response_model=StressPnlResponse,
    tags=["Risk"],
    summary="Run stress P&L scenario",
    description=(
        "Build net exposure from uploaded futures and physical cargo CSVs, then "
        "run a supported predefined synthetic stress P&L scenario."
    ),
    response_description="Net exposure result, stressed bucket P&L and summary.",
    responses=ERROR_RESPONSES,
)
async def stress_pnl(
    futures_file: UploadFile = File(...),
    physical_file: UploadFile = File(...),
    scenario_name: str = Form(PredefinedStressScenario.PARALLEL_DOWN_5),
):
    scenario = _parse_scenario(scenario_name)
    futures_path = await save_upload_to_temp_csv(futures_file)
    physical_path = await save_upload_to_temp_csv(physical_file)
    try:
        net_exposure = _build_net_exposure_from_paths(futures_path, physical_path)
        stress_result = run_stress_pnl(
            predefined_stress_request(scenario, net_exposure.buckets)
        )
    except StressScenarioValidationError as exc:
        raise error_response(str(exc)) from exc
    finally:
        cleanup_paths(futures_path, physical_path)

    return api_json(
        {
            "net_exposure_result": net_exposure,
            "stress_bucket_results": stress_result.bucket_results,
            "stress_summary": stress_result.summary,
        }
    )


def _parse_scenario(scenario_name: str) -> PredefinedStressScenario:
    try:
        scenario = PredefinedStressScenario(scenario_name)
    except ValueError as exc:
        raise error_response(f"Unsupported stress scenario: {scenario_name}") from exc

    if scenario not in SUPPORTED_API_SCENARIOS:
        raise error_response(f"Unsupported stress scenario: {scenario_name}")
    return scenario
