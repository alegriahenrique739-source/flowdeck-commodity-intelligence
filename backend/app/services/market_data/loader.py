from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Iterable

import pandas as pd
from pydantic import ValidationError

from backend.app.services.market_data.schemas import MarketDataRow, ValidationIssue


REQUIRED_MARKET_DATA_COLUMNS = (
    "valuation_date",
    "commodity",
    "contract_code",
    "contract_month",
    "expiry_date",
    "price",
    "currency",
    "unit",
    "source",
)

FIELD_ERROR_CODES = {
    "valuation_date": "invalid_valuation_date",
    "commodity": "unsupported_commodity",
    "contract_code": "invalid_contract_code",
    "contract_month": "invalid_contract_month",
    "expiry_date": "invalid_expiry_date",
    "price": "invalid_price",
    "currency": "unsupported_currency",
    "unit": "unsupported_unit",
    "source": "invalid_source",
}


class MarketDataValidationError(ValueError):
    def __init__(self, issues: Iterable[ValidationIssue]) -> None:
        self.issues = list(issues)
        message = "; ".join(issue.message for issue in self.issues)
        super().__init__(message)


def load_market_data_csv(path: str | Path) -> list[MarketDataRow]:
    csv_path = Path(path)
    frame = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    frame.columns = [str(column).strip() for column in frame.columns]

    issues: list[ValidationIssue] = []
    issues.extend(_validate_required_columns(frame.columns))
    if issues:
        raise MarketDataValidationError(issues)

    rows: list[MarketDataRow] = []
    row_numbers: list[int] = []

    for index, record in frame.iterrows():
        row_number = int(index) + 2
        try:
            rows.append(MarketDataRow.model_validate(record.to_dict()))
            row_numbers.append(row_number)
        except ValidationError as exc:
            issues.extend(_issues_from_pydantic_error(exc, row_number))

    if not issues:
        issues.extend(_detect_duplicate_rows(rows, row_numbers))

    if issues:
        raise MarketDataValidationError(issues)

    return rows


def _validate_required_columns(columns: Iterable[str]) -> list[ValidationIssue]:
    present = set(columns)
    missing = [
        column for column in REQUIRED_MARKET_DATA_COLUMNS if column not in present
    ]
    if not missing:
        return []

    return [
        ValidationIssue(
            column=None,
            code="missing_required_columns",
            message=f"Missing required market data column(s): {', '.join(missing)}.",
        )
    ]


def _issues_from_pydantic_error(
    error: ValidationError, row_number: int
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for entry in error.errors():
        column = str(entry["loc"][0]) if entry.get("loc") else None
        code = FIELD_ERROR_CODES.get(column or "", "invalid_market_data_row")
        detail = str(entry.get("msg", "is invalid")).removeprefix("Value error, ")
        issues.append(
            ValidationIssue(
                row_number=row_number,
                column=column,
                code=code,
                message=f"Row {row_number}: {column} {detail}.",
            )
        )
    return issues


def _detect_duplicate_rows(
    rows: list[MarketDataRow], row_numbers: list[int]
) -> list[ValidationIssue]:
    grouped: dict[tuple[object, str, str], list[int]] = defaultdict(list)
    for row, row_number in zip(rows, row_numbers, strict=True):
        key = (row.valuation_date, row.commodity, row.contract_month)
        grouped[key].append(row_number)

    issues: list[ValidationIssue] = []
    for (valuation_date, commodity, contract_month), duplicates in grouped.items():
        if len(duplicates) < 2:
            continue

        issues.append(
            ValidationIssue(
                row_number=duplicates[0],
                column=None,
                code="duplicate_market_data_row",
                message=(
                    "Duplicate market data rows for "
                    f"{valuation_date} {commodity} {contract_month} "
                    f"at source rows {', '.join(str(row) for row in duplicates)}."
                ),
            )
        )

    return issues

