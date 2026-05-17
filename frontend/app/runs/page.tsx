"use client";

import { useEffect, useMemo, useState } from "react";
import { LayoutShell } from "@/components/LayoutShell";
import { MetricCard } from "@/components/MetricCard";
import { RunDetailPanel } from "@/components/RunDetailPanel";
import { RunTable } from "@/components/RunTable";
import { getRun, getRunReportUrl, getRuns } from "@/lib/api";
import { formatBbl, formatUsd } from "@/lib/format";
import type { RunDetail, RunStatus, RunType } from "@/lib/types";

const limits = [5, 10, 20, 50];

export default function RunsPage() {
  const [runs, setRuns] = useState<RunDetail[]>([]);
  const [selectedRun, setSelectedRun] = useState<RunDetail | null>(null);
  const [status, setStatus] = useState<RunStatus | "">("");
  const [runType, setRunType] = useState<RunType | "">("");
  const [limit, setLimit] = useState(20);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [detailError, setDetailError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    async function loadRuns() {
      setLoading(true);
      setError(null);
      try {
        const payload = await getRuns({
          limit,
          status,
          run_type: runType
        });
        if (isMounted) {
          setRuns(payload.runs);
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "Unable to load runs.");
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    loadRuns();
    return () => {
      isMounted = false;
    };
  }, [limit, status, runType]);

  async function handleSelect(runId: string) {
    setDetailLoading(true);
    setDetailError(null);
    try {
      const run = await getRun(runId);
      setSelectedRun(run);
    } catch (err) {
      setDetailError(
        err instanceof Error ? err.message : "Unable to load run detail."
      );
    } finally {
      setDetailLoading(false);
    }
  }

  const totals = useMemo(() => {
    const buckets = runs.reduce(
      (total, run) => total + Number(run.summary?.number_of_net_exposure_buckets || 0),
      0
    );
    const totalNet = runs.reduce(
      (total, run) => total + Number(run.summary?.total_net_exposure_bbl || 0),
      0
    );
    const stress = runs.reduce(
      (total, run) => total + Number(run.summary?.total_stress_pnl_usd || 0),
      0
    );
    return { buckets, totalNet, stress };
  }, [runs]);

  return (
    <LayoutShell>
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-white">Runs Dashboard</h1>
          <p className="mt-2 text-sm text-slate-400">
            Read-only local workflow metadata from the FastAPI backend.
          </p>
        </div>
      </div>

      <section className="mt-6 grid gap-4 md:grid-cols-3">
        <MetricCard label="Runs Loaded" value={runs.length} />
        <MetricCard label="Exposure Buckets" value={totals.buckets} />
        <MetricCard label="Total Net" value={formatBbl(totals.totalNet)} />
        <MetricCard label="Stress P&L" value={formatUsd(totals.stress)} />
      </section>

      <section className="mt-6 rounded-lg border border-slate-800 bg-ink-900 p-4">
        <div className="grid gap-4 md:grid-cols-4">
          <label className="text-sm text-slate-300">
            Status
            <select
              className="mt-2 w-full rounded-md border border-slate-700 bg-ink-950 px-3 py-2 text-slate-100"
              onChange={(event) => setStatus(event.target.value as RunStatus | "")}
              value={status}
            >
              <option value="">All</option>
              <option value="SUCCESS">SUCCESS</option>
              <option value="FAILED">FAILED</option>
              <option value="RUNNING">RUNNING</option>
            </select>
          </label>
          <label className="text-sm text-slate-300">
            Run type
            <select
              className="mt-2 w-full rounded-md border border-slate-700 bg-ink-950 px-3 py-2 text-slate-100"
              onChange={(event) => setRunType(event.target.value as RunType | "")}
              value={runType}
            >
              <option value="">All</option>
              <option value="DEMO_WORKFLOW">DEMO_WORKFLOW</option>
            </select>
          </label>
          <label className="text-sm text-slate-300">
            Limit
            <select
              className="mt-2 w-full rounded-md border border-slate-700 bg-ink-950 px-3 py-2 text-slate-100"
              onChange={(event) => setLimit(Number(event.target.value))}
              value={limit}
            >
              {limits.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>
          <div className="flex items-end text-sm text-slate-400">
            {loading ? "Loading runs..." : `${runs.length} run records displayed`}
          </div>
        </div>
      </section>

      {error ? (
        <div className="mt-6 rounded-lg border border-red-900 bg-red-950/40 p-4 text-sm text-red-100">
          {error}
        </div>
      ) : null}

      <section className="mt-6 grid gap-6 xl:grid-cols-[1fr_360px]">
        <RunTable
          getReportUrl={getRunReportUrl}
          onSelect={handleSelect}
          runs={runs}
        />
        <RunDetailPanel
          error={detailError}
          getReportUrl={getRunReportUrl}
          loading={detailLoading}
          run={selectedRun}
        />
      </section>
    </LayoutShell>
  );
}

