"use client";

import { formatBbl, formatDateTime, formatStatus, formatUsd, statusClass } from "@/lib/format";
import type { RunDetail } from "@/lib/types";

interface RunDetailPanelProps {
  run: RunDetail | null;
  loading: boolean;
  error: string | null;
  getReportUrl: (runId: string) => string;
}

export function RunDetailPanel({
  run,
  loading,
  error,
  getReportUrl
}: RunDetailPanelProps) {
  return (
    <aside className="rounded-lg border border-slate-800 bg-ink-900 p-5 shadow-panel">
      <div className="flex items-center justify-between gap-4">
        <div>
          <div className="text-sm font-medium uppercase text-slate-500">
            Run Detail
          </div>
          <h2 className="mt-2 text-lg font-semibold text-white">
            {run ? run.run_id : "Select a run"}
          </h2>
        </div>
        {run ? (
          <span
            className={`rounded-full border px-2 py-1 text-xs ${statusClass(
              run.status
            )}`}
          >
            {formatStatus(run.status)}
          </span>
        ) : null}
      </div>

      {loading ? <p className="mt-5 text-sm text-slate-300">Loading run detail...</p> : null}
      {error ? <p className="mt-5 text-sm text-red-200">{error}</p> : null}
      {!run && !loading && !error ? (
        <p className="mt-5 text-sm text-slate-400">
          Choose a row from the runs table to inspect inputs, outputs, summary
          metrics and notes.
        </p>
      ) : null}

      {run ? (
        <div className="mt-5 space-y-5 text-sm">
          <dl className="grid grid-cols-1 gap-3">
            <Detail label="Run type" value={String(run.run_type)} />
            <Detail label="Created" value={formatDateTime(run.created_at)} />
            <Detail label="Completed" value={formatDateTime(run.completed_at)} />
            <Detail
              label="Total net exposure"
              value={formatBbl(run.summary?.total_net_exposure_bbl)}
            />
            <Detail
              label="Post-hedge absolute exposure"
              value={formatBbl(run.summary?.total_post_hedge_absolute_exposure_bbl)}
            />
            <Detail
              label="Stress P&L"
              value={formatUsd(run.summary?.total_stress_pnl_usd)}
            />
          </dl>

          <Section title="Input Files" values={run.input_files} />
          <Section title="Output Files" values={run.output_files} />

          {run.errors && run.errors.length > 0 ? (
            <div>
              <h3 className="font-medium text-white">Errors</h3>
              <ul className="mt-2 list-disc space-y-1 pl-5 text-red-200">
                {run.errors.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          ) : null}

          {run.notes ? (
            <div>
              <h3 className="font-medium text-white">Notes</h3>
              <p className="mt-2 text-slate-300">{run.notes}</p>
            </div>
          ) : null}

          <a
            className="inline-flex rounded-md border border-teal-700 bg-teal-900/30 px-4 py-2 text-sm text-teal-100 hover:border-teal-500"
            href={getReportUrl(run.run_id)}
          >
            Download Excel report
          </a>
        </div>
      ) : null}
    </aside>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-4 border-b border-slate-800 pb-2">
      <dt className="text-slate-500">{label}</dt>
      <dd className="text-right text-slate-200">{value}</dd>
    </div>
  );
}

function Section({
  title,
  values
}: {
  title: string;
  values: Record<string, string | null | undefined> | undefined;
}) {
  if (!values) {
    return null;
  }

  return (
    <div>
      <h3 className="font-medium text-white">{title}</h3>
      <dl className="mt-2 space-y-2">
        {Object.entries(values).map(([key, value]) => (
          <div key={key}>
            <dt className="text-xs uppercase text-slate-500">{key}</dt>
            <dd className="break-words font-mono text-xs text-slate-300">
              {value || "-"}
            </dd>
          </div>
        ))}
      </dl>
    </div>
  );
}

