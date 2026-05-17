from __future__ import annotations

from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_UP

from backend.app.services.hedging.hedge_schemas import (
    HedgeMode,
    HedgeRecommendation,
    HedgeRoundingMethod,
    HedgeSimulationRequest,
    HedgeSimulationResult,
    HedgeSimulationSummary,
    HedgeTradeDirection,
    LargestRequiredHedgeBucket,
)
from backend.app.services.positions import NetExposureBucket


ZERO = Decimal("0")


def simulate_hedges(request: HedgeSimulationRequest) -> HedgeSimulationResult:
    recommendations = tuple(
        _simulate_bucket(bucket, request) for bucket in request.exposure_buckets
    )
    return HedgeSimulationResult(
        recommendations=recommendations,
        summary=_build_summary(recommendations),
    )


def _simulate_bucket(
    bucket: NetExposureBucket, request: HedgeSimulationRequest
) -> HedgeRecommendation:
    current_net = bucket.net_exposure_bbl
    target_residual = _target_residual_exposure(current_net, request)
    required_hedge = target_residual - current_net
    direction = _recommended_direction(required_hedge)
    lots_exact = abs(required_hedge) / request.contract_size_bbl
    lots_rounded = _round_lots(lots_exact, request.rounding_method)
    rounded_hedge = _signed_rounded_hedge_exposure(
        direction=direction,
        recommended_lots_rounded=lots_rounded,
        contract_size_bbl=request.contract_size_bbl,
    )
    post_hedge_net = current_net + rounded_hedge

    return HedgeRecommendation(
        hedge_index=bucket.hedge_index,
        exposure_month=bucket.exposure_month,
        book=bucket.book,
        current_net_exposure_bbl=current_net,
        target_residual_exposure_bbl=target_residual,
        required_hedge_exposure_bbl=required_hedge,
        contract_size_bbl=request.contract_size_bbl,
        recommended_direction=direction,
        recommended_lots_exact=lots_exact,
        recommended_lots_rounded=lots_rounded,
        rounded_hedge_exposure_bbl=rounded_hedge,
        post_hedge_net_exposure_bbl=post_hedge_net,
        residual_difference_vs_target_bbl=post_hedge_net - target_residual,
        recommendation_label=_recommendation_label(
            direction=direction,
            recommended_lots_rounded=lots_rounded,
            hedge_index=bucket.hedge_index,
            exposure_month=bucket.exposure_month,
            book=bucket.book,
        ),
    )


def _target_residual_exposure(
    current_net_exposure: Decimal, request: HedgeSimulationRequest
) -> Decimal:
    if request.hedge_mode == HedgeMode.TARGET_HEDGE_RATIO:
        return current_net_exposure * (Decimal("1") - request.target_hedge_ratio)

    return request.target_residual_exposure_bbl


def _recommended_direction(
    required_hedge_exposure: Decimal,
) -> HedgeTradeDirection:
    if required_hedge_exposure < 0:
        return HedgeTradeDirection.SELL
    if required_hedge_exposure > 0:
        return HedgeTradeDirection.BUY
    return HedgeTradeDirection.NO_ACTION


def _round_lots(lots_exact: Decimal, rounding_method: HedgeRoundingMethod) -> int:
    if rounding_method == HedgeRoundingMethod.NEAREST:
        rounded = lots_exact.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    elif rounding_method == HedgeRoundingMethod.FLOOR:
        rounded = lots_exact.quantize(Decimal("1"), rounding=ROUND_FLOOR)
    else:
        rounded = lots_exact.quantize(Decimal("1"), rounding=ROUND_CEILING)

    return int(rounded)


def _signed_rounded_hedge_exposure(
    direction: HedgeTradeDirection,
    recommended_lots_rounded: int,
    contract_size_bbl: Decimal,
) -> Decimal:
    rounded_abs_exposure = Decimal(recommended_lots_rounded) * contract_size_bbl
    if direction == HedgeTradeDirection.SELL:
        return -rounded_abs_exposure
    if direction == HedgeTradeDirection.BUY:
        return rounded_abs_exposure
    return ZERO


def _recommendation_label(
    direction: HedgeTradeDirection,
    recommended_lots_rounded: int,
    hedge_index: str,
    exposure_month: str,
    book: str,
) -> str:
    if direction == HedgeTradeDirection.NO_ACTION:
        return f"NO_ACTION for {hedge_index} {exposure_month} / {book}"

    return (
        f"{direction} {recommended_lots_rounded} {hedge_index} "
        f"{exposure_month} futures-equivalent lots for {book}"
    )


def _build_summary(
    recommendations: tuple[HedgeRecommendation, ...]
) -> HedgeSimulationSummary:
    largest_required = _largest_required_hedge_bucket(recommendations)

    return HedgeSimulationSummary(
        total_current_absolute_net_exposure_bbl=sum(
            (
                abs(recommendation.current_net_exposure_bbl)
                for recommendation in recommendations
            ),
            ZERO,
        ),
        total_post_hedge_absolute_net_exposure_bbl=sum(
            (
                abs(recommendation.post_hedge_net_exposure_bbl)
                for recommendation in recommendations
            ),
            ZERO,
        ),
        total_required_hedge_abs_bbl=sum(
            (
                abs(recommendation.required_hedge_exposure_bbl)
                for recommendation in recommendations
            ),
            ZERO,
        ),
        total_recommended_lots_abs=sum(
            recommendation.recommended_lots_rounded
            for recommendation in recommendations
        ),
        number_of_recommendations=sum(
            1
            for recommendation in recommendations
            if recommendation.recommended_direction != HedgeTradeDirection.NO_ACTION
        ),
        number_of_no_action_buckets=sum(
            1
            for recommendation in recommendations
            if recommendation.recommended_direction == HedgeTradeDirection.NO_ACTION
        ),
        largest_required_hedge_bucket=largest_required,
    )


def _largest_required_hedge_bucket(
    recommendations: tuple[HedgeRecommendation, ...]
) -> LargestRequiredHedgeBucket | None:
    actionable = [
        recommendation
        for recommendation in recommendations
        if recommendation.required_hedge_exposure_bbl != 0
    ]
    if not actionable:
        return None

    largest = max(
        actionable,
        key=lambda recommendation: abs(recommendation.required_hedge_exposure_bbl),
    )
    return LargestRequiredHedgeBucket(
        label=largest.recommendation_label,
        required_hedge_abs_bbl=abs(largest.required_hedge_exposure_bbl),
    )

