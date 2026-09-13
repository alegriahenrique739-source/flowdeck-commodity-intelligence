"use client";

import Link from "next/link";
import { isPublicDemoMode } from "@/lib/config";
import { formatBbl, formatDateTime, formatStatus, formatUsd, statusClass } from "@/lib/format";
import type { RunDetail } from "@/lib/types";

interface RunTableProps {
  runs: RunDetail[];
  onSelect: (runId: string) => void;
  getReportUrl: (runId: string) => string;
}

export function RunTable({ runs, onSelect, getReportUrl }: RunTableProps) {
  if (runs.length === 0) {
    return (
      <div className="rounded-lg border border-slate-800 bg-ink-900 p-6 text-sm text-slate-300">
        {isPublicDemoMode ? <>
          No demo runs match this view. Adjust the filters or <Link className="text-teal-200 underline" href="/demo">open Demo</Link> to generate a synthetic run.
        </> : "No local runs found. Run `python scripts/run_demo_workflow.py` from the project root, then refresh this page."}
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-slate-800 bg-ink-900 shadow-panel">
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-slate-900 text-xs uppercase text-slate-400">
            <tr>
              <th className="px-4 py-3">Run ID</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Type</th>
              <th className="px-4 py-3">Created</th>
              <th className="px-4 py-3">Completed</th>
              <th className="px-4 py-3 text-right">Curves</th>
              <th className="px-4 py-3 text-right">Buckets</th>
              <th className="px-4 py-3 text-right">Net</th>
              <th className="px-4 py-3 text-right">Post-Hedge Abs</th>
              <th className="px-4 py-3 text-right">Stress P&L</th>
              <th className="px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800 text-slate-200">
            {runs.map((run) => (
              <tr key={run.run_id} className="hover:bg-slate-900/70">
                <td className="whitespace-nowrap px-4 py-3 font-mono text-xs">
                  {run.run_id}
                </td>
                <td className="px-4 py-3">
                  <span
                    className={`rounded-full border px-2 py-1 text-xs ${statusClass(
                      run.status
                    )}`}
                  >
                    {formatStatus(run.status)}
                  </span>
                </td>
                <td className="whitespace-nowrap px-4 py-3">{run.run_type}</td>
                <td className="whitespace-nowrap px-4 py-3">
                  {formatDateTime(run.created_at)}
                </td>
                <td className="whitespace-nowrap px-4 py-3">
                  {formatDateTime(run.completed_at)}
                </td>
                <td className="px-4 py-3 text-right">
                  {run.summary?.number_of_curves ?? "-"}
                </td>
                <td className="px-4 py-3 text-right">
                  {run.summary?.number_of_net_exposure_buckets ?? "-"}
                </td>
                <td className="whitespace-nowrap px-4 py-3 text-right">
                  {formatBbl(run.summary?.total_net_exposure_bbl)}
                </td>
                <td className="whitespace-nowrap px-4 py-3 text-right">
                  {formatBbl(run.summary?.total_post_hedge_absolute_exposure_bbl)}
                </td>
                <td className="whitespace-nowrap px-4 py-3 text-right">
                  {formatUsd(run.summary?.total_stress_pnl_usd)}
                </td>
                <td className="whitespace-nowrap px-4 py-3">
                  <div className="flex gap-2">
                    <button
                      className="rounded-md border border-slate-700 px-3 py-2 text-xs text-slate-100 hover:border-slate-500"
                      onClick={() => onSelect(run.run_id)}
                      type="button"
                    >
                      View details
                    </button>
                    <Link
                      className="rounded-md border border-slate-700 px-3 py-2 text-xs text-slate-100 hover:border-slate-500"
                      href={`/runs/${encodeURIComponent(run.run_id)}`}
                    >
                      Open run page
                    </Link>
                    <a
                      className="rounded-md border border-teal-700 bg-teal-900/30 px-3 py-2 text-xs text-teal-100 hover:border-teal-500"
                      href={getReportUrl(run.run_id)}
                    >
                      Download Excel
                    </a>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
