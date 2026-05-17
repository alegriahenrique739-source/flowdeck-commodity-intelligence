from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Iterable

from backend.app.services.positions.exposure import FuturesExposureBucket
from backend.app.services.positions.net_exposure_schemas import (
    LargestExposureBucket,
    NetExposureBucket,
    NetExposureResult,
    NetExposureSummary,
)
from backend.app.services.positions.physical_exposure import PhysicalExposureBucket


ZERO = Decimal("0")


def build_net_exposure(
    physical_exposures: Iterable[PhysicalExposureBucket],
    futures_exposures: Iterable[FuturesExposureBucket],
) -> NetExposureResult:
    physical_by_key: dict[tuple[str, str, str], Decimal] = defaultdict(lambda: ZERO)
    paper_by_key: dict[tuple[str, str, str], Decimal] = defaultdict(lambda: ZERO)

    for exposure in physical_exposures:
        key = (exposure.pricing_index, exposure.pricing_month, exposure.book)
        physical_by_key[key] += exposure.net_physical_exposure_bbl

    for exposure in futures_exposures:
        key = (exposure.commodity, exposure.contract_month, exposure.book)
        paper_by_key[key] += exposure.net_exposure_bbl

    keys = sorted(set(physical_by_key) | set(paper_by_key))
    buckets = tuple(
        _build_bucket(
            hedge_index=hedge_index,
            exposure_month=exposure_month,
            book=book,
            physical_exposure=physical_by_key[(hedge_index, exposure_month, book)],
            paper_exposure=paper_by_key[(hedge_index, exposure_month, book)],
        )
        for hedge_index, exposure_month, book in keys
    )

    return NetExposureResult(buckets=buckets, summary=_build_summary(buckets))


def _build_bucket(
    hedge_index: str,
    exposure_month: str,
    book: str,
    physical_exposure: Decimal,
    paper_exposure: Decimal,
) -> NetExposureBucket:
    net_exposure = physical_exposure + paper_exposure
    absolute_net_exposure = abs(net_exposure)
    gross_component_exposure = abs(physical_exposure) + abs(paper_exposure)
    long_exposure = net_exposure if net_exposure > 0 else ZERO
    short_exposure = net_exposure if net_exposure < 0 else ZERO

    return NetExposureBucket(
        hedge_index=hedge_index,
        exposure_month=exposure_month,
        book=book,
        label=f"{hedge_index} {exposure_month} / {book}",
        physical_exposure_bbl=physical_exposure,
        paper_exposure_bbl=paper_exposure,
        net_exposure_bbl=net_exposure,
        absolute_net_exposure_bbl=absolute_net_exposure,
        gross_component_exposure_bbl=gross_component_exposure,
        gross_exposure_bbl=absolute_net_exposure,
        long_exposure_bbl=long_exposure,
        short_exposure_bbl=short_exposure,
    )


def _build_summary(buckets: tuple[NetExposureBucket, ...]) -> NetExposureSummary:
    largest_long = _largest_long_bucket(buckets)
    largest_short = _largest_short_bucket(buckets)

    return NetExposureSummary(
        total_physical_exposure_bbl=sum(
            (bucket.physical_exposure_bbl for bucket in buckets), ZERO
        ),
        total_paper_exposure_bbl=sum(
            (bucket.paper_exposure_bbl for bucket in buckets), ZERO
        ),
        total_net_exposure_bbl=sum(
            (bucket.net_exposure_bbl for bucket in buckets), ZERO
        ),
        total_absolute_net_exposure_bbl=sum(
            (bucket.absolute_net_exposure_bbl for bucket in buckets), ZERO
        ),
        total_gross_component_exposure_bbl=sum(
            (bucket.gross_component_exposure_bbl for bucket in buckets), ZERO
        ),
        total_gross_exposure_bbl=sum(
            (bucket.absolute_net_exposure_bbl for bucket in buckets), ZERO
        ),
        total_long_exposure_bbl=sum(
            (bucket.long_exposure_bbl for bucket in buckets), ZERO
        ),
        total_short_exposure_bbl=sum(
            (bucket.short_exposure_bbl for bucket in buckets), ZERO
        ),
        number_of_exposure_buckets=len(buckets),
        largest_long_bucket=largest_long,
        largest_short_bucket=largest_short,
    )


def _largest_long_bucket(
    buckets: tuple[NetExposureBucket, ...]
) -> LargestExposureBucket | None:
    long_buckets = [bucket for bucket in buckets if bucket.net_exposure_bbl > 0]
    if not long_buckets:
        return None

    largest = max(long_buckets, key=lambda bucket: bucket.net_exposure_bbl)
    return LargestExposureBucket(
        label=largest.label,
        net_exposure_bbl=largest.net_exposure_bbl,
    )


def _largest_short_bucket(
    buckets: tuple[NetExposureBucket, ...]
) -> LargestExposureBucket | None:
    short_buckets = [bucket for bucket in buckets if bucket.net_exposure_bbl < 0]
    if not short_buckets:
        return None

    largest = min(short_buckets, key=lambda bucket: bucket.net_exposure_bbl)
    return LargestExposureBucket(
        label=largest.label,
        net_exposure_bbl=largest.net_exposure_bbl,
    )
