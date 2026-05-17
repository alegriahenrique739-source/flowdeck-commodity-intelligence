"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { LayoutShell } from "@/components/LayoutShell";
import { MetricCard } from "@/components/MetricCard";
import { getRun, getRunReportUrl } from "@/lib/api";
import {
  formatBbl,
  formatDateTime,
  formatStatus,
  formatUsd,
  statusClass
} from "@/lib/format";
import type { RunDetail } from "@/lib/types";

export default function RunDetailPage({
  params
}: {
  params: { runId: string };
}) {
  const runId = decodeURIComponent(params.runId);
  const [run, setRun] = useState<RunDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    setError(null);
    getRun(runId)
      .then((result) => {
        if (mounted) {
          setRun(result);
        }
      })
      .catch((err) => {
        if (mounted) {
          setError(err instanceof Error ? err.message : "Unable to load run.");
        }
      })
      .finally(() => {
        if (mounted) {
          setLoading(false);
        }
      });

    return () => {
      mounted = false;
    };
  }, [runId]);

  return (
    <LayoutShell>
      <section className="rounded-lg border border-slate-800 bg-ink-900 p-7 shadow-panel">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <div className="text-sm font-semibold uppercase text-teal-200">
              Local run record
            </div>
            <h1 className="mt-3 text-3xl font-semibold tracking-normal text-white md:text-4xl">
              Run Detail
            </h1>
            <div className="mt-3 break-words font-mono text-sm text-teal-100 md:text-base">
              {run?.run_id || runId}
            </div>
            <p className="mt-4 max-w-3xl text-sm text-slate-300">
              This page is a read-only report card for one backend-created
              FlowDeck workflow run: timestamps, input files, output files,
              summary metrics, notes, errors, and the run-scoped Excel report.
            </p>
          </div>
          {run ? (
            <span
              className={`w-fit rounded-full border px-3 py-2 text-sm ${statusClass(
                run.status
              )}`}
            >
              {formatStatus(run.status)}
            </span>
          ) : null}
        </div>

        <div className="mt-6 flex flex-wrap gap-3">
          {run ? (
            <a
              className="rounded-md border border-teal-600 bg-teal-500/15 px-4 py-2 text-sm font-semibold text-teal-50 shadow-panel hover:border-teal-300"
              href={getRunReportUrl(run.run_id)}
            >
              Download Excel Report
            </a>
          ) : null}
          <Link
            className="rounded-md border border-slate-700 px-3 py-2 text-sm font-semibold text-slate-100 hover:border-slate-500"
            href="/runs"
          >
            Back to Runs
          </Link>
          <Link
            className="rounded-md border border-slate-700 px-3 py-2 text-sm font-semibold text-slate-100 hover:border-slate-500"
            href="/demo"
          >
            Back to Demo
          </Link>
          <Link
            className="rounded-md border border-slate-700 px-3 py-2 text-sm font-semibold text-slate-100 hover:border-slate-500"
            href="/workspace"
          >
            Back to Workspace
          </Link>
        </div>
      </section>

      {loading ? (
        <div className="mt-6 rounded-lg border border-slate-800 bg-ink-900 p-6 text-sm text-slate-300">
          Loading run metadata...
        </div>
      ) : null}

      {error ? (
        <div className="mt-6 rounded-lg border border-red-900 bg-red-950/40 p-6 text-sm text-red-100">
          <h2 className="text-lg font-semibold text-red-100">
            Unable to load run.
          </h2>
          <p className="mt-2">{error}</p>
        </div>
      ) : null}

      {run ? (
        <div className="mt-6 space-y-6">
          <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
            <MetricCard
              label="Curves"
              value={run.summary?.number_of_curves ?? "-"}
            />
            <MetricCard
              label="Exposure Buckets"
              value={run.summary?.number_of_net_exposure_buckets ?? "-"}
            />
            <MetricCard
              label="Total Net"
              value={formatBbl(run.summary?.total_net_exposure_bbl)}
            />
            <MetricCard
              label="Post-Hedge Abs"
              value={formatBbl(
                run.summary?.total_post_hedge_absolute_exposure_bbl
              )}
            />
            <MetricCard
              label="Stress P&L"
              value={formatUsd(run.summary?.total_stress_pnl_usd)}
            />
          </section>

          <section className="grid gap-6 lg:grid-cols-[1fr_1fr]">
            <div className="rounded-lg border border-slate-800 bg-ink-900 p-5 shadow-panel">
              <h2 className="text-lg font-semibold text-white">
                Run Metadata
              </h2>
              <dl className="mt-4 space-y-3 text-sm">
                <Detail label="Run ID" value={run.run_id} />
                <Detail label="Status" value={formatStatus(run.status)} />
                <Detail label="Run type" value={String(run.run_type)} />
                <Detail label="Created" value={formatDateTime(run.created_at)} />
                <Detail
                  label="Completed"
                  value={formatDateTime(run.completed_at)}
                />
              </dl>
            </div>

            <div className="rounded-lg border border-slate-800 bg-ink-900 p-5 shadow-panel">
              <h2 className="text-lg font-semibold text-white">
                Files And Notes
              </h2>
              <FileSection title="Input Files" values={run.input_files} />
              <FileSection title="Output Files" values={run.output_files} />
              {run.notes ? (
                <div className="mt-5">
                  <h3 className="text-sm font-semibold text-slate-100">Notes</h3>
                  <p className="mt-2 text-sm text-slate-300">{run.notes}</p>
                </div>
              ) : null}
            </div>
          </section>

          <section className="rounded-lg border border-slate-800 bg-ink-900 p-5 shadow-panel">
            <h2 className="text-lg font-semibold text-white">Errors</h2>
            {run.errors && run.errors.length > 0 ? (
              <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-red-200">
                {run.errors.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            ) : (
              <p className="mt-3 text-sm text-slate-400">
                No errors recorded for this run.
              </p>
            )}
          </section>
        </div>
      ) : null}
    </LayoutShell>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-start justify-between gap-4 border-b border-slate-800 pb-3">
      <dt className="text-slate-500">{label}</dt>
      <dd className="break-words text-right font-mono text-slate-200">{value}</dd>
    </div>
  );
}

function FileSection({
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
    <div className="mt-4">
      <h3 className="text-sm font-semibold text-slate-100">{title}</h3>
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
