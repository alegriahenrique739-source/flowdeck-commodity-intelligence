from __future__ import annotations

from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.app.services.positions import NetExposureBucket


class HedgeMode(StrEnum):
    TARGET_HEDGE_RATIO = "TARGET_HEDGE_RATIO"
    TARGET_RESIDUAL_EXPOSURE = "TARGET_RESIDUAL_EXPOSURE"


class HedgeRoundingMethod(StrEnum):
    NEAREST = "NEAREST"
    FLOOR = "FLOOR"
    CEIL = "CEIL"


class HedgeTradeDirection(StrEnum):
    BUY = "BUY"
    SELL = "SELL"
    NO_ACTION = "NO_ACTION"


class HedgeSimulationRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    exposure_buckets: tuple[NetExposureBucket, ...] = ()
    hedge_mode: HedgeMode
    target_hedge_ratio: Decimal | None = None
    target_residual_exposure_bbl: Decimal | None = None
    contract_size_bbl: Decimal = Field(default=Decimal("1000"), gt=0)
    rounding_method: HedgeRoundingMethod = HedgeRoundingMethod.NEAREST

    @model_validator(mode="after")
    def validate_mode_targets(self) -> HedgeSimulationRequest:
        if self.hedge_mode == HedgeMode.TARGET_HEDGE_RATIO:
            if self.target_hedge_ratio is None:
                raise ValueError(
                    "target_hedge_ratio is required for TARGET_HEDGE_RATIO mode"
                )
            if self.target_hedge_ratio < 0 or self.target_hedge_ratio > 1:
                raise ValueError("target_hedge_ratio must be between 0 and 1")

        if self.hedge_mode == HedgeMode.TARGET_RESIDUAL_EXPOSURE:
            if self.target_residual_exposure_bbl is None:
                raise ValueError(
                    "target_residual_exposure_bbl is required for "
                    "TARGET_RESIDUAL_EXPOSURE mode"
                )

        return self


class HedgeRecommendation(BaseModel):
    model_config = ConfigDict(frozen=True)

    hedge_index: str
    exposure_month: str
    book: str
    current_net_exposure_bbl: Decimal
    target_residual_exposure_bbl: Decimal
    required_hedge_exposure_bbl: Decimal
    contract_size_bbl: Decimal
    recommended_direction: HedgeTradeDirection
    recommended_lots_exact: Decimal
    recommended_lots_rounded: int
    rounded_hedge_exposure_bbl: Decimal
    post_hedge_net_exposure_bbl: Decimal
    residual_difference_vs_target_bbl: Decimal
    recommendation_label: str


class LargestRequiredHedgeBucket(BaseModel):
    model_config = ConfigDict(frozen=True)

    label: str
    required_hedge_abs_bbl: Decimal


class HedgeSimulationSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    total_current_absolute_net_exposure_bbl: Decimal
    total_post_hedge_absolute_net_exposure_bbl: Decimal
    total_required_hedge_abs_bbl: Decimal
    total_recommended_lots_abs: int
    number_of_recommendations: int
    number_of_no_action_buckets: int
    largest_required_hedge_bucket: LargestRequiredHedgeBucket | None


class HedgeSimulationResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    recommendations: tuple[HedgeRecommendation, ...]
    summary: HedgeSimulationSummary

