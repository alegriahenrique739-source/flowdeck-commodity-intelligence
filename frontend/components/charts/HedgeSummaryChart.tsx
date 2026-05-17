import { formatBbl, formatPercent } from "@/lib/format";
import type { ApiRecord } from "@/lib/types";
import { toNumber } from "./chartUtils";

interface HedgeSummaryChartProps {
  summary: ApiRecord;
}

export function HedgeSummaryChart({ summary }: HedgeSummaryChartProps) {
  const currentAbs =
    toNumber(summary.total_current_absolute_net_exposure_bbl) ?? 0;
  const postAbs =
    toNumber(summary.total_post_hedge_absolute_net_exposure_bbl) ?? 0;
  const reduction = Math.max(currentAbs - postAbs, 0);
  const reductionRatio = currentAbs > 0 ? reduction / currentAbs : 0;
  const maxValue = Math.max(currentAbs, postAbs, 1);

  return (
    <section
      aria-label="Hedge Impact chart"
      className="rounded-lg border border-slate-800 bg-ink-950 p-4"
    >
      <h3 className="text-sm font-semibold text-white">Hedge Impact</h3>
      <div className="mt-4 grid gap-3 md:grid-cols-3">
        <Metric label="Current absolute net" value={formatBbl(currentAbs)} />
        <Metric label="Post-hedge absolute net" value={formatBbl(postAbs)} />
        <Metric label="Presentation reduction" value={formatPercent(reductionRatio)} />
      </div>
      <div className="mt-5 space-y-3">
        <ComparisonBar label="Before hedge" maxValue={maxValue} value={currentAbs} />
        <ComparisonBar label="After hedge" maxValue={maxValue} value={postAbs} />
      </div>
      <p className="mt-3 text-xs text-slate-500">
        Reduction percentage is frontend presentation only; recommendations come
        from the backend hedge simulator.
      </p>
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-slate-800 bg-slate-950 p-3">
      <div className="text-xs uppercase text-slate-500">{label}</div>
      <div className="mt-1 font-mono text-sm text-slate-100">{value}</div>
    </div>
  );
}

function ComparisonBar({
  label,
  maxValue,
  value
}: {
  label: string;
  maxValue: number;
  value: number;
}) {
  const width = Math.max((value / maxValue) * 100, 2);

  return (
    <div className="grid gap-2 text-xs sm:grid-cols-[130px_1fr_110px] sm:items-center">
      <div className="text-slate-300">{label}</div>
      <div className="h-7 rounded border border-slate-800 bg-slate-950">
        <div className="h-full rounded bg-teal-500/70" style={{ width: `${width}%` }} />
      </div>
      <div className="font-mono text-slate-200">{formatBbl(value)}</div>
    </div>
  );
}
