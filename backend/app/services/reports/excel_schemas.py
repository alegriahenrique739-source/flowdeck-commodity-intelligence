from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from backend.app.services.curves import ForwardCurve
from backend.app.services.hedging import HedgeSimulationResult
from backend.app.services.market_data import MarketDataRow
from backend.app.services.positions import (
    FuturesPositionRow,
    NetExposureResult,
    PhysicalCargoRow,
)
from backend.app.services.risk import StressPnlResult


class CalendarSpreadReportRow(BaseModel):
    model_config = ConfigDict(frozen=True)

    valuation_date: date
    commodity: str
    spread_name: str
    near_contract: str
    far_contract: str
    spread_usd_per_bbl: Decimal


class ExcelReportInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    market_data_rows: tuple[MarketDataRow, ...] = ()
    curve_summaries: tuple[ForwardCurve, ...] = ()
    calendar_spreads: tuple[CalendarSpreadReportRow, ...] = ()
    futures_positions: tuple[FuturesPositionRow, ...] = ()
    physical_cargoes: tuple[PhysicalCargoRow, ...] = ()
    net_exposure_result: NetExposureResult | None = None
    hedge_simulation_result: HedgeSimulationResult | None = None
    stress_result: StressPnlResult | None = None
    assumptions: tuple[str, ...] = ()

