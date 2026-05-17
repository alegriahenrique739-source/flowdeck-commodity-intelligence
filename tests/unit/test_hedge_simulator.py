from decimal import Decimal

import pytest
from pydantic import ValidationError

from backend.app.services.hedging import (
    HedgeMode,
    HedgeRoundingMethod,
    HedgeSimulationRequest,
    HedgeTradeDirection,
    simulate_hedges,
)
from backend.app.services.positions import NetExposureBucket


def test_long_net_exposure_with_target_hedge_ratio_recommends_sell() -> None:
    result = simulate_hedges(
        HedgeSimulationRequest(
            exposure_buckets=(_bucket("BRENT", "2026-09", "CRUDE_BOOK", "600000"),),
            hedge_mode=HedgeMode.TARGET_HEDGE_RATIO,
            target_hedge_ratio=Decimal("0.80"),
        )
    )

    recommendation = result.recommendations[0]

    assert recommendation.recommended_direction == HedgeTradeDirection.SELL
    assert recommendation.target_residual_exposure_bbl == Decimal("120000.00")
    assert recommendation.required_hedge_exposure_bbl == Decimal("-480000.00")
    assert recommendation.recommended_lots_exact == Decimal("480.00")
    assert recommendation.recommended_lots_rounded == 480
    assert recommendation.recommendation_label == (
        "SELL 480 BRENT 2026-09 futures-equivalent lots for CRUDE_BOOK"
    )


def test_short_net_exposure_with_target_hedge_ratio_recommends_buy() -> None:
    result = simulate_hedges(
        HedgeSimulationRequest(
            exposure_buckets=(_bucket("WTI", "2026-09", "CRUDE_BOOK", "-500000"),),
            hedge_mode=HedgeMode.TARGET_HEDGE_RATIO,
            target_hedge_ratio=Decimal("0.50"),
        )
    )

    recommendation = result.recommendations[0]

    assert recommendation.recommended_direction == HedgeTradeDirection.BUY
    assert recommendation.target_residual_exposure_bbl == Decimal("-250000.00")
    assert recommendation.required_hedge_exposure_bbl == Decimal("250000.00")
    assert recommendation.recommended_lots_rounded == 250


def test_target_residual_exposure_works_for_long_exposure() -> None:
    result = simulate_hedges(
        HedgeSimulationRequest(
            exposure_buckets=(_bucket("BRENT", "2026-10", "BOOK", "350000"),),
            hedge_mode=HedgeMode.TARGET_RESIDUAL_EXPOSURE,
            target_residual_exposure_bbl=Decimal("100000"),
        )
    )

    recommendation = result.recommendations[0]

    assert recommendation.recommended_direction == HedgeTradeDirection.SELL
    assert recommendation.required_hedge_exposure_bbl == Decimal("-250000")
    assert recommendation.recommended_lots_rounded == 250


def test_target_residual_exposure_works_for_short_exposure() -> None:
    result = simulate_hedges(
        HedgeSimulationRequest(
            exposure_buckets=(_bucket("WTI", "2026-10", "BOOK", "-350000"),),
            hedge_mode=HedgeMode.TARGET_RESIDUAL_EXPOSURE,
            target_residual_exposure_bbl=Decimal("-100000"),
        )
    )

    recommendation = result.recommendations[0]

    assert recommendation.recommended_direction == HedgeTradeDirection.BUY
    assert recommendation.required_hedge_exposure_bbl == Decimal("250000")
    assert recommendation.recommended_lots_rounded == 250


def test_zero_net_exposure_returns_no_action() -> None:
    result = simulate_hedges(
        HedgeSimulationRequest(
            exposure_buckets=(_bucket("BRENT", "2026-09", "BOOK", "0"),),
            hedge_mode=HedgeMode.TARGET_HEDGE_RATIO,
            target_hedge_ratio=Decimal("1"),
        )
    )

    recommendation = result.recommendations[0]

    assert recommendation.recommended_direction == HedgeTradeDirection.NO_ACTION
    assert recommendation.recommended_lots_exact == Decimal("0")
    assert recommendation.recommended_lots_rounded == 0
    assert recommendation.rounded_hedge_exposure_bbl == Decimal("0")


def test_target_hedge_ratio_zero_means_no_hedge() -> None:
    result = simulate_hedges(
        HedgeSimulationRequest(
            exposure_buckets=(_bucket("BRENT", "2026-09", "BOOK", "250000"),),
            hedge_mode=HedgeMode.TARGET_HEDGE_RATIO,
            target_hedge_ratio=Decimal("0"),
        )
    )

    recommendation = result.recommendations[0]

    assert recommendation.target_residual_exposure_bbl == Decimal("250000")
    assert recommendation.required_hedge_exposure_bbl == Decimal("0")
    assert recommendation.recommended_direction == HedgeTradeDirection.NO_ACTION


def test_target_hedge_ratio_one_fully_hedges_to_zero_residual() -> None:
    result = simulate_hedges(
        HedgeSimulationRequest(
            exposure_buckets=(_bucket("BRENT", "2026-09", "BOOK", "250000"),),
            hedge_mode=HedgeMode.TARGET_HEDGE_RATIO,
            target_hedge_ratio=Decimal("1"),
        )
    )

    recommendation = result.recommendations[0]

    assert recommendation.target_residual_exposure_bbl == Decimal("0")
    assert recommendation.required_hedge_exposure_bbl == Decimal("-250000")
    assert recommendation.post_hedge_net_exposure_bbl == Decimal("0")


def test_invalid_target_hedge_ratio_fails() -> None:
    with pytest.raises(ValidationError, match="target_hedge_ratio"):
        HedgeSimulationRequest(
            exposure_buckets=(_bucket("BRENT", "2026-09", "BOOK", "250000"),),
            hedge_mode=HedgeMode.TARGET_HEDGE_RATIO,
            target_hedge_ratio=Decimal("1.20"),
        )


def test_missing_required_target_field_fails() -> None:
    with pytest.raises(ValidationError, match="target_residual_exposure_bbl"):
        HedgeSimulationRequest(
            exposure_buckets=(_bucket("BRENT", "2026-09", "BOOK", "250000"),),
            hedge_mode=HedgeMode.TARGET_RESIDUAL_EXPOSURE,
        )


def test_invalid_contract_size_fails() -> None:
    with pytest.raises(ValidationError, match="contract_size_bbl"):
        HedgeSimulationRequest(
            exposure_buckets=(_bucket("BRENT", "2026-09", "BOOK", "250000"),),
            hedge_mode=HedgeMode.TARGET_HEDGE_RATIO,
            target_hedge_ratio=Decimal("0.5"),
            contract_size_bbl=Decimal("0"),
        )


def test_nearest_rounding_works() -> None:
    recommendation = _simulate_single(
        net_exposure="2550",
        target_residual="0",
        rounding_method=HedgeRoundingMethod.NEAREST,
    )

    assert recommendation.recommended_lots_exact == Decimal("2.55")
    assert recommendation.recommended_lots_rounded == 3


def test_floor_rounding_works() -> None:
    recommendation = _simulate_single(
        net_exposure="2550",
        target_residual="0",
        rounding_method=HedgeRoundingMethod.FLOOR,
    )

    assert recommendation.recommended_lots_exact == Decimal("2.55")
    assert recommendation.recommended_lots_rounded == 2


def test_ceil_rounding_works() -> None:
    recommendation = _simulate_single(
        net_exposure="2100",
        target_residual="0",
        rounding_method=HedgeRoundingMethod.CEIL,
    )

    assert recommendation.recommended_lots_exact == Decimal("2.1")
    assert recommendation.recommended_lots_rounded == 3


def test_post_hedge_net_exposure_is_calculated_after_rounding() -> None:
    recommendation = _simulate_single(
        net_exposure="2550",
        target_residual="0",
        rounding_method=HedgeRoundingMethod.FLOOR,
    )

    assert recommendation.rounded_hedge_exposure_bbl == Decimal("-2000")
    assert recommendation.post_hedge_net_exposure_bbl == Decimal("550")
    assert recommendation.residual_difference_vs_target_bbl == Decimal("550")


def test_portfolio_summary_metrics_are_correct() -> None:
    result = simulate_hedges(
        HedgeSimulationRequest(
            exposure_buckets=(
                _bucket("BRENT", "2026-09", "BOOK", "600000"),
                _bucket("WTI", "2026-09", "BOOK", "-200000"),
                _bucket("BRENT", "2026-10", "BOOK", "0"),
            ),
            hedge_mode=HedgeMode.TARGET_HEDGE_RATIO,
            target_hedge_ratio=Decimal("0.50"),
        )
    )

    summary = result.summary

    assert summary.total_current_absolute_net_exposure_bbl == Decimal("800000")
    assert summary.total_post_hedge_absolute_net_exposure_bbl == Decimal("400000.00")
    assert summary.total_required_hedge_abs_bbl == Decimal("400000.00")
    assert summary.total_recommended_lots_abs == 400
    assert summary.number_of_recommendations == 2
    assert summary.number_of_no_action_buckets == 1
    assert summary.largest_required_hedge_bucket is not None
    assert summary.largest_required_hedge_bucket.required_hedge_abs_bbl == Decimal(
        "300000.00"
    )


def test_empty_input_returns_controlled_empty_result() -> None:
    result = simulate_hedges(
        HedgeSimulationRequest(
            exposure_buckets=(),
            hedge_mode=HedgeMode.TARGET_HEDGE_RATIO,
            target_hedge_ratio=Decimal("0.80"),
        )
    )

    assert result.recommendations == ()
    assert result.summary.total_current_absolute_net_exposure_bbl == Decimal("0")
    assert result.summary.total_post_hedge_absolute_net_exposure_bbl == Decimal("0")
    assert result.summary.total_required_hedge_abs_bbl == Decimal("0")
    assert result.summary.total_recommended_lots_abs == 0
    assert result.summary.number_of_recommendations == 0
    assert result.summary.number_of_no_action_buckets == 0
    assert result.summary.largest_required_hedge_bucket is None


def _simulate_single(
    net_exposure: str,
    target_residual: str,
    rounding_method: HedgeRoundingMethod,
):
    result = simulate_hedges(
        HedgeSimulationRequest(
            exposure_buckets=(_bucket("BRENT", "2026-09", "BOOK", net_exposure),),
            hedge_mode=HedgeMode.TARGET_RESIDUAL_EXPOSURE,
            target_residual_exposure_bbl=Decimal(target_residual),
            rounding_method=rounding_method,
        )
    )
    return result.recommendations[0]


def _bucket(
    hedge_index: str,
    exposure_month: str,
    book: str,
    net_exposure: str,
) -> NetExposureBucket:
    net = Decimal(net_exposure)
    long_exposure = net if net > 0 else Decimal("0")
    short_exposure = net if net < 0 else Decimal("0")
    return NetExposureBucket(
        hedge_index=hedge_index,
        exposure_month=exposure_month,
        book=book,
        label=f"{hedge_index} {exposure_month} / {book}",
        physical_exposure_bbl=net,
        paper_exposure_bbl=Decimal("0"),
        net_exposure_bbl=net,
        absolute_net_exposure_bbl=abs(net),
        gross_component_exposure_bbl=abs(net),
        gross_exposure_bbl=abs(net),
        long_exposure_bbl=long_exposure,
        short_exposure_bbl=short_exposure,
    )

