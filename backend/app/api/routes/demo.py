from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Query

from backend.app.api.routes._utils import error_response
from backend.app.api.schemas.demo import (
    DemoRunResponse,
    DemoSampleFilesResponse,
)
from backend.app.api.schemas.errors import ERROR_RESPONSES, ErrorEnvelope
from backend.app.services.demo import (
    DemoStressScenario,
    get_demo_sample_files,
    run_sample_demo,
)


DEMO_ERROR_RESPONSES = {
    **ERROR_RESPONSES,
    404: {
        "model": ErrorEnvelope,
        "description": "Demo sample file or generated run artifact was not found.",
        "content": {
            "application/json": {
                "example": {
                    "detail": {
                        "error": "Demo sample file not found.",
                        "error_code": "DEMO_SAMPLE_FILE_NOT_FOUND",
                        "message": "Demo sample file not found.",
                        "details": None,
                    }
                }
            }
        },
    },
}

router = APIRouter(prefix="/demo")


@router.get(
    "/sample-files",
    response_model=DemoSampleFilesResponse,
    tags=["Demo"],
    summary="List synthetic demo sample files",
    description=(
        "Return the backend-owned synthetic CSV files used by FlowDeck demo "
        "mode. These files are sample-only and do not contain real trade or "
        "licensed market data."
    ),
    response_description="Synthetic demo sample file metadata.",
    responses=DEMO_ERROR_RESPONSES,
)
def sample_files():
    try:
        return get_demo_sample_files()
    except FileNotFoundError as exc:
        raise error_response(
            "Demo sample file not found.",
            status_code=404,
            error_code="DEMO_SAMPLE_FILE_NOT_FOUND",
        ) from exc


@router.post(
    "/run",
    response_model=DemoRunResponse,
    tags=["Demo"],
    summary="Run the synthetic sample demo workflow",
    description=(
        "Run FlowDeck's full backend-owned synthetic demo workflow without "
        "requiring CSV uploads. The service loads sample Brent/WTI market "
        "data, futures positions and physical cargoes, then builds curves, "
        "net exposure, hedge simulation, stress P&L, run metadata and an "
        "Excel report."
    ),
    response_description="Demo run summary with run detail and report links.",
    responses=DEMO_ERROR_RESPONSES,
)
def run_demo(
    target_hedge_ratio: Decimal = Query(
        default=Decimal("0.80"),
        description="Target hedge ratio for the sample hedge simulation.",
        examples=["0.80"],
    ),
    stress_scenario: DemoStressScenario = Query(
        default=DemoStressScenario.PARALLEL_DOWN_5,
        description="Supported predefined stress scenario for the demo run.",
        examples=["PARALLEL_DOWN_5"],
    ),
):
    try:
        return run_sample_demo(
            target_hedge_ratio=target_hedge_ratio,
            stress_scenario=stress_scenario,
        )
    except FileNotFoundError as exc:
        raise error_response(
            "Demo sample file not found.",
            status_code=404,
            error_code="DEMO_SAMPLE_FILE_NOT_FOUND",
        ) from exc
    except ValueError as exc:
        raise error_response(
            str(exc),
            status_code=400,
            error_code="DEMO_RUN_VALIDATION_ERROR",
        ) from exc
    except Exception as exc:
        raise error_response(
            "Demo run failed.",
            status_code=500,
            error_code="DEMO_RUN_FAILED",
        ) from exc
