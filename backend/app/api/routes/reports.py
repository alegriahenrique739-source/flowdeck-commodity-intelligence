from decimal import Decimal
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, File, Form, UploadFile
from fastapi.responses import FileResponse

from backend.app.api.schemas.errors import ERROR_RESPONSES
from backend.app.api.schemas.reports import EXCEL_REPORT_RESPONSES
from backend.app.api.routes._utils import (
    API_TMP_DIR,
    cleanup_paths,
    save_upload_to_temp_csv,
    validation_error_response,
)
from backend.app.services.curves import build_forward_curves
from backend.app.services.hedging import (
    HedgeMode,
    HedgeSimulationRequest,
    simulate_hedges,
)
from backend.app.services.market_data import (
    MarketDataValidationError,
    load_market_data_csv,
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
from backend.app.services.reports import ExcelReportInput, build_excel_report
from backend.app.services.risk import (
    PredefinedStressScenario,
    predefined_stress_request,
    run_stress_pnl,
)


router = APIRouter(prefix="/reports")


@router.post(
    "/excel",
    tags=["Reports"],
    summary="Generate Excel report",
    description=(
        "Generate a temporary professional FlowDeck Excel workbook from uploaded "
        "market data, futures positions and physical cargo CSV files. The API "
        "returns the workbook as a downloadable .xlsx file."
    ),
    response_description="FlowDeck Excel workbook file.",
    responses={**EXCEL_REPORT_RESPONSES, **ERROR_RESPONSES},
)
async def build_excel_report_endpoint(
    background_tasks: BackgroundTasks,
    market_data_file: UploadFile = File(...),
    futures_file: UploadFile = File(...),
    physical_file: UploadFile = File(...),
    target_hedge_ratio: Decimal = Form(Decimal("0.80")),
    stress_scenario: str = Form(PredefinedStressScenario.PARALLEL_DOWN_5),
):
    market_path = await save_upload_to_temp_csv(market_data_file)
    futures_path = await save_upload_to_temp_csv(futures_file)
    physical_path = await save_upload_to_temp_csv(physical_file)
    output_path = API_TMP_DIR / f"flowdeck_report_{uuid4().hex}.xlsx"

    try:
        market_data_rows = load_market_data_csv(market_path)
        curves = build_forward_curves(market_data_rows)
        futures_positions = load_futures_positions_csv(futures_path)
        physical_cargoes = load_physical_cargoes_csv(physical_path)
        futures_exposure = aggregate_futures_exposure(futures_positions)
        physical_exposure = aggregate_physical_exposure(physical_cargoes)
        net_exposure = build_net_exposure(physical_exposure, futures_exposure)
        hedge_result = simulate_hedges(
            HedgeSimulationRequest(
                exposure_buckets=net_exposure.buckets,
                hedge_mode=HedgeMode.TARGET_HEDGE_RATIO,
                target_hedge_ratio=target_hedge_ratio,
            )
        )
        stress_result = run_stress_pnl(
            predefined_stress_request(
                PredefinedStressScenario(stress_scenario),
                net_exposure.buckets,
            )
        )
        build_excel_report(
            ExcelReportInput(
                market_data_rows=tuple(market_data_rows),
                curve_summaries=tuple(curves),
                futures_positions=tuple(futures_positions),
                physical_cargoes=tuple(physical_cargoes),
                net_exposure_result=net_exposure,
                hedge_simulation_result=hedge_result,
                stress_result=stress_result,
            ),
            output_path,
        )
    except MarketDataValidationError as exc:
        cleanup_paths(output_path)
        raise validation_error_response(exc.issues) from exc
    except FuturesPositionValidationError as exc:
        cleanup_paths(output_path)
        raise validation_error_response(exc.issues) from exc
    except PhysicalCargoValidationError as exc:
        cleanup_paths(output_path)
        raise validation_error_response(exc.issues) from exc
    except ValueError as exc:
        cleanup_paths(output_path)
        from backend.app.api.routes._utils import error_response

        raise error_response(str(exc)) from exc
    finally:
        cleanup_paths(market_path, futures_path, physical_path)

    background_tasks.add_task(cleanup_paths, output_path)
    return FileResponse(
        path=output_path,
        filename="flowdeck_report.xlsx",
        media_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
        background=background_tasks,
    )
