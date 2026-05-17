from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


SUPPORTED_COMMODITIES = {"BRENT", "WTI"}
SUPPORTED_PRICING_INDEXES = {"BRENT", "WTI"}
SUPPORTED_CURRENCY = "USD"
SUPPORTED_UNIT = "bbl"


class PhysicalBuySell(StrEnum):
    BUY = "BUY"
    SELL = "SELL"


class PhysicalCargoValidationIssue(BaseModel):
    dataset: str = "physical_cargoes"
    severity: str = "error"
    row_number: int | None = None
    column: str | None = None
    code: str
    message: str


class PhysicalCargoRow(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, frozen=True)

    cargo_id: str
    trade_date: date
    book: str
    commodity: str
    buy_sell: PhysicalBuySell
    volume_bbl: Decimal
    pricing_index: str
    pricing_month: str
    fixed_price: Decimal | None = None
    differential: Decimal | None = None
    delivery_start: date
    delivery_end: date
    location: str
    freight_cost_per_bbl: Decimal | None = None
    storage_cost_per_bbl: Decimal | None = None
    currency: str
    unit: str
    counterparty: str

    @field_validator("cargo_id", "book", "location", "counterparty", mode="before")
    @classmethod
    def clean_required_text(cls, value: Any) -> str:
        return _clean_text(value)

    @field_validator("cargo_id", "book", "location", "counterparty")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        if not value:
            raise ValueError("must not be blank")
        return value

    @field_validator("trade_date", "delivery_start", "delivery_end", mode="before")
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

    @field_validator("buy_sell", mode="before")
    @classmethod
    def normalize_buy_sell(cls, value: Any) -> str:
        return _clean_text(value).upper()

    @field_validator("volume_bbl")
    @classmethod
    def validate_positive_volume(cls, value: Decimal) -> Decimal:
        if value <= 0:
            raise ValueError("must be strictly positive")
        return value

    @field_validator("pricing_index", mode="before")
    @classmethod
    def normalize_pricing_index(cls, value: Any) -> str:
        return _clean_text(value).upper()

    @field_validator("pricing_index")
    @classmethod
    def validate_pricing_index(cls, value: str) -> str:
        if value not in SUPPORTED_PRICING_INDEXES:
            raise ValueError("must be one of BRENT or WTI")
        return value

    @field_validator("pricing_month", mode="before")
    @classmethod
    def normalize_pricing_month(cls, value: Any) -> str:
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

    @field_validator("fixed_price", "differential", "freight_cost_per_bbl", "storage_cost_per_bbl", mode="before")
    @classmethod
    def blank_optional_decimal_as_none(cls, value: Any) -> Any:
        if _clean_text(value) == "":
            return None
        return value

    @field_validator("fixed_price")
    @classmethod
    def validate_optional_positive_price(
        cls, value: Decimal | None
    ) -> Decimal | None:
        if value is not None and value <= 0:
            raise ValueError("must be positive when provided")
        return value

    @field_validator("freight_cost_per_bbl", "storage_cost_per_bbl")
    @classmethod
    def validate_optional_non_negative_cost(
        cls, value: Decimal | None
    ) -> Decimal | None:
        if value is not None and value < 0:
            raise ValueError("must be zero or positive when provided")
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

    @model_validator(mode="after")
    def validate_delivery_window(self) -> PhysicalCargoRow:
        if self.delivery_end < self.delivery_start:
            raise ValueError("delivery_end must be on or after delivery_start")
        return self


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()

