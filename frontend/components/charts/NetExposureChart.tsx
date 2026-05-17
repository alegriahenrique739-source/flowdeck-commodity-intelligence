import { formatBbl } from "@/lib/format";
import type { ApiRecord } from "@/lib/types";
import { bucketLabel, toNumber, topByAbsoluteValue } from "./chartUtils";

interface NetExposureChartProps {
  buckets: ApiRecord[];
}

export function NetExposureChart({ buckets }: NetExposureChartProps) {
  const rows = topByAbsoluteValue(buckets, "net_exposure_bbl", 10)
    .map((bucket) => ({
      label: bucketLabel(bucket),
      value: toNumber(bucket.net_exposure_bbl) ?? 0
    }))
    .filter((row) => Number.isFinite(row.value));

  if (rows.length === 0) {
    return <ChartEmptyState title="Net Exposure by Bucket" message="No net exposure buckets to chart." />;
  }

  const maxAbs = Math.max(...rows.map((row) => Math.abs(row.value)), 1);

  return (
    <section
      aria-label="Net Exposure by Bucket chart"
      className="rounded-lg border border-slate-800 bg-ink-950 p-4"
    >
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h3 className="text-sm font-semibold text-white">Net Exposure by Bucket</h3>
        <div className="flex gap-3 text-xs text-slate-400">
          <span className="text-emerald-200">Positive long</span>
          <span className="text-red-200">Negative short</span>
        </div>
      </div>

      <div className="mt-4 space-y-3">
        {rows.map((row) => (
          <HorizontalExposureBar
            formatValue={formatBbl}
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

function HorizontalExposureBar({
  formatValue,
  label,
  maxAbs,
  value
}: {
  formatValue: (value: number) => string;
  label: string;
  maxAbs: number;
  value: number;
}) {
  const percent = Math.min((Math.abs(value) / maxAbs) * 50, 50);
  const isPositive = value >= 0;

  return (
    <div className="grid gap-2 text-xs lg:grid-cols-[220px_1fr_110px] lg:items-center">
      <div className="truncate text-slate-300" title={label}>
        {label}
      </div>
      <div className="relative h-7 rounded border border-slate-800 bg-slate-950">
        <div className="absolute left-1/2 top-0 h-full w-px bg-slate-600" />
        <div
          className={`absolute top-1 h-5 rounded ${isPositive ? "left-1/2 bg-emerald-500/70" : "right-1/2 bg-red-500/70"}`}
          style={{ width: `${percent}%` }}
        />
      </div>
      <div className={`font-mono ${isPositive ? "text-emerald-200" : "text-red-200"}`}>
        {formatValue(value)}
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
