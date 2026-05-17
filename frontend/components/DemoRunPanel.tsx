"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { LoadingButton } from "@/components/LoadingButton";
import { ResultMetricGrid } from "@/components/ResultMetricGrid";
import {
  API_BASE_URL,
  FlowDeckApiError,
  getDemoSampleFiles,
  runSampleDemo
} from "@/lib/api";
import {
  formatBbl,
  formatDateTime,
  formatPercent,
  formatStatus,
  formatUsd,
  statusClass
} from "@/lib/format";
import type {
  DemoRunResponse,
  DemoSampleFilesResponse,
  StressScenarioName
} from "@/lib/types";

const demoStressScenarios: StressScenarioName[] = [
  "PARALLEL_DOWN_5",
  "PARALLEL_UP_5",
  "BRENT_DOWN_5",
  "BRENT_UP_5",
  "WTI_DOWN_5"
];

export function DemoRunPanel() {
  const [sampleFiles, setSampleFiles] =
    useState<DemoSampleFilesResponse | null>(null);
  const [sampleWarning, setSampleWarning] = useState<string | null>(null);
  const [targetHedgeRatio, setTargetHedgeRatio] = useState("0.80");
  const [stressScenario, setStressScenario] =
    useState<StressScenarioName>("PARALLEL_DOWN_5");
  const [isRunning, setIsRunning] = useState(false);
  const [demoResult, setDemoResult] = useState<DemoRunResponse | null>(null);
  const [demoError, setDemoError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    getDemoSampleFiles()
      .then((result) => {
        if (mounted) {
          setSampleFiles(result);
          setSampleWarning(null);
        }
      })
      .catch(() => {
        if (mounted) {
          setSampleWarning(
            "Unable to load sample file metadata. Demo run can still be attempted if the backend sample files exist."
          );
        }
      });
    return () => {
      mounted = false;
    };
  }, []);

  async function handleRunDemo() {
    setIsRunning(true);
    setDemoError(null);
    setDemoResult(null);
    try {
      const result = await runSampleDemo({
        targetHedgeRatio,
        stressScenario
      });
      setDemoResult(result);
    } catch (err) {
      setDemoError(friendlyDemoError(err));
    } finally {
      setIsRunning(false);
    }
  }

  const reportHref = demoResult?.report_url
    ? `${API_BASE_URL}${demoResult.report_url}`
    : null;

  return (
    <section className="rounded-lg border border-teal-900/60 bg-ink-900 p-5 shadow-panel">
      <div className="grid gap-5 xl:grid-cols-[1fr_340px]">
        <div>
          <div className="text-xs font-semibold uppercase text-teal-200">
            Fast demo mode
          </div>
          <h2 className="mt-2 text-xl font-semibold text-white">
            Run Sample Demo
          </h2>
          <p className="mt-2 max-w-3xl text-sm text-slate-300">
            Launch the full FlowDeck workflow using backend-owned synthetic
            Brent/WTI sample data. The backend validates data, builds curves,
            computes exposure, simulates hedge impact, runs stress P&L, writes
            run metadata, and generates the Excel workbook.
          </p>
          <p className="mt-3 rounded-md border border-slate-800 bg-ink-950 p-3 text-xs text-slate-400">
            Demo mode uses synthetic sample data only and does not execute
            trades. Manual CSV upload remains available in the Workspace for
            explicit file testing.
          </p>
        </div>

        <div className="rounded-md border border-slate-800 bg-ink-950 p-4">
          <label className="block text-sm text-slate-300">
            Target hedge ratio
            <input
              className="mt-2 w-full rounded-md border border-slate-700 bg-ink-950 px-3 py-2 text-slate-100"
              onChange={(event) => setTargetHedgeRatio(event.target.value)}
              value={targetHedgeRatio}
            />
            <span className="mt-1 block text-xs text-slate-500">
              Current: {formatPercent(targetHedgeRatio)}
            </span>
          </label>

          <label className="mt-4 block text-sm text-slate-300">
            Stress scenario
            <select
              className="mt-2 w-full rounded-md border border-slate-700 bg-ink-950 px-3 py-2 text-slate-100"
              onChange={(event) =>
                setStressScenario(event.target.value as StressScenarioName)
              }
              value={stressScenario}
            >
              {demoStressScenarios.map((scenario) => (
                <option key={scenario} value={scenario}>
                  {scenario}
                </option>
              ))}
            </select>
          </label>

          <div className="mt-4">
            <LoadingButton loading={isRunning} onClick={handleRunDemo}>
              Run Sample Demo
            </LoadingButton>
          </div>
        </div>
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-[1fr_1fr]">
        <div className="rounded-md border border-slate-800 bg-ink-950 p-4">
          <h3 className="text-sm font-semibold text-slate-200">
            Backend sample files
          </h3>
          {sampleWarning ? (
            <div className="mt-3 rounded-md border border-amber-900 bg-amber-950/30 p-3 text-xs text-amber-100">
              {sampleWarning}
            </div>
          ) : sampleFiles ? (
            <dl className="mt-3 space-y-2 text-xs">
              <SampleFileRow
                label="Market data"
                value={sampleFiles.market_data_file}
              />
              <SampleFileRow
                label="Futures positions"
                value={sampleFiles.futures_positions_file}
              />
              <SampleFileRow
                label="Physical cargoes"
                value={sampleFiles.physical_cargoes_file}
              />
            </dl>
          ) : (
            <p className="mt-3 text-xs text-slate-500">
              Loading sample file metadata...
            </p>
          )}
        </div>

        <div className="rounded-md border border-slate-800 bg-ink-950 p-4">
          <h3 className="text-sm font-semibold text-slate-200">
            Latest generated run
          </h3>
          {demoError ? (
            <div className="mt-3 rounded-md border border-red-900 bg-red-950/30 p-3 text-sm text-red-100">
              <div className="font-semibold">Demo run failed.</div>
              <p className="mt-1">{demoError}</p>
              <p className="mt-2 text-xs text-red-100/80">
                Confirm the backend is running and sample data files exist.
              </p>
            </div>
          ) : null}
          {isRunning ? (
            <p className="mt-3 text-sm text-slate-400">
              Running sample workflow...
            </p>
          ) : null}
          {demoResult ? (
            <div className="mt-3 space-y-4">
              <div className="rounded-md border border-emerald-900 bg-emerald-950/30 p-4">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <h4 className="text-base font-semibold text-emerald-100">
                      Demo run completed
                    </h4>
                    <p className="mt-1 text-sm text-emerald-100/80">
                      This is the output of the current demo session.
                    </p>
                  </div>
                  <span
                    className={`w-fit rounded-full border px-2 py-1 text-xs ${statusClass(
                      demoResult.status
                    )}`}
                  >
                    {formatStatus(demoResult.status)}
                  </span>
                </div>
              </div>
              <div className="rounded-md border border-slate-800 bg-slate-950/50 p-3">
                <div>
                  <div className="text-xs uppercase text-slate-500">Run ID</div>
                  <div className="mt-1 break-words font-mono text-base text-white">
                    {demoResult.run_id}
                  </div>
                </div>
                <div className="mt-3 text-xs text-slate-500">
                  Completed {formatDateTime(demoResult.completed_at)}
                </div>
              </div>
              <ResultMetricGrid
                metrics={[
                  {
                    label: "Curves",
                    value: demoResult.summary.number_of_curves
                  },
                  {
                    label: "Net exposure buckets",
                    value: demoResult.summary.number_of_net_exposure_buckets
                  },
                  {
                    label: "Total net exposure",
                    value: formatBbl(demoResult.summary.total_net_exposure_bbl)
                  },
                  {
                    label: "Post-hedge abs",
                    value: formatBbl(
                      demoResult.summary
                        .total_post_hedge_absolute_exposure_bbl
                    )
                  },
                  {
                    label: "Total stress P&L",
                    value: formatUsd(demoResult.summary.total_stress_pnl_usd)
                  }
                ]}
              />
              <div className="rounded-md border border-slate-800 bg-slate-950/50 p-3 text-sm text-slate-300">
                <h4 className="font-semibold text-slate-100">
                  What just happened?
                </h4>
                <p className="mt-2">
                  FlowDeck loaded synthetic Brent/WTI market data, combined
                  physical cargoes and futures positions, calculated net
                  exposure, simulated a {formatPercent(targetHedgeRatio)} hedge,
                  ran the {stressScenario} stress scenario, generated run
                  metadata, and exported an Excel report.
                </p>
              </div>
              <div className="flex flex-wrap gap-3">
                <Link
                  className="rounded-md border border-teal-700 bg-teal-500/10 px-3 py-2 text-sm font-semibold text-teal-100 hover:border-teal-400"
                  href={`/runs/${encodeURIComponent(demoResult.run_id)}`}
                >
                  View Run Detail
                </Link>
                {reportHref ? (
                  <a
                    className="rounded-md border border-teal-700 bg-teal-500/10 px-3 py-2 text-sm font-semibold text-teal-100 hover:border-teal-400"
                    href={reportHref}
                  >
                    Download Excel Report
                  </a>
                ) : null}
                <Link
                  className="rounded-md border border-slate-700 px-3 py-2 text-sm font-semibold text-slate-100 hover:border-teal-500"
                  href="/runs"
                >
                  Open Runs Dashboard
                </Link>
              </div>
              <p className="text-xs text-slate-500">
                Use the run detail page for metadata review, or download the
                Excel workbook for desk-style presentation.
              </p>
            </div>
          ) : !isRunning && !demoError ? (
            <p className="mt-3 text-sm text-slate-500">
              No sample demo has been run in this browser session yet.
            </p>
          ) : null}
        </div>
      </div>
    </section>
  );
}

function SampleFileRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-slate-500">{label}</dt>
      <dd className="mt-1 break-words font-mono text-slate-300">{value}</dd>
    </div>
  );
}

function friendlyDemoError(err: unknown): string {
  if (err instanceof FlowDeckApiError) {
    if (err.message.toLowerCase().includes("failed to fetch")) {
      return "Unable to reach the FlowDeck API. Confirm the backend is running at http://127.0.0.1:8000.";
    }
    return err.message;
  }
  if (err instanceof TypeError && String(err.message).toLowerCase().includes("fetch")) {
    return "Unable to reach the FlowDeck API. Confirm the backend is running at http://127.0.0.1:8000.";
  }
  return err instanceof Error ? err.message : "Sample demo request failed.";
}
