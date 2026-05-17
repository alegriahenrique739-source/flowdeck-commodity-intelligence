from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from secrets import token_hex

from pydantic import BaseModel, ConfigDict, Field


class RunType(str, Enum):
    DEMO_WORKFLOW = "DEMO_WORKFLOW"


class RunStatus(str, Enum):
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class RunInputFiles(BaseModel):
    model_config = ConfigDict(frozen=True)

    market_data_file: str | None = None
    futures_positions_file: str | None = None
    physical_cargoes_file: str | None = None


class RunOutputFiles(BaseModel):
    model_config = ConfigDict(frozen=True)

    excel_report_path: str | None = None


class RunSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    number_of_curves: int = 0
    number_of_net_exposure_buckets: int = 0
    total_net_exposure_bbl: Decimal = Decimal("0")
    total_post_hedge_absolute_exposure_bbl: Decimal = Decimal("0")
    total_stress_pnl_usd: Decimal = Decimal("0")


class RunMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)

    run_id: str
    run_type: RunType
    status: RunStatus
    created_at: datetime
    completed_at: datetime | None = None
    input_files: RunInputFiles = Field(default_factory=RunInputFiles)
    output_files: RunOutputFiles = Field(default_factory=RunOutputFiles)
    summary: RunSummary = Field(default_factory=RunSummary)
    errors: tuple[str, ...] = ()
    notes: str | None = None


def generate_run_id(now: datetime | None = None) -> str:
    timestamp = (now or datetime.now(UTC)).strftime("%Y%m%d-%H%M%S")
    suffix = token_hex(3).upper()
    return f"FD-RUN-{timestamp}-{suffix}"

