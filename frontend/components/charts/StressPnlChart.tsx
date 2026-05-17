import { formatUsd } from "@/lib/format";
import type { ApiRecord } from "@/lib/types";
import { bucketLabel, toNumber, topByAbsoluteValue } from "./chartUtils";

interface StressPnlChartProps {
  rows: ApiRecord[];
  totalStressPnlUsd?: unknown;
}

export function StressPnlChart({ rows, totalStressPnlUsd }: StressPnlChartProps) {
  const chartRows = topByAbsoluteValue(rows, "stress_pnl_usd", 10)
    .map((row) => ({
      label: bucketLabel(row),
      value: toNumber(row.stress_pnl_usd) ?? 0
    }))
    .filter((row) => Number.isFinite(row.value));

  if (chartRows.length === 0) {
    return <ChartEmptyState title="Stress P&L by Bucket" message="No stress P&L buckets to chart." />;
  }

  const maxAbs = Math.max(...chartRows.map((row) => Math.abs(row.value)), 1);

  return (
    <section
      aria-label="Stress P&L by Bucket chart"
      className="rounded-lg border border-slate-800 bg-ink-950 p-4"
    >
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h3 className="text-sm font-semibold text-white">Stress P&L by Bucket</h3>
        <div className="rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-xs">
          <span className="text-slate-500">Total stress P&L </span>
          <span className="font-mono text-slate-100">
            {formatUsd(totalStressPnlUsd as string | number)}
          </span>
        </div>
      </div>

      <div className="mt-4 space-y-3">
        {chartRows.map((row) => (
          <HorizontalPnlBar
            key={row.label}
            label={row.label}
            maxAbs={maxAbs}
            value={row.value}
          />
        ))}
      </div>
    </section>
  );
}

function HorizontalPnlBar({
  label,
  maxAbs,
  value
}: {
  label: string;
  maxAbs: number;
  value: number;
}) {
  const percent = Math.min((Math.abs(value) / maxAbs) * 50, 50);
  const isGain = value >= 0;

  return (
    <div className="grid gap-2 text-xs lg:grid-cols-[220px_1fr_110px] lg:items-center">
      <div className="truncate text-slate-300" title={label}>
        {label}
      </div>
      <div className="relative h-7 rounded border border-slate-800 bg-slate-950">
        <div className="absolute left-1/2 top-0 h-full w-px bg-slate-600" />
        <div
          className={`absolute top-1 h-5 rounded ${isGain ? "left-1/2 bg-emerald-500/70" : "right-1/2 bg-red-500/70"}`}
          style={{ width: `${percent}%` }}
        />
      </div>
      <div className={`font-mono ${isGain ? "text-emerald-200" : "text-red-200"}`}>
        {formatUsd(value)}
      </div>
    </div>
  );
}

function ChartEmptyState({ title, message }: { title: string; message: string }) {
  return (
    <section className="rounded-lg border border-slate-800 bg-ink-950 p-4">
      <h3 className="text-sm font-semibold text-white">{title}</h3>
      <p className="mt-3 text-sm text-slate-500">{message}</p>
    </section>
  );
}
