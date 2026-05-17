from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Iterable

import pandas as pd
from pydantic import ValidationError

from backend.app.services.positions.physical_schemas import (
    PhysicalCargoRow,
    PhysicalCargoValidationIssue,
)


REQUIRED_PHYSICAL_CARGO_COLUMNS = (
    "cargo_id",
    "trade_date",
    "book",
    "commodity",
    "buy_sell",
    "volume_bbl",
    "pricing_index",
    "pricing_month",
    "fixed_price",
    "differential",
    "delivery_start",
    "delivery_end",
    "location",
    "freight_cost_per_bbl",
    "storage_cost_per_bbl",
    "currency",
    "unit",
    "counterparty",
)

FIELD_ERROR_CODES = {
    "cargo_id": "invalid_cargo_id",
    "trade_date": "invalid_trade_date",
    "book": "invalid_book",
    "commodity": "unsupported_commodity",
    "buy_sell": "invalid_buy_sell",
    "volume_bbl": "invalid_volume_bbl",
    "pricing_index": "unsupported_pricing_index",
    "pricing_month": "invalid_pricing_month",
    "fixed_price": "invalid_fixed_price",
    "differential": "invalid_differential",
    "delivery_start": "invalid_delivery_start",
    "delivery_end": "invalid_delivery_end",
    "location": "invalid_location",
    "freight_cost_per_bbl": "invalid_freight_cost_per_bbl",
    "storage_cost_per_bbl": "invalid_storage_cost_per_bbl",
    "currency": "unsupported_currency",
    "unit": "unsupported_unit",
    "counterparty": "invalid_counterparty",
}


class PhysicalCargoValidationError(ValueError):
    def __init__(self, issues: Iterable[PhysicalCargoValidationIssue]) -> None:
        self.issues = list(issues)
        message = "; ".join(issue.message for issue in self.issues)
        super().__init__(message)


def load_physical_cargoes_csv(path: str | Path) -> list[PhysicalCargoRow]:
    csv_path = Path(path)
    frame = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    frame.columns = [str(column).strip() for column in frame.columns]

    issues: list[PhysicalCargoValidationIssue] = []
    issues.extend(_validate_required_columns(frame.columns))
    if issues:
        raise PhysicalCargoValidationError(issues)

    rows: list[PhysicalCargoRow] = []
    row_numbers: list[int] = []

    for index, record in frame.iterrows():
        row_number = int(index) + 2
        try:
            rows.append(PhysicalCargoRow.model_validate(record.to_dict()))
            row_numbers.append(row_number)
        except ValidationError as exc:
            issues.extend(_issues_from_pydantic_error(exc, row_number))

    if not issues:
        issues.extend(_detect_duplicate_cargo_ids(rows, row_numbers))

    if issues:
        raise PhysicalCargoValidationError(issues)

    return rows


def _validate_required_columns(
    columns: Iterable[str],
) -> list[PhysicalCargoValidationIssue]:
    present = set(columns)
    missing = [
        column for column in REQUIRED_PHYSICAL_CARGO_COLUMNS if column not in present
    ]
    if not missing:
        return []

    return [
        PhysicalCargoValidationIssue(
            column=None,
            code="missing_required_columns",
            message=f"Missing required physical cargo column(s): {', '.join(missing)}.",
        )
    ]


def _issues_from_pydantic_error(
    error: ValidationError, row_number: int
) -> list[PhysicalCargoValidationIssue]:
    issues: list[PhysicalCargoValidationIssue] = []
    for entry in error.errors():
        column = _column_from_error_location(entry.get("loc", ()))
        code = FIELD_ERROR_CODES.get(column or "", "invalid_physical_cargo_row")
        detail = str(entry.get("msg", "is invalid")).removeprefix("Value error, ")
        issues.append(
            PhysicalCargoValidationIssue(
                row_number=row_number,
                column=column,
                code=code,
                message=f"Row {row_number}: {column or 'row'} {detail}.",
            )
        )
    return issues


def _column_from_error_location(location: Iterable[object]) -> str | None:
    parts = list(location)
    if not parts:
        return None
    first = parts[0]
    return str(first) if first != "__root__" else None


def _detect_duplicate_cargo_ids(
    rows: list[PhysicalCargoRow], row_numbers: list[int]
) -> list[PhysicalCargoValidationIssue]:
    grouped: dict[str, list[int]] = defaultdict(list)
    for row, row_number in zip(rows, row_numbers, strict=True):
        grouped[row.cargo_id].append(row_number)

    issues: list[PhysicalCargoValidationIssue] = []
    for cargo_id, duplicates in grouped.items():
        if len(duplicates) < 2:
            continue

        issues.append(
            PhysicalCargoValidationIssue(
                row_number=duplicates[0],
                column="cargo_id",
                code="duplicate_cargo_id",
                message=(
                    f"Duplicate cargo_id '{cargo_id}' at source rows "
                    f"{', '.join(str(row) for row in duplicates)}."
                ),
            )
        )

    return issues

