from __future__ import annotations

from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from backend.app.services.positions import NetExposureBucket


SUPPORTED_HEDGE_INDEXES = {"BRENT", "WTI"}


class StressScenarioType(StrEnum):
    INDEX_ABSOLUTE_SHOCK = "INDEX_ABSOLUTE_SHOCK"
    INDEX_PERCENTAGE_SHOCK = "INDEX_PERCENTAGE_SHOCK"
    PARALLEL_SHIFT = "PARALLEL_SHIFT"
    FRONT_END_SHOCK = "FRONT_END_SHOCK"
    BASIS_SHOCK = "BASIS_SHOCK"


class PnlDirection(StrEnum):
    GAIN = "GAIN"
    LOSS = "LOSS"
    FLAT = "FLAT"


class PredefinedStressScenario(StrEnum):
    BRENT_DOWN_5 = "BRENT_DOWN_5"
    BRENT_UP_5 = "BRENT_UP_5"
    WTI_DOWN_5 = "WTI_DOWN_5"
    PARALLEL_DOWN_5 = "PARALLEL_DOWN_5"
    PARALLEL_UP_5 = "PARALLEL_UP_5"
    BRENT_WTI_BASIS_WIDENS_2_WTI_FIXED = (
        "BRENT_WTI_BASIS_WIDENS_2_WTI_FIXED"
    )
    FRONT_END_DOWN_5 = "FRONT_END_DOWN_5"


class StressScenarioValidationError(ValueError):
    pass


class StressScenarioRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    exposure_buckets: tuple[NetExposureBucket, ...] = ()
    scenario_name: str
    scenario_type: StressScenarioType
    index_price_deltas_usd_per_bbl: dict[str, Decimal] | None = None
    index_percentage_shocks: dict[str, Decimal] | None = None
    current_prices_usd_per_bbl: dict[str, Decimal] | None = None
    parallel_shift_usd_per_bbl: Decimal | None = None
    front_end_month_count: int = Field(default=3, ge=1)
    front_end_shift_usd_per_bbl: Decimal | None = None


class StressBucketResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    hedge_index: str
    exposure_month: str
    book: str
    net_exposure_bbl: Decimal
    price_delta_usd_per_bbl: Decimal
    stress_pnl_usd: Decimal
    pnl_direction: PnlDirection
    scenario_name: str
    label: str


class StressPnlSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    scenario_name: str
    scenario_type: StressScenarioType
    total_stress_pnl_usd: Decimal
    total_gain_usd: Decimal
    total_loss_usd: Decimal
    worst_bucket: StressBucketResult | None
    best_bucket: StressBucketResult | None
    number_of_buckets: int
    number_of_gain_buckets: int
    number_of_loss_buckets: int
    number_of_flat_buckets: int


class StressPnlResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    bucket_results: tuple[StressBucketResult, ...]
    summary: StressPnlSummary

