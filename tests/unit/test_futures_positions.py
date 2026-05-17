from decimal import Decimal
from pathlib import Path

import pytest

from backend.app.services.positions import (
    FuturesPositionValidationError,
    aggregate_futures_exposure,
    load_futures_positions_csv,
    signed_exposure_bbl,
)


SAMPLE_DIR = Path(__file__).resolve().parents[2] / "data" / "sample" / "positions"


def test_valid_futures_file_loads_successfully() -> None:
    rows = load_futures_positions_csv(SAMPLE_DIR / "valid_futures_positions.csv")

    assert len(rows) == 6
    assert {row.commodity for row in rows} == {"BRENT", "WTI"}
    assert rows[0].contract_month == "2026-06"
    assert {row.currency for row in rows} == {"USD"}
    assert {row.unit for row in rows} == {"bbl"}


def test_missing_required_column_fails() -> None:
    with pytest.raises(FuturesPositionValidationError) as exc_info:
        load_futures_positions_csv(SAMPLE_DIR / "invalid_missing_column.csv")

    assert _codes(exc_info.value) == {"missing_required_columns"}
    assert "counterparty" in str(exc_info.value)


def test_negative_lots_fail() -> None:
    with pytest.raises(FuturesPositionValidationError) as exc_info:
        load_futures_positions_csv(SAMPLE_DIR / "invalid_negative_lots.csv")

    assert _codes(exc_info.value) == {"invalid_lots"}
    assert "strictly positive" in str(exc_info.value)


def test_invalid_direction_fails() -> None:
    with pytest.raises(FuturesPositionValidationError) as exc_info:
        load_futures_positions_csv(SAMPLE_DIR / "invalid_bad_direction.csv")

    assert _codes(exc_info.value) == {"invalid_direction"}


def test_unsupported_commodity_fails() -> None:
    with pytest.raises(FuturesPositionValidationError) as exc_info:
        load_futures_positions_csv(SAMPLE_DIR / "invalid_unsupported_commodity.csv")

    assert _codes(exc_info.value) == {"unsupported_commodity"}
    assert "BRENT or WTI" in str(exc_info.value)


def test_duplicate_position_id_fails() -> None:
    with pytest.raises(FuturesPositionValidationError) as exc_info:
        load_futures_positions_csv(SAMPLE_DIR / "invalid_duplicate_position_id.csv")

    assert _codes(exc_info.value) == {"duplicate_position_id"}
    assert "FUT-0001" in str(exc_info.value)


def test_malformed_trade_date_fails() -> None:
    with pytest.raises(FuturesPositionValidationError) as exc_info:
        load_futures_positions_csv(SAMPLE_DIR / "invalid_bad_dates.csv")

    assert _codes(exc_info.value) == {"invalid_trade_date"}


def test_buy_futures_create_positive_exposure() -> None:
    rows = load_futures_positions_csv(SAMPLE_DIR / "valid_futures_positions.csv")

    assert signed_exposure_bbl(rows[0]) == Decimal("12000")


def test_sell_futures_create_negative_exposure() -> None:
    rows = load_futures_positions_csv(SAMPLE_DIR / "valid_futures_positions.csv")

    assert signed_exposure_bbl(rows[1]) == Decimal("-5000")


def test_exposure_aggregates_by_commodity_contract_month_and_book() -> None:
    rows = load_futures_positions_csv(SAMPLE_DIR / "valid_futures_positions.csv")

    buckets = aggregate_futures_exposure(rows)
    brent_m1 = _bucket_for(buckets, "BRENT", "2026-06", "Crude Alpha")
    wti_m1 = _bucket_for(buckets, "WTI", "2026-06", "Crude Beta")

    assert brent_m1.net_exposure_bbl == Decimal("7000")
    assert wti_m1.net_exposure_bbl == Decimal("-2000")


def test_gross_net_long_short_exposure_metrics_are_correct() -> None:
    rows = load_futures_positions_csv(SAMPLE_DIR / "valid_futures_positions.csv")

    buckets = aggregate_futures_exposure(rows)
    brent_m1 = _bucket_for(buckets, "BRENT", "2026-06", "Crude Alpha")

    assert brent_m1.gross_exposure_bbl == Decimal("17000")
    assert brent_m1.net_exposure_bbl == Decimal("7000")
    assert brent_m1.long_exposure_bbl == Decimal("12000")
    assert brent_m1.short_exposure_bbl == Decimal("-5000")


def _codes(error: FuturesPositionValidationError) -> set[str]:
    return {issue.code for issue in error.issues}


def _bucket_for(buckets, commodity: str, contract_month: str, book: str):
    return next(
        bucket
        for bucket in buckets
        if bucket.commodity == commodity
        and bucket.contract_month == contract_month
        and bucket.book == book
    )

