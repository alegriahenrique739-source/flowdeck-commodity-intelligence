from __future__ import annotations

from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import Iterable

from backend.app.services.curves.schemas import (
    CurveShape,
    ForwardCurve,
    ForwardCurveContract,
)
from backend.app.services.curves.spreads import compute_calendar_spreads
from backend.app.services.market_data import MarketDataRow


CURVE_SHAPE_TOLERANCE = Decimal("0.0001")


class CurveBuildError(ValueError):
    pass


def build_forward_curves(rows: Iterable[MarketDataRow]) -> list[ForwardCurve]:
    market_rows = list(rows)
    if not market_rows:
        raise CurveBuildError("Cannot build forward curves from empty market data.")

    grouped: dict[tuple[date, str], list[MarketDataRow]] = defaultdict(list)
    for row in market_rows:
        grouped[(row.valuation_date, row.commodity)].append(row)

    curves = [
        _build_single_curve(valuation_date, commodity, curve_rows)
        for (valuation_date, commodity), curve_rows in grouped.items()
    ]
    return sorted(curves, key=lambda curve: (curve.valuation_date, curve.commodity))


def _build_single_curve(
    valuation_date: date, commodity: str, rows: list[MarketDataRow]
) -> ForwardCurve:
    contracts = tuple(_to_contract(row) for row in sorted(rows, key=_contract_sort_key))
    if not contracts:
        raise CurveBuildError(
            f"Cannot build {commodity} curve for {valuation_date}: no contracts found."
        )

    front = contracts[0]
    back = contracts[-1]
    return ForwardCurve(
        valuation_date=valuation_date,
        commodity=commodity,
        ordered_contracts=contracts,
        front_month_contract=front.contract_code,
        front_month_price=front.price,
        back_month_contract=back.contract_code,
        back_month_price=back.price,
        front_to_back_spread=front.price - back.price,
        curve_shape=classify_curve_shape(
            tuple(contract.price for contract in contracts)
        ),
        calendar_spreads=compute_calendar_spreads(contracts),
    )


def classify_curve_shape(
    prices: tuple[Decimal, ...], tolerance: Decimal = CURVE_SHAPE_TOLERANCE
) -> CurveShape:
    if not prices:
        raise CurveBuildError("Cannot classify curve shape without prices.")

    if len(prices) == 1:
        return CurveShape.FLAT

    has_upward_step = False
    has_downward_step = False

    for near_price, far_price in zip(prices, prices[1:], strict=False):
        difference = near_price - far_price
        if abs(difference) <= tolerance:
            continue
        if difference > 0:
            has_downward_step = True
        else:
            has_upward_step = True

    if has_upward_step and has_downward_step:
        return CurveShape.MIXED
    if not has_upward_step and not has_downward_step:
        return CurveShape.FLAT
    if has_downward_step:
        return CurveShape.BACKWARDATION
    return CurveShape.CONTANGO


def _to_contract(row: MarketDataRow) -> ForwardCurveContract:
    return ForwardCurveContract(
        contract_code=row.contract_code,
        contract_month=row.contract_month,
        expiry_date=row.expiry_date,
        price=row.price,
    )


def _contract_sort_key(row: MarketDataRow) -> tuple[int, int, date, str]:
    try:
        year_text, month_text = row.contract_month.split("-", maxsplit=1)
        year = int(year_text)
        month = int(month_text)
    except ValueError as exc:
        raise CurveBuildError(
            f"Invalid contract_month '{row.contract_month}' for {row.commodity} "
            f"{row.contract_code}; expected YYYY-MM."
        ) from exc

    if month < 1 or month > 12:
        raise CurveBuildError(
            f"Invalid contract_month '{row.contract_month}' for {row.commodity} "
            f"{row.contract_code}; month must be 01 through 12."
        )

    return (year, month, row.expiry_date, row.contract_code)

