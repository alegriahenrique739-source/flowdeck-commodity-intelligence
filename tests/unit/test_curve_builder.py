from decimal import Decimal
from pathlib import Path

import pytest

from backend.app.services.curves import (
    CurveBuildError,
    CurveShape,
    build_forward_curves,
)
from backend.app.services.market_data import load_market_data_csv


SAMPLE_DIR = (
    Path(__file__).resolve().parents[2] / "data" / "sample" / "market_data"
)


def test_valid_brent_curve_builds_successfully() -> None:
    rows = load_market_data_csv(SAMPLE_DIR / "valid_brent_wti_futures.csv")

    brent_curve = _curve_for(build_forward_curves(rows), "BRENT")

    assert brent_curve.valuation_date.isoformat() == "2026-05-08"
    assert brent_curve.front_month_contract == "BRTM26"
    assert brent_curve.back_month_contract == "BRTQ26"
    assert brent_curve.front_month_price == Decimal("84.12")
    assert brent_curve.back_month_price == Decimal("83.31")


def test_valid_wti_curve_builds_successfully() -> None:
    rows = load_market_data_csv(SAMPLE_DIR / "valid_brent_wti_futures.csv")

    wti_curve = _curve_for(build_forward_curves(rows), "WTI")

    assert wti_curve.front_month_contract == "WTIM26"
    assert wti_curve.back_month_contract == "WTIQ26"
    assert wti_curve.front_to_back_spread == Decimal("0.83")


def test_contracts_are_correctly_ordered() -> None:
    rows = load_market_data_csv(SAMPLE_DIR / "curve_mixed.csv")

    curve = build_forward_curves(rows)[0]

    assert [contract.contract_code for contract in curve.ordered_contracts] == [
        "BRTM26",
        "BRTN26",
        "BRTQ26",
        "BRTU26",
        "BRTV26",
        "BRTX26",
    ]


def test_backwardation_is_detected_correctly() -> None:
    rows = load_market_data_csv(SAMPLE_DIR / "curve_backwardated.csv")

    curve = build_forward_curves(rows)[0]

    assert curve.curve_shape == CurveShape.BACKWARDATION
    assert curve.front_to_back_spread == Decimal("3.80")


def test_contango_is_detected_correctly() -> None:
    rows = load_market_data_csv(SAMPLE_DIR / "curve_contango.csv")

    curve = build_forward_curves(rows)[0]

    assert curve.curve_shape == CurveShape.CONTANGO
    assert curve.front_to_back_spread == Decimal("-2.60")


def test_mixed_curve_is_detected_correctly() -> None:
    rows = load_market_data_csv(SAMPLE_DIR / "curve_mixed.csv")

    curve = build_forward_curves(rows)[0]

    assert curve.curve_shape == CurveShape.MIXED


def test_m1_m2_spread_is_calculated_correctly() -> None:
    rows = load_market_data_csv(SAMPLE_DIR / "curve_backwardated.csv")

    curve = build_forward_curves(rows)[0]
    spread = curve.calendar_spreads["M1_M2"]

    assert spread.near_contract == "BRTM26"
    assert spread.far_contract == "BRTN26"
    assert spread.spread == Decimal("0.45")


def test_missing_m6_or_m12_does_not_crash_service() -> None:
    rows = load_market_data_csv(SAMPLE_DIR / "valid_brent_wti_futures.csv")

    brent_curve = _curve_for(build_forward_curves(rows), "BRENT")

    assert set(brent_curve.calendar_spreads) == {"M1_M2", "M2_M3"}


def test_empty_input_gives_clear_error() -> None:
    with pytest.raises(CurveBuildError, match="empty market data"):
        build_forward_curves([])


def _curve_for(curves, commodity: str):
    return next(curve for curve in curves if curve.commodity == commodity)

