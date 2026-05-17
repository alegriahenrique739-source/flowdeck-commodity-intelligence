from __future__ import annotations

from decimal import Decimal

from backend.app.services.curves.schemas import CalendarSpread, ForwardCurveContract


SPREAD_DEFINITIONS = {
    "M1_M2": (0, 1),
    "M2_M3": (1, 2),
    "M3_M6": (2, 5),
    "M6_M12": (5, 11),
}


def compute_calendar_spreads(
    contracts: tuple[ForwardCurveContract, ...],
) -> dict[str, CalendarSpread]:
    spreads: dict[str, CalendarSpread] = {}

    for label, (near_index, far_index) in SPREAD_DEFINITIONS.items():
        if len(contracts) <= far_index:
            continue

        near_contract = contracts[near_index]
        far_contract = contracts[far_index]
        spreads[label] = CalendarSpread(
            label=label,
            near_contract=near_contract.contract_code,
            far_contract=far_contract.contract_code,
            spread=_spread(near_contract.price, far_contract.price),
        )

    return spreads


def _spread(near_price: Decimal, far_price: Decimal) -> Decimal:
    return near_price - far_price

