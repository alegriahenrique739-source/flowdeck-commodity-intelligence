import { formatUsdPerBbl } from "@/lib/format";
import type { ApiRecord } from "@/lib/types";
import { stringValue, toNumber } from "./chartUtils";

interface ForwardCurveChartProps {
  curves: ApiRecord[];
}

interface CurvePoint {
  commodity: string;
  contractMonth: string;
  price: number;
}

const SERIES_COLORS: Record<string, string> = {
  BRENT: "#5eead4",
  WTI: "#fbbf24"
};

export function ForwardCurveChart({ curves }: ForwardCurveChartProps) {
  const points = extractCurvePoints(curves);
  const months = Array.from(new Set(points.map((point) => point.contractMonth))).sort();
  const commodities = Array.from(new Set(points.map((point) => point.commodity))).sort();

  if (points.length === 0 || months.length === 0) {
    return <ChartEmptyState title="Forward Curves" message="No curve points to chart." />;
  }

  const prices = points.map((point) => point.price);
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const yMin = Math.floor(minPrice - 1);
  const yMax = Math.ceil(maxPrice + 1);
  const yRange = Math.max(yMax - yMin, 1);
  const width = 640;
  const height = 260;
  const margin = { top: 20, right: 24, bottom: 58, left: 70 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;

  function xFor(month: string): number {
    if (months.length === 1) {
      return margin.left + plotWidth / 2;
    }
    const index = months.indexOf(month);
    return margin.left + (index / (months.length - 1)) * plotWidth;
  }

  function yFor(price: number): number {
    return margin.top + ((yMax - price) / yRange) * plotHeight;
  }

  return (
    <section
      aria-label="Forward Curves chart"
      className="rounded-lg border border-slate-800 bg-ink-950 p-4"
    >
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h3 className="text-sm font-semibold text-white">Forward Curves</h3>
        <div className="flex flex-wrap gap-3 text-xs">
          {commodities.map((commodity) => (
            <span className="flex items-center gap-2 text-slate-300" key={commodity}>
              <span
                className="h-2.5 w-2.5 rounded-full"
                style={{ backgroundColor: colorFor(commodity) }}
              />
              {commodity}
            </span>
          ))}
        </div>
      </div>

      <svg className="mt-4 h-auto w-full" role="img" viewBox={`0 0 ${width} ${height}`}>
        <title>Forward Curves</title>
        <line
          stroke="#334155"
          x1={margin.left}
          x2={margin.left + plotWidth}
          y1={margin.top + plotHeight}
          y2={margin.top + plotHeight}
        />
        <line
          stroke="#334155"
          x1={margin.left}
          x2={margin.left}
          y1={margin.top}
          y2={margin.top + plotHeight}
        />
        {[yMin, Math.round((yMin + yMax) / 2), yMax].map((tick) => (
          <g key={tick}>
            <line
              stroke="#1e293b"
              x1={margin.left}
              x2={margin.left + plotWidth}
              y1={yFor(tick)}
              y2={yFor(tick)}
            />
            <text fill="#94a3b8" fontSize="11" textAnchor="end" x={margin.left - 8} y={yFor(tick) + 4}>
              {formatUsdPerBbl(tick)}
            </text>
          </g>
        ))}
        {months.map((month) => (
          <text
            fill="#94a3b8"
            fontSize="11"
            key={month}
            textAnchor="middle"
            x={xFor(month)}
            y={height - 30}
          >
            {month}
          </text>
        ))}
        <text fill="#94a3b8" fontSize="12" textAnchor="middle" x={margin.left + plotWidth / 2} y={height - 8}>
          Contract Month
        </text>
        <text
          fill="#94a3b8"
          fontSize="12"
          textAnchor="middle"
          transform={`translate(18 ${margin.top + plotHeight / 2}) rotate(-90)`}
        >
          USD/bbl
        </text>

        {commodities.map((commodity) => {
          const series = points
            .filter((point) => point.commodity === commodity)
            .sort((left, right) => left.contractMonth.localeCompare(right.contractMonth));
          const path = series
            .map((point, index) => `${index === 0 ? "M" : "L"} ${xFor(point.contractMonth)} ${yFor(point.price)}`)
            .join(" ");

          return (
            <g key={commodity}>
              <path d={path} fill="none" stroke={colorFor(commodity)} strokeLinecap="round" strokeWidth="2.5" />
              {series.map((point) => (
                <circle
                  cx={xFor(point.contractMonth)}
                  cy={yFor(point.price)}
                  fill={colorFor(commodity)}
                  key={`${commodity}-${point.contractMonth}`}
                  r="4"
                />
              ))}
            </g>
          );
        })}
      </svg>
    </section>
  );
}

function extractCurvePoints(curves: ApiRecord[]): CurvePoint[] {
  return curves.flatMap((curve) => {
    const commodity = stringValue(curve.commodity, "UNKNOWN");
    const contracts = Array.isArray(curve.ordered_contracts)
      ? (curve.ordered_contracts as ApiRecord[])
      : [];

    return contracts.flatMap((contract) => {
      const price = toNumber(contract.price);
      if (price === null) {
        return [];
      }
      return [
        {
          commodity,
          contractMonth: stringValue(contract.contract_month),
          price
        }
      ];
    });
  });
}

function colorFor(commodity: string): string {
  return SERIES_COLORS[commodity] ?? "#cbd5e1";
}

function ChartEmptyState({ title, message }: { title: string; message: string }) {
  return (
    <section className="rounded-lg border border-slate-800 bg-ink-950 p-4">
      <h3 className="text-sm font-semibold text-white">{title}</h3>
      <p className="mt-3 text-sm text-slate-500">{message}</p>
    </section>
  );
}
