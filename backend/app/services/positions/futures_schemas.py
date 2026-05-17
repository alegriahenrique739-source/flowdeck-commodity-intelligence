from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator


SUPPORTED_COMMODITIES = {"BRENT", "WTI"}
SUPPORTED_CURRENCY = "USD"
SUPPORTED_UNIT = "bbl"


class FuturesDirection(StrEnum):
    BUY = "BUY"
    SELL = "SELL"


class PositionValidationIssue(BaseModel):
    dataset: str = "futures_positions"
    severity: str = "error"
    row_number: int | None = None
    column: str | None = None
    code: str
    message: str


class FuturesPositionRow(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, frozen=True)

    position_id: str
    trade_date: date
    book: str
    commodity: str
    contract_code: str
    contract_month: str
    direction: FuturesDirection
    lots: Decimal
    contract_size: Decimal
    entry_price: Decimal
    currency: str
    unit: str
    counterparty: str

    @field_validator("position_id", "book", "contract_code", "counterparty", mode="before")
    @classmethod
    def clean_required_text(cls, value: Any) -> str:
        return _clean_text(value)

    @field_validator("position_id", "book", "contract_code", "counterparty")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        if not value:
            raise ValueError("must not be blank")
        return value

    @field_validator("trade_date", mode="before")
    @classmethod
    def parse_trade_date(cls, value: Any) -> date:
        if isinstance(value, date):
            return value

        text = _clean_text(value)
        try:
            return date.fromisoformat(text)
        except ValueError as exc:
            raise ValueError("must be a valid ISO date in YYYY-MM-DD format") from exc

    @field_validator("commodity", mode="before")
    @classmethod
    def normalize_commodity(cls, value: Any) -> str:
        return _clean_text(value).upper()

    @field_validator("commodity")
    @classmethod
    def validate_commodity(cls, value: str) -> str:
        if value not in SUPPORTED_COMMODITIES:
            raise ValueError("must be one of BRENT or WTI")
        return value

    @field_validator("contract_month", mode="before")
    @classmethod
    def normalize_contract_month(cls, value: Any) -> str:
        text = _clean_text(value)
        parts = text.split("-")
        if len(parts) != 2:
            raise ValueError("must be a valid monthly bucket in YYYY-MM format")

        try:
            year = int(parts[0])
            month = int(parts[1])
        except ValueError as exc:
            raise ValueError("must be a valid monthly bucket in YYYY-MM format") from exc

        if year < 1900 or month < 1 or month > 12:
            raise ValueError("must be a valid monthly bucket in YYYY-MM format")

        return f"{year:04d}-{month:02d}"

    @field_validator("direction", mode="before")
    @classmethod
    def normalize_direction(cls, value: Any) -> str:
        return _clean_text(value).upper()

    @field_validator("lots", "contract_size", "entry_price")
    @classmethod
    def validate_positive_decimal(cls, value: Decimal) -> Decimal:
        if value <= 0:
            raise ValueError("must be strictly positive")
        return value

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency(cls, value: Any) -> str:
        return _clean_text(value).upper()

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str) -> str:
        if value != SUPPORTED_CURRENCY:
            raise ValueError("must be USD")
        return value

    @field_validator("unit", mode="before")
    @classmethod
    def normalize_unit(cls, value: Any) -> str:
        return _clean_text(value).lower()

    @field_validator("unit")
    @classmethod
    def validate_unit(cls, value: str) -> str:
        if value != SUPPORTED_UNIT:
            raise ValueError("must be bbl")
        return value


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()

