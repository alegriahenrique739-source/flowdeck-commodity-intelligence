from decimal import Decimal
from pathlib import Path

import pytest

from backend.app.services.positions import (
    PhysicalCargoValidationError,
    aggregate_physical_exposure,
    load_physical_cargoes_csv,
    signed_physical_exposure_bbl,
)


SAMPLE_DIR = Path(__file__).resolve().parents[2] / "data" / "sample" / "positions"


def test_valid_physical_cargo_file_loads_successfully() -> None:
    cargoes = load_physical_cargoes_csv(SAMPLE_DIR / "valid_physical_cargoes.csv")

    assert len(cargoes) == 5
    assert {cargo.commodity for cargo in cargoes} == {"BRENT", "WTI"}
    assert {cargo.pricing_index for cargo in cargoes} == {"BRENT", "WTI"}
    assert cargoes[0].pricing_month == "2026-06"
    assert {cargo.currency for cargo in cargoes} == {"USD"}
    assert {cargo.unit for cargo in cargoes} == {"bbl"}


def test_missing_required_column_fails() -> None:
    with pytest.raises(PhysicalCargoValidationError) as exc_info:
        load_physical_cargoes_csv(
            SAMPLE_DIR / "invalid_physical_missing_column.csv"
        )

    assert _codes(exc_info.value) == {"missing_required_columns"}
    assert "counterparty" in str(exc_info.value)


def test_negative_volume_fails() -> None:
    with pytest.raises(PhysicalCargoValidationError) as exc_info:
        load_physical_cargoes_csv(
            SAMPLE_DIR / "invalid_physical_negative_volume.csv"
        )

    assert _codes(exc_info.value) == {"invalid_volume_bbl"}
    assert "strictly positive" in str(exc_info.value)


def test_invalid_buy_sell_fails() -> None:
    with pytest.raises(PhysicalCargoValidationError) as exc_info:
        load_physical_cargoes_csv(SAMPLE_DIR / "invalid_physical_bad_buy_sell.csv")

    assert _codes(exc_info.value) == {"invalid_buy_sell"}


def test_unsupported_pricing_index_fails() -> None:
    with pytest.raises(PhysicalCargoValidationError) as exc_info:
        load_physical_cargoes_csv(
            SAMPLE_DIR / "invalid_physical_unsupported_pricing_index.csv"
        )

    assert _codes(exc_info.value) == {"unsupported_pricing_index"}
    assert "BRENT or WTI" in str(exc_info.value)


def test_duplicate_cargo_id_fails() -> None:
    with pytest.raises(PhysicalCargoValidationError) as exc_info:
        load_physical_cargoes_csv(
            SAMPLE_DIR / "invalid_physical_duplicate_cargo_id.csv"
        )

    assert _codes(exc_info.value) == {"duplicate_cargo_id"}
    assert "CARGO-0001" in str(exc_info.value)


def test_malformed_dates_fail() -> None:
    with pytest.raises(PhysicalCargoValidationError) as exc_info:
        load_physical_cargoes_csv(SAMPLE_DIR / "invalid_physical_bad_dates.csv")

    assert _codes(exc_info.value) == {
        "invalid_delivery_start",
        "invalid_trade_date",
    }


def test_delivery_end_before_delivery_start_fails() -> None:
    with pytest.raises(PhysicalCargoValidationError) as exc_info:
        load_physical_cargoes_csv(
            SAMPLE_DIR / "invalid_physical_delivery_end_before_start.csv"
        )

    assert "delivery_end must be on or after delivery_start" in str(exc_info.value)


def test_buy_physical_creates_positive_exposure() -> None:
    cargoes = load_physical_cargoes_csv(SAMPLE_DIR / "valid_physical_cargoes.csv")

    assert signed_physical_exposure_bbl(cargoes[0]) == Decimal("600000")


def test_sell_physical_creates_negative_exposure() -> None:
    cargoes = load_physical_cargoes_csv(SAMPLE_DIR / "valid_physical_cargoes.csv")

    assert signed_physical_exposure_bbl(cargoes[1]) == Decimal("-250000")


def test_exposure_aggregates_by_commodity_pricing_index_pricing_month_and_book() -> None:
    cargoes = load_physical_cargoes_csv(SAMPLE_DIR / "valid_physical_cargoes.csv")

    buckets = aggregate_physical_exposure(cargoes)
    brent_bucket = _bucket_for(
        buckets, "BRENT", "BRENT", "2026-06", "Physical Atlantic"
    )
    wti_bucket = _bucket_for(buckets, "WTI", "WTI", "2026-07", "Physical Gulf")

    assert brent_bucket.net_physical_exposure_bbl == Decimal("250000")
    assert wti_bucket.net_physical_exposure_bbl == Decimal("150000")


def test_gross_net_long_short_physical_exposure_metrics_are_correct() -> None:
    cargoes = load_physical_cargoes_csv(SAMPLE_DIR / "valid_physical_cargoes.csv")

    buckets = aggregate_physical_exposure(cargoes)
    brent_bucket = _bucket_for(
        buckets, "BRENT", "BRENT", "2026-06", "Physical Atlantic"
    )

    assert brent_bucket.gross_physical_exposure_bbl == Decimal("950000")
    assert brent_bucket.net_physical_exposure_bbl == Decimal("250000")
    assert brent_bucket.long_physical_exposure_bbl == Decimal("600000")
    assert brent_bucket.short_physical_exposure_bbl == Decimal("-350000")


def test_optional_fixed_price_can_be_blank() -> None:
    cargoes = load_physical_cargoes_csv(SAMPLE_DIR / "valid_physical_cargoes.csv")

    assert cargoes[0].fixed_price is None


def test_optional_differential_can_be_negative() -> None:
    cargoes = load_physical_cargoes_csv(SAMPLE_DIR / "valid_physical_cargoes.csv")

    assert cargoes[1].differential == Decimal("-0.20")


def test_optional_freight_and_storage_costs_can_be_blank_or_zero() -> None:
    cargoes = load_physical_cargoes_csv(SAMPLE_DIR / "valid_physical_cargoes.csv")

    assert cargoes[0].freight_cost_per_bbl is None
    assert cargoes[0].storage_cost_per_bbl == Decimal("0")
    assert cargoes[1].storage_cost_per_bbl is None


def _codes(error: PhysicalCargoValidationError) -> set[str]:
    return {issue.code for issue in error.issues}


def _bucket_for(
    buckets, commodity: str, pricing_index: str, pricing_month: str, book: str
):
    return next(
        bucket
        for bucket in buckets
        if bucket.commodity == commodity
        and bucket.pricing_index == pricing_index
        and bucket.pricing_month == pricing_month
        and bucket.book == book
    )

