from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class CurveShape(StrEnum):
    BACKWARDATION = "BACKWARDATION"
    CONTANGO = "CONTANGO"
    FLAT = "FLAT"
    MIXED = "MIXED"


class ForwardCurveContract(BaseModel):
    model_config = ConfigDict(frozen=True)

    contract_code: str
    contract_month: str
    expiry_date: date
    price: Decimal


class CalendarSpread(BaseModel):
    model_config = ConfigDict(frozen=True)

    label: str
    near_contract: str
    far_contract: str
    spread: Decimal


class ForwardCurve(BaseModel):
    model_config = ConfigDict(frozen=True)

    valuation_date: date
    commodity: str
    ordered_contracts: tuple[ForwardCurveContract, ...]
    front_month_contract: str
    front_month_price: Decimal
    back_month_contract: str
    back_month_price: Decimal
    front_to_back_spread: Decimal
    curve_shape: CurveShape
    calendar_spreads: dict[str, CalendarSpread]

