from __future__ import annotations

import re

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import FileResponse

from backend.app.api.routes._utils import error_response
from backend.app.api.schemas.errors import ERROR_RESPONSES, ErrorEnvelope
from backend.app.api.schemas.runs import RunsListResponse
from backend.app.services.workflows import (
    LocalRunRegistry,
    RunMetadata,
    RunStatus,
    RunType,
)

RUN_ID_PATTERN = re.compile(r"^FD-RUN-\d{8}-\d{6}-[A-F0-9]{6}$")

RUN_ERROR_RESPONSES = {
    **ERROR_RESPONSES,
    404: {
        "model": ErrorEnvelope,
        "description": "Run metadata was not found.",
        "content": {
            "application/json": {
                "example": {
                    "detail": {
                        "error": "Run metadata not found.",
                        "error_code": "RUN_NOT_FOUND",
                        "message": "Run metadata not found.",
                        "details": {"run_id": "FD-RUN-20260512-235500-ABC123"},
                    }
                }
            }
        },
    },
}

RUN_REPORT_RESPONSES = {
    200: {
        "description": "Excel report file associated with the run.",
        "content": {
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {
                "schema": {"type": "string", "format": "binary"}
            }
        },
    },
    **RUN_ERROR_RESPONSES,
}

router = APIRouter(prefix="/runs")


def get_run_registry(request: Request) -> LocalRunRegistry:
    return request.app.state.run_registry or LocalRunRegistry()


@router.get(
    "",
    response_model=RunsListResponse,
    tags=["Runs"],
    summary="List local workflow runs",
    description=(
        "Return recent local workflow run metadata records from the file-based "
        "runs directory. Invalid metadata files are ignored."
    ),
    response_description="Recent local workflow run metadata records.",
    responses=ERROR_RESPONSES,
)
def list_runs(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of run records to return after filtering.",
    ),
    status: RunStatus | None = Query(
        default=None,
        description="Optional run status filter: SUCCESS, FAILED, or RUNNING.",
    ),
    run_type: RunType | None = Query(
        default=None,
        description="Optional run type filter. Currently supports DEMO_WORKFLOW.",
    ),
    registry: LocalRunRegistry = Depends(get_run_registry),
):
    runs = registry.list_metadata()
    if status is not None:
        runs = [run for run in runs if run.status == status]
    if run_type is not None:
        runs = [run for run in runs if run.run_type == run_type]
    runs = runs[:limit]
    return {"runs": runs, "count": len(runs)}


@router.get(
    "/{run_id}",
    response_model=RunMetadata,
    tags=["Runs"],
    summary="Get local workflow run metadata",
    description=(
        "Return the full local metadata record for a single run ID. The run ID "
        "is validated before any file lookup to prevent path traversal."
    ),
    response_description="Full local workflow run metadata record.",
    responses=RUN_ERROR_RESPONSES,
)
def get_run(
    run_id: str,
    registry: LocalRunRegistry = Depends(get_run_registry),
):
    if not RUN_ID_PATTERN.fullmatch(run_id):
        raise error_response(
            "Invalid run_id.",
            status_code=400,
            error_code="INVALID_RUN_ID",
        )

    try:
        return registry.read_metadata(run_id)
    except (OSError, ValueError) as exc:
        raise error_response(
            "Run metadata not found.",
            status_code=404,
            error_code="RUN_NOT_FOUND",
        ) from exc


@router.get(
    "/{run_id}/report",
    tags=["Runs"],
    summary="Download local workflow run report",
    description=(
        "Return the Excel workbook associated with a local workflow run. The "
        "run ID is validated and the resolved report path must remain inside "
        "the expected run folder."
    ),
    response_description="Excel report file associated with the run.",
    responses=RUN_REPORT_RESPONSES,
)
def download_run_report(
    run_id: str,
    registry: LocalRunRegistry = Depends(get_run_registry),
):
    if not RUN_ID_PATTERN.fullmatch(run_id):
        raise error_response(
            "Invalid run_id.",
            status_code=400,
            error_code="INVALID_RUN_ID",
        )

    try:
        metadata = registry.read_metadata(run_id)
    except (OSError, ValueError) as exc:
        raise error_response(
            "Run metadata not found.",
            status_code=404,
            error_code="RUN_NOT_FOUND",
        ) from exc

    if not metadata.output_files.excel_report_path:
        raise error_response(
            "Run report not found.",
            status_code=404,
            error_code="RUN_REPORT_NOT_FOUND",
        )

    try:
        report_path = registry.validate_report_path_for_run(
            run_id, metadata.output_files.excel_report_path
        )
    except OSError as exc:
        raise error_response(
            "Run report not found.",
            status_code=404,
            error_code="RUN_REPORT_NOT_FOUND",
        ) from exc
    except ValueError as exc:
        raise error_response(
            "Run report path is invalid.",
            status_code=400,
            error_code="INVALID_RUN_REPORT_PATH",
        ) from exc

    return FileResponse(
        path=report_path,
        filename=f"flowdeck_report_{run_id}.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
