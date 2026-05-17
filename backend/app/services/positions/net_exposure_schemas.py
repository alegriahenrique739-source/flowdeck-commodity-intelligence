from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class NetExposureBucket(BaseModel):
    model_config = ConfigDict(frozen=True)

    hedge_index: str
    exposure_month: str
    book: str
    label: str
    physical_exposure_bbl: Decimal
    paper_exposure_bbl: Decimal
    net_exposure_bbl: Decimal
    absolute_net_exposure_bbl: Decimal
    gross_component_exposure_bbl: Decimal
    gross_exposure_bbl: Decimal
    long_exposure_bbl: Decimal
    short_exposure_bbl: Decimal


class LargestExposureBucket(BaseModel):
    model_config = ConfigDict(frozen=True)

    label: str
    net_exposure_bbl: Decimal


class NetExposureSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    total_physical_exposure_bbl: Decimal
    total_paper_exposure_bbl: Decimal
    total_net_exposure_bbl: Decimal
    total_absolute_net_exposure_bbl: Decimal
    total_gross_component_exposure_bbl: Decimal
    total_gross_exposure_bbl: Decimal
    total_long_exposure_bbl: Decimal
    total_short_exposure_bbl: Decimal
    number_of_exposure_buckets: int
    largest_long_bucket: LargestExposureBucket | None
    largest_short_bucket: LargestExposureBucket | None


class NetExposureResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    buckets: tuple[NetExposureBucket, ...]
    summary: NetExposureSummary
