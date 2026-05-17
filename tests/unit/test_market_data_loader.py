from pathlib import Path

import pytest

from backend.app.services.market_data import (
    MarketDataValidationError,
    load_market_data_csv,
)


SAMPLE_DIR = (
    Path(__file__).resolve().parents[2] / "data" / "sample" / "market_data"
)


def test_valid_file_loads_successfully() -> None:
    rows = load_market_data_csv(SAMPLE_DIR / "valid_brent_wti_futures.csv")

    assert len(rows) == 6
    assert {row.commodity for row in rows} == {"BRENT", "WTI"}
    assert rows[0].contract_month == "2026-06"
    assert {row.currency for row in rows} == {"USD"}
    assert {row.unit for row in rows} == {"bbl"}


def test_missing_required_column_fails() -> None:
    with pytest.raises(MarketDataValidationError) as exc_info:
        load_market_data_csv(SAMPLE_DIR / "invalid_missing_column.csv")

    assert _codes(exc_info.value) == {"missing_required_columns"}
    assert "source" in str(exc_info.value)


def test_negative_price_fails() -> None:
    with pytest.raises(MarketDataValidationError) as exc_info:
        load_market_data_csv(SAMPLE_DIR / "invalid_negative_price.csv")

    assert _codes(exc_info.value) == {"invalid_price"}
    assert "must be positive" in str(exc_info.value)


def test_unsupported_commodity_fails() -> None:
    with pytest.raises(MarketDataValidationError) as exc_info:
        load_market_data_csv(SAMPLE_DIR / "invalid_unsupported_commodity.csv")

    assert _codes(exc_info.value) == {"unsupported_commodity"}
    assert "BRENT or WTI" in str(exc_info.value)


def test_duplicate_rows_fail() -> None:
    with pytest.raises(MarketDataValidationError) as exc_info:
        load_market_data_csv(SAMPLE_DIR / "invalid_duplicate_rows.csv")

    assert _codes(exc_info.value) == {"duplicate_market_data_row"}
    assert "2026-05-08 BRENT 2026-06" in str(exc_info.value)


def test_malformed_dates_fail() -> None:
    with pytest.raises(MarketDataValidationError) as exc_info:
        load_market_data_csv(SAMPLE_DIR / "invalid_bad_dates.csv")

    assert _codes(exc_info.value) == {
        "invalid_expiry_date",
        "invalid_valuation_date",
    }


def _codes(error: MarketDataValidationError) -> set[str]:
    return {issue.code for issue in error.issues}

