from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from backend.app.services.positions import NetExposureBucket
from backend.app.services.risk.stress_schemas import (
    PnlDirection,
    PredefinedStressScenario,
    SUPPORTED_HEDGE_INDEXES,
    StressBucketResult,
    StressPnlResult,
    StressPnlSummary,
    StressScenarioRequest,
    StressScenarioType,
    StressScenarioValidationError,
)


ZERO = Decimal("0")


def run_stress_pnl(request: StressScenarioRequest) -> StressPnlResult:
    _validate_request(request)
    bucket_results = tuple(
        _stress_bucket(
            bucket=bucket,
            price_delta=_price_delta_for_bucket(bucket, request),
            scenario_name=request.scenario_name,
        )
        for bucket in request.exposure_buckets
    )
    return StressPnlResult(
        bucket_results=bucket_results,
        summary=_build_summary(
            bucket_results=bucket_results,
            scenario_name=request.scenario_name,
            scenario_type=request.scenario_type,
        ),
    )


def predefined_stress_request(
    scenario: PredefinedStressScenario,
    exposure_buckets: tuple[NetExposureBucket, ...],
) -> StressScenarioRequest:
    if scenario == PredefinedStressScenario.BRENT_DOWN_5:
        return StressScenarioRequest(
            exposure_buckets=exposure_buckets,
            scenario_name=scenario,
            scenario_type=StressScenarioType.INDEX_ABSOLUTE_SHOCK,
            index_price_deltas_usd_per_bbl={"BRENT": Decimal("-5")},
        )
    if scenario == PredefinedStressScenario.BRENT_UP_5:
        return StressScenarioRequest(
            exposure_buckets=exposure_buckets,
            scenario_name=scenario,
            scenario_type=StressScenarioType.INDEX_ABSOLUTE_SHOCK,
            index_price_deltas_usd_per_bbl={"BRENT": Decimal("5")},
        )
    if scenario == PredefinedStressScenario.WTI_DOWN_5:
        return StressScenarioRequest(
            exposure_buckets=exposure_buckets,
            scenario_name=scenario,
            scenario_type=StressScenarioType.INDEX_ABSOLUTE_SHOCK,
            index_price_deltas_usd_per_bbl={"WTI": Decimal("-5")},
        )
    if scenario == PredefinedStressScenario.PARALLEL_DOWN_5:
        return StressScenarioRequest(
            exposure_buckets=exposure_buckets,
            scenario_name=scenario,
            scenario_type=StressScenarioType.PARALLEL_SHIFT,
            parallel_shift_usd_per_bbl=Decimal("-5"),
        )
    if scenario == PredefinedStressScenario.PARALLEL_UP_5:
        return StressScenarioRequest(
            exposure_buckets=exposure_buckets,
            scenario_name=scenario,
            scenario_type=StressScenarioType.PARALLEL_SHIFT,
            parallel_shift_usd_per_bbl=Decimal("5"),
        )
    if scenario == PredefinedStressScenario.BRENT_WTI_BASIS_WIDENS_2_WTI_FIXED:
        return StressScenarioRequest(
            exposure_buckets=exposure_buckets,
            scenario_name=scenario,
            scenario_type=StressScenarioType.BASIS_SHOCK,
            index_price_deltas_usd_per_bbl={
                "BRENT": Decimal("2"),
                "WTI": Decimal("0"),
            },
        )

    return StressScenarioRequest(
        exposure_buckets=exposure_buckets,
        scenario_name=scenario,
        scenario_type=StressScenarioType.FRONT_END_SHOCK,
        front_end_shift_usd_per_bbl=Decimal("-5"),
    )


def _validate_request(request: StressScenarioRequest) -> None:
    unsupported_indexes = sorted(
        {
            bucket.hedge_index
            for bucket in request.exposure_buckets
            if bucket.hedge_index not in SUPPORTED_HEDGE_INDEXES
        }
    )
    if unsupported_indexes:
        raise StressScenarioValidationError(
            "Unsupported hedge_index value(s): " + ", ".join(unsupported_indexes)
        )

    if request.scenario_type in {
        StressScenarioType.INDEX_ABSOLUTE_SHOCK,
        StressScenarioType.BASIS_SHOCK,
    }:
        if request.index_price_deltas_usd_per_bbl is None:
            raise StressScenarioValidationError(
                "index_price_deltas_usd_per_bbl is required for "
                f"{request.scenario_type} scenarios"
            )
        _validate_index_map(
            request.index_price_deltas_usd_per_bbl,
            "index_price_deltas_usd_per_bbl",
        )

    if request.scenario_type == StressScenarioType.INDEX_PERCENTAGE_SHOCK:
        if request.index_percentage_shocks is None:
            raise StressScenarioValidationError(
                "index_percentage_shocks is required for INDEX_PERCENTAGE_SHOCK"
            )
        if request.current_prices_usd_per_bbl is None:
            raise StressScenarioValidationError(
                "current_prices_usd_per_bbl is required for INDEX_PERCENTAGE_SHOCK"
            )
        _validate_index_map(
            request.index_percentage_shocks,
            "index_percentage_shocks",
        )
        _validate_index_map(
            request.current_prices_usd_per_bbl,
            "current_prices_usd_per_bbl",
        )

    if request.scenario_type == StressScenarioType.PARALLEL_SHIFT:
        if request.parallel_shift_usd_per_bbl is None:
            raise StressScenarioValidationError(
                "parallel_shift_usd_per_bbl is required for PARALLEL_SHIFT"
            )

    if request.scenario_type == StressScenarioType.FRONT_END_SHOCK:
        if request.front_end_shift_usd_per_bbl is None:
            raise StressScenarioValidationError(
                "front_end_shift_usd_per_bbl is required for FRONT_END_SHOCK"
            )
        _validate_front_end_months_are_sortable(request.exposure_buckets)


def _validate_index_map(index_map: dict[str, Decimal], field_name: str) -> None:
    unsupported = sorted(
        index for index in index_map if index not in SUPPORTED_HEDGE_INDEXES
    )
    if unsupported:
        raise StressScenarioValidationError(
            f"{field_name} contains unsupported hedge index value(s): "
            + ", ".join(unsupported)
        )


def _validate_front_end_months_are_sortable(
    buckets: tuple[NetExposureBucket, ...]
) -> None:
    for bucket in buckets:
        _month_sort_key(bucket.exposure_month)


def _price_delta_for_bucket(
    bucket: NetExposureBucket, request: StressScenarioRequest
) -> Decimal:
    if request.scenario_type in {
        StressScenarioType.INDEX_ABSOLUTE_SHOCK,
        StressScenarioType.BASIS_SHOCK,
    }:
        return request.index_price_deltas_usd_per_bbl.get(bucket.hedge_index, ZERO)

    if request.scenario_type == StressScenarioType.INDEX_PERCENTAGE_SHOCK:
        percentage_shock = request.index_percentage_shocks.get(
            bucket.hedge_index, ZERO
        )
        current_price = request.current_prices_usd_per_bbl.get(bucket.hedge_index)
        if current_price is None:
            raise StressScenarioValidationError(
                f"Missing current price for {bucket.hedge_index}."
            )
        return current_price * percentage_shock

    if request.scenario_type == StressScenarioType.PARALLEL_SHIFT:
        return request.parallel_shift_usd_per_bbl

    front_months = _front_end_months_by_index(
        request.exposure_buckets, request.front_end_month_count
    )
    if bucket.exposure_month in front_months[bucket.hedge_index]:
        return request.front_end_shift_usd_per_bbl
    return ZERO


def _front_end_months_by_index(
    buckets: tuple[NetExposureBucket, ...], front_end_month_count: int
) -> dict[str, set[str]]:
    months_by_index: dict[str, set[str]] = defaultdict(set)
    for bucket in buckets:
        months_by_index[bucket.hedge_index].add(bucket.exposure_month)

    return {
        hedge_index: set(
            sorted(months, key=_month_sort_key)[:front_end_month_count]
        )
        for hedge_index, months in months_by_index.items()
    }


def _month_sort_key(exposure_month: str) -> tuple[int, int]:
    parts = exposure_month.split("-")
    if len(parts) != 2:
        raise StressScenarioValidationError(
            f"Invalid exposure_month '{exposure_month}'; expected YYYY-MM."
        )

    try:
        year = int(parts[0])
        month = int(parts[1])
    except ValueError as exc:
        raise StressScenarioValidationError(
            f"Invalid exposure_month '{exposure_month}'; expected YYYY-MM."
        ) from exc

    if month < 1 or month > 12:
        raise StressScenarioValidationError(
            f"Invalid exposure_month '{exposure_month}'; month must be 01 through 12."
        )

    return (year, month)


def _stress_bucket(
    bucket: NetExposureBucket,
    price_delta: Decimal,
    scenario_name: str,
) -> StressBucketResult:
    stress_pnl = bucket.net_exposure_bbl * price_delta
    return StressBucketResult(
        hedge_index=bucket.hedge_index,
        exposure_month=bucket.exposure_month,
        book=bucket.book,
        net_exposure_bbl=bucket.net_exposure_bbl,
        price_delta_usd_per_bbl=price_delta,
        stress_pnl_usd=stress_pnl,
        pnl_direction=_pnl_direction(stress_pnl),
        scenario_name=scenario_name,
        label=f"{bucket.hedge_index} {bucket.exposure_month} / {bucket.book}",
    )


def _pnl_direction(stress_pnl: Decimal) -> PnlDirection:
    if stress_pnl > 0:
        return PnlDirection.GAIN
    if stress_pnl < 0:
        return PnlDirection.LOSS
    return PnlDirection.FLAT


def _build_summary(
    bucket_results: tuple[StressBucketResult, ...],
    scenario_name: str,
    scenario_type: StressScenarioType,
) -> StressPnlSummary:
    gain_buckets = [
        bucket for bucket in bucket_results if bucket.pnl_direction == PnlDirection.GAIN
    ]
    loss_buckets = [
        bucket for bucket in bucket_results if bucket.pnl_direction == PnlDirection.LOSS
    ]
    flat_buckets = [
        bucket for bucket in bucket_results if bucket.pnl_direction == PnlDirection.FLAT
    ]

    return StressPnlSummary(
        scenario_name=scenario_name,
        scenario_type=scenario_type,
        total_stress_pnl_usd=sum(
            (bucket.stress_pnl_usd for bucket in bucket_results), ZERO
        ),
        total_gain_usd=sum(
            (bucket.stress_pnl_usd for bucket in gain_buckets), ZERO
        ),
        total_loss_usd=sum(
            (bucket.stress_pnl_usd for bucket in loss_buckets), ZERO
        ),
        worst_bucket=min(
            bucket_results, key=lambda bucket: bucket.stress_pnl_usd, default=None
        ),
        best_bucket=max(
            bucket_results, key=lambda bucket: bucket.stress_pnl_usd, default=None
        ),
        number_of_buckets=len(bucket_results),
        number_of_gain_buckets=len(gain_buckets),
        number_of_loss_buckets=len(loss_buckets),
        number_of_flat_buckets=len(flat_buckets),
    )

