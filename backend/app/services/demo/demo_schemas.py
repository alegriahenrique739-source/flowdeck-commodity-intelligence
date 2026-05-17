from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from backend.app.services.workflows import RunStatus


class DemoStressScenario(StrEnum):
    BRENT_DOWN_5 = "BRENT_DOWN_5"
    BRENT_UP_5 = "BRENT_UP_5"
    WTI_DOWN_5 = "WTI_DOWN_5"
    PARALLEL_DOWN_5 = "PARALLEL_DOWN_5"
    PARALLEL_UP_5 = "PARALLEL_UP_5"


class DemoSampleFiles(BaseModel):
    model_config = ConfigDict(frozen=True)

    market_data_file: str
    futures_positions_file: str
    physical_cargoes_file: str
    descriptions: dict[str, str]
    note: str


class DemoRunSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    number_of_curves: int
    number_of_net_exposure_buckets: int
    total_net_exposure_bbl: Decimal
    total_post_hedge_absolute_exposure_bbl: Decimal
    total_stress_pnl_usd: Decimal


class DemoRunResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    run_id: str
    status: RunStatus
    created_at: datetime
    completed_at: datetime
    summary: DemoRunSummary
    report_url: str
    run_detail_url: str
    assumptions: tuple[str, ...]
    excel_output_path: Path
    metadata_output_path: Path
