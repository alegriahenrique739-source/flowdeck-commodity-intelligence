from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Iterable

import pandas as pd
from pydantic import ValidationError

from backend.app.services.positions.futures_schemas import (
    FuturesPositionRow,
    PositionValidationIssue,
)


REQUIRED_FUTURES_POSITION_COLUMNS = (
    "position_id",
    "trade_date",
    "book",
    "commodity",
    "contract_code",
    "contract_month",
    "direction",
    "lots",
    "contract_size",
    "entry_price",
    "currency",
    "unit",
    "counterparty",
)

FIELD_ERROR_CODES = {
    "position_id": "invalid_position_id",
    "trade_date": "invalid_trade_date",
    "book": "invalid_book",
    "commodity": "unsupported_commodity",
    "contract_code": "invalid_contract_code",
    "contract_month": "invalid_contract_month",
    "direction": "invalid_direction",
    "lots": "invalid_lots",
    "contract_size": "invalid_contract_size",
    "entry_price": "invalid_entry_price",
    "currency": "unsupported_currency",
    "unit": "unsupported_unit",
    "counterparty": "invalid_counterparty",
}


class FuturesPositionValidationError(ValueError):
    def __init__(self, issues: Iterable[PositionValidationIssue]) -> None:
        self.issues = list(issues)
        message = "; ".join(issue.message for issue in self.issues)
        super().__init__(message)


def load_futures_positions_csv(path: str | Path) -> list[FuturesPositionRow]:
    csv_path = Path(path)
    frame = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    frame.columns = [str(column).strip() for column in frame.columns]

    issues: list[PositionValidationIssue] = []
    issues.extend(_validate_required_columns(frame.columns))
    if issues:
        raise FuturesPositionValidationError(issues)

    rows: list[FuturesPositionRow] = []
    row_numbers: list[int] = []

    for index, record in frame.iterrows():
        row_number = int(index) + 2
        try:
            rows.append(FuturesPositionRow.model_validate(record.to_dict()))
            row_numbers.append(row_number)
        except ValidationError as exc:
            issues.extend(_issues_from_pydantic_error(exc, row_number))

    if not issues:
        issues.extend(_detect_duplicate_position_ids(rows, row_numbers))

    if issues:
        raise FuturesPositionValidationError(issues)

    return rows


def _validate_required_columns(columns: Iterable[str]) -> list[PositionValidationIssue]:
    present = set(columns)
    missing = [
        column for column in REQUIRED_FUTURES_POSITION_COLUMNS if column not in present
    ]
    if not missing:
        return []

    return [
        PositionValidationIssue(
            column=None,
            code="missing_required_columns",
            message=f"Missing required futures position column(s): {', '.join(missing)}.",
        )
    ]


def _issues_from_pydantic_error(
    error: ValidationError, row_number: int
) -> list[PositionValidationIssue]:
    issues: list[PositionValidationIssue] = []
    for entry in error.errors():
        column = str(entry["loc"][0]) if entry.get("loc") else None
        code = FIELD_ERROR_CODES.get(column or "", "invalid_futures_position_row")
        detail = str(entry.get("msg", "is invalid")).removeprefix("Value error, ")
        issues.append(
            PositionValidationIssue(
                row_number=row_number,
                column=column,
                code=code,
                message=f"Row {row_number}: {column} {detail}.",
            )
        )
    return issues


def _detect_duplicate_position_ids(
    rows: list[FuturesPositionRow], row_numbers: list[int]
) -> list[PositionValidationIssue]:
    grouped: dict[str, list[int]] = defaultdict(list)
    for row, row_number in zip(rows, row_numbers, strict=True):
        grouped[row.position_id].append(row_number)

    issues: list[PositionValidationIssue] = []
    for position_id, duplicates in grouped.items():
        if len(duplicates) < 2:
            continue

        issues.append(
            PositionValidationIssue(
                row_number=duplicates[0],
                column="position_id",
                code="duplicate_position_id",
                message=(
                    f"Duplicate position_id '{position_id}' at source rows "
                    f"{', '.join(str(row) for row in duplicates)}."
                ),
            )
        )

    return issues

