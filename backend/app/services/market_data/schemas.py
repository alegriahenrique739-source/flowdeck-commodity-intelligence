from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator


SUPPORTED_COMMODITIES = {"BRENT", "WTI"}
SUPPORTED_CURRENCY = "USD"
SUPPORTED_UNIT = "bbl"


class ValidationIssue(BaseModel):
    dataset: str = "market_data"
    severity: str = "error"
    row_number: int | None = None
    column: str | None = None
    code: str
    message: str


class MarketDataRow(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, frozen=True)

    valuation_date: date
    commodity: str
    contract_code: str
    contract_month: str
    expiry_date: date
    price: Decimal
    currency: str
    unit: str
    source: str

    @field_validator("valuation_date", "expiry_date", mode="before")
    @classmethod
    def parse_iso_date(cls, value: Any) -> date:
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

    @field_validator("contract_code", "source", mode="before")
    @classmethod
    def require_non_blank_text(cls, value: Any) -> str:
        return _clean_text(value)

    @field_validator("contract_code", "source")
    @classmethod
    def validate_non_blank_text(cls, value: str) -> str:
        if not value:
            raise ValueError("must not be blank")
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

    @field_validator("price")
    @classmethod
    def validate_positive_price(cls, value: Decimal) -> Decimal:
        if value <= 0:
            raise ValueError("must be positive")
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

