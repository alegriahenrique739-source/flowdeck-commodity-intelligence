from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Iterable

from pydantic import BaseModel, ConfigDict

from backend.app.services.positions.futures_schemas import (
    FuturesDirection,
    FuturesPositionRow,
)


class FuturesExposureBucket(BaseModel):
    model_config = ConfigDict(frozen=True)

    commodity: str
    contract_month: str
    book: str
    gross_exposure_bbl: Decimal
    net_exposure_bbl: Decimal
    long_exposure_bbl: Decimal
    short_exposure_bbl: Decimal


def signed_exposure_bbl(position: FuturesPositionRow) -> Decimal:
    sign = Decimal("1") if position.direction == FuturesDirection.BUY else Decimal("-1")
    return position.lots * position.contract_size * sign


def aggregate_futures_exposure(
    positions: Iterable[FuturesPositionRow],
) -> list[FuturesExposureBucket]:
    grouped: dict[tuple[str, str, str], list[Decimal]] = defaultdict(list)

    for position in positions:
        key = (position.commodity, position.contract_month, position.book)
        grouped[key].append(signed_exposure_bbl(position))

    buckets: list[FuturesExposureBucket] = []
    for (commodity, contract_month, book), exposures in grouped.items():
        long_exposure = sum(
            (exposure for exposure in exposures if exposure > 0), Decimal("0")
        )
        short_exposure = sum(
            (exposure for exposure in exposures if exposure < 0), Decimal("0")
        )
        net_exposure = sum(exposures, Decimal("0"))
        gross_exposure = long_exposure + abs(short_exposure)

        buckets.append(
            FuturesExposureBucket(
                commodity=commodity,
                contract_month=contract_month,
                book=book,
                gross_exposure_bbl=gross_exposure,
                net_exposure_bbl=net_exposure,
                long_exposure_bbl=long_exposure,
                short_exposure_bbl=short_exposure,
            )
        )

    return sorted(
        buckets,
        key=lambda bucket: (bucket.commodity, bucket.contract_month, bucket.book),
    )

