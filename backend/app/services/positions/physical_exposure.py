from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Iterable

from pydantic import BaseModel, ConfigDict

from backend.app.services.positions.physical_schemas import (
    PhysicalBuySell,
    PhysicalCargoRow,
)


class PhysicalExposureBucket(BaseModel):
    model_config = ConfigDict(frozen=True)

    commodity: str
    pricing_index: str
    pricing_month: str
    book: str
    gross_physical_exposure_bbl: Decimal
    net_physical_exposure_bbl: Decimal
    long_physical_exposure_bbl: Decimal
    short_physical_exposure_bbl: Decimal


def signed_physical_exposure_bbl(cargo: PhysicalCargoRow) -> Decimal:
    sign = Decimal("1") if cargo.buy_sell == PhysicalBuySell.BUY else Decimal("-1")
    return cargo.volume_bbl * sign


def aggregate_physical_exposure(
    cargoes: Iterable[PhysicalCargoRow],
) -> list[PhysicalExposureBucket]:
    grouped: dict[tuple[str, str, str, str], list[Decimal]] = defaultdict(list)

    for cargo in cargoes:
        key = (cargo.commodity, cargo.pricing_index, cargo.pricing_month, cargo.book)
        grouped[key].append(signed_physical_exposure_bbl(cargo))

    buckets: list[PhysicalExposureBucket] = []
    for (commodity, pricing_index, pricing_month, book), exposures in grouped.items():
        long_exposure = sum(
            (exposure for exposure in exposures if exposure > 0), Decimal("0")
        )
        short_exposure = sum(
            (exposure for exposure in exposures if exposure < 0), Decimal("0")
        )
        net_exposure = sum(exposures, Decimal("0"))
        gross_exposure = long_exposure + abs(short_exposure)

        buckets.append(
            PhysicalExposureBucket(
                commodity=commodity,
                pricing_index=pricing_index,
                pricing_month=pricing_month,
                book=book,
                gross_physical_exposure_bbl=gross_exposure,
                net_physical_exposure_bbl=net_exposure,
                long_physical_exposure_bbl=long_exposure,
                short_physical_exposure_bbl=short_exposure,
            )
        )

    return sorted(
        buckets,
        key=lambda bucket: (
            bucket.commodity,
            bucket.pricing_index,
            bucket.pricing_month,
            bucket.book,
        ),
    )

