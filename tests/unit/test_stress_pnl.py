from decimal import Decimal

import pytest

from backend.app.services.positions import NetExposureBucket
from backend.app.services.risk import (
    PnlDirection,
    PredefinedStressScenario,
    StressScenarioRequest,
    StressScenarioType,
    StressScenarioValidationError,
    predefined_stress_request,
    run_stress_pnl,
)


def test_long_exposure_loses_money_when_price_delta_is_negative() -> None:
    result = run_stress_pnl(
        _absolute_request(
            [_bucket("BRENT", "2026-09", "BOOK", "1000")],
            {"BRENT": Decimal("-5")},
        )
    )

    bucket = result.bucket_results[0]

    assert bucket.stress_pnl_usd == Decimal("-5000")
    assert bucket.pnl_direction == PnlDirection.LOSS


def test_long_exposure_gains_money_when_price_delta_is_positive() -> None:
    result = run_stress_pnl(
        _absolute_request(
            [_bucket("BRENT", "2026-09", "BOOK", "1000")],
            {"BRENT": Decimal("5")},
        )
    )

    bucket = result.bucket_results[0]

    assert bucket.stress_pnl_usd == Decimal("5000")
    assert bucket.pnl_direction == PnlDirection.GAIN


def test_short_exposure_gains_money_when_price_delta_is_negative() -> None:
    result = run_stress_pnl(
        _absolute_request(
            [_bucket("WTI", "2026-09", "BOOK", "-1000")],
            {"WTI": Decimal("-5")},
        )
    )

    bucket = result.bucket_results[0]

    assert bucket.stress_pnl_usd == Decimal("5000")
    assert bucket.pnl_direction == PnlDirection.GAIN


def test_short_exposure_loses_money_when_price_delta_is_positive() -> None:
    result = run_stress_pnl(
        _absolute_request(
            [_bucket("WTI", "2026-09", "BOOK", "-1000")],
            {"WTI": Decimal("5")},
        )
    )

    bucket = result.bucket_results[0]

    assert bucket.stress_pnl_usd == Decimal("-5000")
    assert bucket.pnl_direction == PnlDirection.LOSS


def test_zero_net_exposure_has_zero_pnl() -> None:
    result = run_stress_pnl(
        _absolute_request(
            [_bucket("BRENT", "2026-09", "BOOK", "0")],
            {"BRENT": Decimal("-5")},
        )
    )

    bucket = result.bucket_results[0]

    assert bucket.stress_pnl_usd == Decimal("0")
    assert bucket.pnl_direction == PnlDirection.FLAT


def test_index_absolute_shock_applies_correct_deltas() -> None:
    result = run_stress_pnl(
        _absolute_request(
            [
                _bucket("BRENT", "2026-09", "BOOK", "1000"),
                _bucket("WTI", "2026-09", "BOOK", "1000"),
            ],
            {"BRENT": Decimal("-5"), "WTI": Decimal("-3")},
        )
    )

    assert _result_for(result.bucket_results, "BRENT").price_delta_usd_per_bbl == Decimal(
        "-5"
    )
    assert _result_for(result.bucket_results, "WTI").price_delta_usd_per_bbl == Decimal(
        "-3"
    )


def test_percentage_shock_converts_percentage_to_usd_per_bbl() -> None:
    result = run_stress_pnl(
        StressScenarioRequest(
            exposure_buckets=(_bucket("BRENT", "2026-09", "BOOK", "1000"),),
            scenario_name="BRENT_DOWN_5_PERCENT",
            scenario_type=StressScenarioType.INDEX_PERCENTAGE_SHOCK,
            index_percentage_shocks={"BRENT": Decimal("-0.05")},
            current_prices_usd_per_bbl={"BRENT": Decimal("80")},
        )
    )

    bucket = result.bucket_results[0]

    assert bucket.price_delta_usd_per_bbl == Decimal("-4.00")
    assert bucket.stress_pnl_usd == Decimal("-4000.00")


def test_parallel_shift_applies_to_all_buckets() -> None:
    result = run_stress_pnl(
        StressScenarioRequest(
            exposure_buckets=(
                _bucket("BRENT", "2026-09", "BOOK", "1000"),
                _bucket("WTI", "2026-10", "BOOK", "-1000"),
            ),
            scenario_name="PARALLEL_DOWN_5",
            scenario_type=StressScenarioType.PARALLEL_SHIFT,
            parallel_shift_usd_per_bbl=Decimal("-5"),
        )
    )

    assert {bucket.price_delta_usd_per_bbl for bucket in result.bucket_results} == {
        Decimal("-5")
    }


def test_front_end_shock_applies_only_to_earliest_n_months() -> None:
    result = run_stress_pnl(
        StressScenarioRequest(
            exposure_buckets=(
                _bucket("BRENT", "2026-09", "BOOK", "1000"),
                _bucket("BRENT", "2026-10", "BOOK", "1000"),
                _bucket("BRENT", "2026-11", "BOOK", "1000"),
                _bucket("BRENT", "2026-12", "BOOK", "1000"),
            ),
            scenario_name="FRONT_TWO_DOWN_5",
            scenario_type=StressScenarioType.FRONT_END_SHOCK,
            front_end_month_count=2,
            front_end_shift_usd_per_bbl=Decimal("-5"),
        )
    )

    deltas_by_month = {
        bucket.exposure_month: bucket.price_delta_usd_per_bbl
        for bucket in result.bucket_results
    }

    assert deltas_by_month == {
        "2026-09": Decimal("-5"),
        "2026-10": Decimal("-5"),
        "2026-11": Decimal("0"),
        "2026-12": Decimal("0"),
    }


def test_basis_shock_applies_explicit_brent_wti_deltas_correctly() -> None:
    result = run_stress_pnl(
        predefined_stress_request(
            PredefinedStressScenario.BRENT_WTI_BASIS_WIDENS_2_WTI_FIXED,
            (
                _bucket("BRENT", "2026-09", "BOOK", "1000"),
                _bucket("WTI", "2026-09", "BOOK", "1000"),
            ),
        )
    )

    assert _result_for(result.bucket_results, "BRENT").price_delta_usd_per_bbl == Decimal(
        "2"
    )
    assert _result_for(result.bucket_results, "WTI").price_delta_usd_per_bbl == Decimal(
        "0"
    )


def test_portfolio_total_pnl_is_correct() -> None:
    result = run_stress_pnl(
        _absolute_request(
            [
                _bucket("BRENT", "2026-09", "BOOK", "1000"),
                _bucket("WTI", "2026-09", "BOOK", "-1000"),
                _bucket("BRENT", "2026-10", "BOOK", "0"),
            ],
            {"BRENT": Decimal("-5"), "WTI": Decimal("-3")},
        )
    )

    assert result.summary.total_stress_pnl_usd == Decimal("-2000")


def test_gain_loss_flat_bucket_counts_are_correct() -> None:
    result = run_stress_pnl(
        _absolute_request(
            [
                _bucket("BRENT", "2026-09", "BOOK", "1000"),
                _bucket("WTI", "2026-09", "BOOK", "-1000"),
                _bucket("BRENT", "2026-10", "BOOK", "0"),
            ],
            {"BRENT": Decimal("-5"), "WTI": Decimal("-3")},
        )
    )

    assert result.summary.number_of_gain_buckets == 1
    assert result.summary.number_of_loss_buckets == 1
    assert result.summary.number_of_flat_buckets == 1


def test_worst_and_best_bucket_are_correct() -> None:
    result = run_stress_pnl(
        _absolute_request(
            [
                _bucket("BRENT", "2026-09", "BOOK", "2000"),
                _bucket("WTI", "2026-09", "BOOK", "-1000"),
                _bucket("BRENT", "2026-10", "BOOK", "500"),
            ],
            {"BRENT": Decimal("-5"), "WTI": Decimal("-3")},
        )
    )

    assert result.summary.worst_bucket is not None
    assert result.summary.worst_bucket.label == "BRENT 2026-09 / BOOK"
    assert result.summary.worst_bucket.stress_pnl_usd == Decimal("-10000")
    assert result.summary.best_bucket is not None
    assert result.summary.best_bucket.label == "WTI 2026-09 / BOOK"
    assert result.summary.best_bucket.stress_pnl_usd == Decimal("3000")


def test_empty_input_returns_controlled_empty_result() -> None:
    result = run_stress_pnl(
        StressScenarioRequest(
            exposure_buckets=(),
            scenario_name="EMPTY_PARALLEL_DOWN_5",
            scenario_type=StressScenarioType.PARALLEL_SHIFT,
            parallel_shift_usd_per_bbl=Decimal("-5"),
        )
    )

    assert result.bucket_results == ()
    assert result.summary.total_stress_pnl_usd == Decimal("0")
    assert result.summary.total_gain_usd == Decimal("0")
    assert result.summary.total_loss_usd == Decimal("0")
    assert result.summary.worst_bucket is None
    assert result.summary.best_bucket is None
    assert result.summary.number_of_buckets == 0


def test_missing_current_price_for_percentage_shock_fails() -> None:
    request = StressScenarioRequest(
        exposure_buckets=(_bucket("BRENT", "2026-09", "BOOK", "1000"),),
        scenario_name="MISSING_PRICE",
        scenario_type=StressScenarioType.INDEX_PERCENTAGE_SHOCK,
        index_percentage_shocks={"BRENT": Decimal("-0.05")},
        current_prices_usd_per_bbl={"WTI": Decimal("75")},
    )

    with pytest.raises(StressScenarioValidationError, match="Missing current price"):
        run_stress_pnl(request)


def test_unsupported_hedge_index_fails_clearly() -> None:
    request = StressScenarioRequest(
        exposure_buckets=(_bucket("DUBAI", "2026-09", "BOOK", "1000"),),
        scenario_name="UNSUPPORTED_INDEX",
        scenario_type=StressScenarioType.PARALLEL_SHIFT,
        parallel_shift_usd_per_bbl=Decimal("-5"),
    )

    with pytest.raises(StressScenarioValidationError, match="Unsupported hedge_index"):
        run_stress_pnl(request)


def _absolute_request(
    buckets: list[NetExposureBucket],
    deltas: dict[str, Decimal],
) -> StressScenarioRequest:
    return StressScenarioRequest(
        exposure_buckets=tuple(buckets),
        scenario_name="INDEX_ABSOLUTE",
        scenario_type=StressScenarioType.INDEX_ABSOLUTE_SHOCK,
        index_price_deltas_usd_per_bbl=deltas,
    )


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


def _result_for(bucket_results, hedge_index: str):
    return next(bucket for bucket in bucket_results if bucket.hedge_index == hedge_index)

