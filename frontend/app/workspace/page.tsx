"use client";

import { useState } from "react";
import { ApiStatusCard } from "@/components/ApiStatusCard";
import { DemoRunPanel } from "@/components/DemoRunPanel";
import { ErrorBanner } from "@/components/ErrorBanner";
import { FileUploadCard } from "@/components/FileUploadCard";
import { LayoutShell } from "@/components/LayoutShell";
import { LoadingButton } from "@/components/LoadingButton";
import { RawJsonDetails } from "@/components/RawJsonDetails";
import { ResultMetricGrid } from "@/components/ResultMetricGrid";
import { ResultTable } from "@/components/ResultTable";
import { ValidationIssueList } from "@/components/ValidationIssueList";
import { WorkspaceStepCard } from "@/components/WorkspaceStepCard";
import { ForwardCurveChart } from "@/components/charts/ForwardCurveChart";
import { HedgeSummaryChart } from "@/components/charts/HedgeSummaryChart";
import { NetExposureChart } from "@/components/charts/NetExposureChart";
import { StressPnlChart } from "@/components/charts/StressPnlChart";
import {
  FlowDeckApiError,
  analyzeFutures,
  analyzePhysical,
  buildCurves,
  computeNetExposure,
  generateExcelReport,
  runStress,
  simulateHedge,
  validateMarketData
} from "@/lib/api";
import {
  formatBbl,
  formatLots,
  formatPercent,
  formatUsd
} from "@/lib/format";
import type {
  CurvesBuildResponse,
  FuturesAnalyzeResponse,
  HedgeSimulationResponse,
  MarketDataValidationResponse,
  NetExposureResponse,
  PhysicalAnalyzeResponse,
  StressResponse,
  StressScenarioName
} from "@/lib/types";

type LoadingKey =
  | "validate"
  | "curves"
  | "futures"
  | "physical"
  | "net"
  | "hedge"
  | "stress"
  | "report";

type StepStatus = "Not started" | "Ready" | "Running" | "Complete" | "Error";

const stressScenarios: StressScenarioName[] = [
  "PARALLEL_DOWN_5",
  "PARALLEL_UP_5",
  "BRENT_DOWN_5",
  "BRENT_UP_5",
  "WTI_DOWN_5"
];

export default function WorkspacePage() {
  const [marketFile, setMarketFile] = useState<File | null>(null);
  const [futuresFile, setFuturesFile] = useState<File | null>(null);
  const [physicalFile, setPhysicalFile] = useState<File | null>(null);
  const [loading, setLoading] = useState<LoadingKey | null>(null);
  const [activeError, setActiveError] = useState<string | null>(null);
  const [reportMessage, setReportMessage] = useState<string | null>(null);
  const [stepErrors, setStepErrors] = useState<Partial<Record<LoadingKey, string>>>({});
  const [stepIssues, setStepIssues] = useState<Partial<Record<LoadingKey, unknown[]>>>({});

  const [marketResult, setMarketResult] =
    useState<MarketDataValidationResponse | null>(null);
  const [curvesResult, setCurvesResult] = useState<CurvesBuildResponse | null>(null);
  const [futuresResult, setFuturesResult] =
    useState<FuturesAnalyzeResponse | null>(null);
  const [physicalResult, setPhysicalResult] =
    useState<PhysicalAnalyzeResponse | null>(null);
  const [netResult, setNetResult] = useState<NetExposureResponse | null>(null);
  const [hedgeResult, setHedgeResult] =
    useState<HedgeSimulationResponse | null>(null);
  const [stressResult, setStressResult] = useState<StressResponse | null>(null);

  const [targetHedgeRatio, setTargetHedgeRatio] = useState("0.80");
  const [contractSizeBbl, setContractSizeBbl] = useState("1000");
  const [stressScenario, setStressScenario] =
    useState<StressScenarioName>("PARALLEL_DOWN_5");

  const allFilesSelected = Boolean(marketFile && futuresFile && physicalFile);
  const positionFilesSelected = Boolean(futuresFile && physicalFile);

  async function runStep(key: LoadingKey, action: () => Promise<void>) {
    setLoading(key);
    setActiveError(null);
    setReportMessage(null);
    setStepErrors((current) => ({ ...current, [key]: undefined }));
    setStepIssues((current) => ({ ...current, [key]: undefined }));
    try {
      await action();
    } catch (err) {
      const message = friendlyError(err);
      setActiveError(message);
      setStepErrors((current) => ({ ...current, [key]: message }));
      if (err instanceof FlowDeckApiError && err.errors.length > 0) {
        setStepIssues((current) => ({ ...current, [key]: err.errors }));
      }
    } finally {
      setLoading(null);
    }
  }

  function setMarketUpload(file: File | null) {
    setMarketFile(file);
    setMarketResult(null);
    setCurvesResult(null);
    clearStepState(["validate", "curves", "report"]);
  }

  function setFuturesUpload(file: File | null) {
    setFuturesFile(file);
    setFuturesResult(null);
    setNetResult(null);
    setHedgeResult(null);
    setStressResult(null);
    clearStepState(["futures", "net", "hedge", "stress", "report"]);
  }

  function setPhysicalUpload(file: File | null) {
    setPhysicalFile(file);
    setPhysicalResult(null);
    setNetResult(null);
    setHedgeResult(null);
    setStressResult(null);
    clearStepState(["physical", "net", "hedge", "stress", "report"]);
  }

  function clearStepState(keys: LoadingKey[]) {
    setActiveError(null);
    setReportMessage(null);
    setStepErrors((current) => {
      const next = { ...current };
      keys.forEach((key) => delete next[key]);
      return next;
    });
    setStepIssues((current) => {
      const next = { ...current };
      keys.forEach((key) => delete next[key]);
      return next;
    });
  }

  const uploadStatus = allFilesSelected ? "Complete" : "Ready";
  const validateStatus = stepStatus("validate", Boolean(marketFile), Boolean(marketResult));
  const curvesStatus = stepStatus("curves", Boolean(marketFile), Boolean(curvesResult));
  const futuresStatus = stepStatus("futures", Boolean(futuresFile), Boolean(futuresResult));
  const physicalStatus = stepStatus("physical", Boolean(physicalFile), Boolean(physicalResult));
  const positionsComplete = Boolean(futuresResult && physicalResult);
  const netStatus = stepStatus("net", positionFilesSelected, Boolean(netResult));
  const hedgeStatus = stepStatus("hedge", positionFilesSelected, Boolean(hedgeResult));
  const stressStatus = stepStatus("stress", positionFilesSelected, Boolean(stressResult));
  const reportStatus = stepStatus("report", allFilesSelected, Boolean(reportMessage));

  function stepStatus(
    key: LoadingKey,
    ready: boolean,
    complete: boolean
  ): StepStatus {
    if (stepErrors[key]) {
      return "Error";
    }
    if (loading === key) {
      return "Running";
    }
    if (complete) {
      return "Complete";
    }
    return ready ? "Ready" : "Not started";
  }

  return (
    <LayoutShell>
      <div className="grid gap-6 xl:grid-cols-[1fr_380px]">
        <section>
          <div className="rounded-lg border border-slate-800 bg-ink-900 p-7 shadow-panel">
            <div className="text-sm font-medium uppercase text-teal-200">
              CSV Analytics Workspace
            </div>
            <h1 className="mt-3 text-3xl font-semibold tracking-normal text-white">
              Analytics Workspace
            </h1>
            <p className="mt-3 max-w-3xl text-sm text-slate-300">
              Upload synthetic sample CSV files, call the existing FastAPI
              services, inspect backend outputs, and generate an Excel workbook.
            </p>
          </div>
        </section>
        <ApiStatusCard />
      </div>

      <div className="mt-6">
        <DemoRunPanel />
      </div>

      <section className="mt-6 rounded-lg border border-slate-800 bg-ink-900 p-5 shadow-panel">
        <h2 className="text-lg font-semibold text-white">Use sample files</h2>
        <p className="mt-2 text-sm text-slate-400">
          Browser upload still requires selecting these files manually from your
          local FlowDeck project folder.
        </p>
        <dl className="mt-4 grid gap-3 text-xs md:grid-cols-3">
          <SamplePath
            label="Market data"
            value="data/sample/market_data/valid_brent_wti_futures.csv"
          />
          <SamplePath
            label="Futures positions"
            value="data/sample/positions/valid_futures_positions.csv"
          />
          <SamplePath
            label="Physical cargoes"
            value="data/sample/positions/valid_physical_cargoes.csv"
          />
        </dl>
      </section>

      <div className="mt-6">
        <ErrorBanner message={activeError} />
      </div>

      <div className="mt-6 space-y-6">
        <WorkspaceStepCard
          description="Choose the three synthetic CSV inputs used by the workflow."
          eyebrow="Step 1"
          requiredInputs={["Market data CSV", "Futures positions CSV", "Physical cargoes CSV"]}
          status={uploadStatus}
          title="Upload CSV Files"
        >
          <section className="grid gap-4 xl:grid-cols-3">
            <FileUploadCard
              description="Forward curve market data input."
              file={marketFile}
              onChange={setMarketUpload}
              samplePath="data/sample/market_data/valid_brent_wti_futures.csv"
              status={marketFile ? "selected" : "required"}
              title="Market Data CSV"
            />
            <FileUploadCard
              description="Paper futures positions input."
              file={futuresFile}
              onChange={setFuturesUpload}
              samplePath="data/sample/positions/valid_futures_positions.csv"
              status={futuresFile ? "selected" : "required"}
              title="Futures Positions CSV"
            />
            <FileUploadCard
              description="Simplified physical cargoes input."
              file={physicalFile}
              onChange={setPhysicalUpload}
              samplePath="data/sample/positions/valid_physical_cargoes.csv"
              status={physicalFile ? "selected" : "required"}
              title="Physical Cargoes CSV"
            />
          </section>
        </WorkspaceStepCard>

        <WorkspaceStepCard
          action={actionButton({
            disabled: !marketFile,
            helper: marketFile ? "Ready to validate market data." : "Select Market Data CSV first.",
            label: "Validate market data",
            loading: loading === "validate",
            onClick: () =>
              marketFile &&
              runStep("validate", async () => {
                setMarketResult(await validateMarketData(marketFile));
              })
          })}
          description="Checks required columns, date parsing, duplicate curve points and supported units."
          eyebrow="Step 2"
          requiredInputs={["Market Data CSV"]}
          status={validateStatus}
          title="Validate Market Data"
        >
          <ValidationIssueList issues={marketResult?.errors} />
          <ValidationIssueList issues={stepIssues.validate} />
          <ResultMetricGrid
            metrics={[
              { label: "Valid", value: marketResult ? String(marketResult.valid) : "-" },
              { label: "Rows", value: marketResult?.row_count ?? "-" },
              { label: "Errors", value: marketResult?.errors.length ?? "-" }
            ]}
          />
          <ResultTable
            columns={["valuation_date", "commodity", "contract_code", "contract_month", "price"]}
            maxRows={5}
            rows={marketResult?.preview_rows ?? []}
          />
          <RawJsonDetails data={marketResult} />
        </WorkspaceStepCard>

        <WorkspaceStepCard
          action={actionButton({
            disabled: !marketFile,
            helper: marketFile ? "Ready to build forward curves." : "Select Market Data CSV first.",
            label: "Build forward curves",
            loading: loading === "curves",
            onClick: () =>
              marketFile &&
              runStep("curves", async () => {
                setCurvesResult(await buildCurves(marketFile));
              })
          })}
          description="Calls the backend curve builder and calendar spread service."
          eyebrow="Step 3"
          requiredInputs={["Market Data CSV"]}
          status={curvesStatus}
          title="Build Forward Curves"
        >
          <ValidationIssueList issues={stepIssues.curves} />
          <ResultMetricGrid
            metrics={[
              { label: "Curves", value: curvesResult?.curve_summaries.length ?? "-" },
              { label: "Spreads", value: curvesResult?.calendar_spreads.length ?? "-" }
            ]}
          />
          {curvesResult ? (
            <ForwardCurveChart curves={curvesResult.curve_summaries} />
          ) : null}
          <ResultTable
            columns={["valuation_date", "commodity", "front_month_contract", "curve_shape"]}
            maxRows={5}
            rows={curvesResult?.curve_summaries ?? []}
          />
          <RawJsonDetails data={curvesResult} />
        </WorkspaceStepCard>

        <WorkspaceStepCard
          description="Validate futures and physical cargo CSV files separately, then review exposure summaries."
          eyebrow="Step 4"
          requiredInputs={["Futures Positions CSV", "Physical Cargoes CSV"]}
          status={positionsComplete ? "Complete" : futuresStatus === "Error" || physicalStatus === "Error" ? "Error" : futuresFile || physicalFile ? "Ready" : "Not started"}
          title="Analyze Positions"
        >
          <div className="grid gap-3 md:grid-cols-2">
            {actionButton({
              disabled: !futuresFile,
              helper: futuresFile ? "Ready to analyze futures." : "Select Futures Positions CSV first.",
              label: "Analyze futures",
              loading: loading === "futures",
              onClick: () =>
                futuresFile &&
                runStep("futures", async () => {
                  setFuturesResult(await analyzeFutures(futuresFile));
                })
            })}
            {actionButton({
              disabled: !physicalFile,
              helper: physicalFile ? "Ready to analyze physical cargoes." : "Select Physical Cargoes CSV first.",
              label: "Analyze physical",
              loading: loading === "physical",
              onClick: () =>
                physicalFile &&
                runStep("physical", async () => {
                  setPhysicalResult(await analyzePhysical(physicalFile));
                })
            })}
          </div>
          <ValidationIssueList issues={stepIssues.futures} />
          <ValidationIssueList issues={stepIssues.physical} />
          <ResultMetricGrid
            metrics={[
              { label: "Futures rows", value: futuresResult?.row_count ?? "-" },
              {
                label: "Futures net",
                value: formatBbl(futuresResult?.summary?.total_net_exposure_bbl as string | number)
              },
              { label: "Physical rows", value: physicalResult?.row_count ?? "-" },
              {
                label: "Physical net",
                value: formatBbl(
                  physicalResult?.summary?.total_net_physical_exposure_bbl as string | number
                )
              }
            ]}
          />
          <RawJsonDetails data={{ futuresResult, physicalResult }} />
        </WorkspaceStepCard>

        <WorkspaceStepCard
          action={actionButton({
            disabled: !positionFilesSelected,
            helper: positionFilesSelected
              ? "Ready to compute hedgeable net exposure."
              : "Select Futures Positions and Physical Cargoes CSVs first.",
            label: "Compute net exposure",
            loading: loading === "net",
            onClick: () =>
              futuresFile &&
              physicalFile &&
              runStep("net", async () => {
                setNetResult(await computeNetExposure(futuresFile, physicalFile));
              })
          })}
          description="Combines futures and physical exposure into hedgeable monthly buckets."
          eyebrow="Step 5"
          requiredInputs={["Futures Positions CSV", "Physical Cargoes CSV"]}
          status={netStatus}
          title="Compute Net Exposure"
        >
          <ValidationIssueList issues={stepIssues.net} />
          <ResultMetricGrid
            metrics={[
              {
                label: "Total net",
                value: formatBbl(netResult?.summary?.total_net_exposure_bbl as string | number)
              },
              {
                label: "Absolute net",
                value: formatBbl(netResult?.summary?.total_absolute_net_exposure_bbl as string | number)
              },
              {
                label: "Gross component",
                value: formatBbl(netResult?.summary?.total_gross_component_exposure_bbl as string | number)
              },
              {
                label: "Buckets",
                value: String(netResult?.summary?.number_of_exposure_buckets ?? "-")
              }
            ]}
          />
          {netResult ? (
            <NetExposureChart buckets={netResult.net_exposure_buckets} />
          ) : null}
          <ResultTable
            columns={["hedge_index", "exposure_month", "book", "net_exposure_bbl"]}
            maxRows={8}
            rows={netResult?.net_exposure_buckets ?? []}
          />
          <RawJsonDetails data={netResult} />
        </WorkspaceStepCard>

        <WorkspaceStepCard
          action={actionButton({
            disabled: !positionFilesSelected,
            helper: positionFilesSelected
              ? "Ready to simulate deterministic hedge recommendations."
              : "Select Futures Positions and Physical Cargoes CSVs first.",
            label: "Simulate hedge",
            loading: loading === "hedge",
            onClick: () =>
              futuresFile &&
              physicalFile &&
              runStep("hedge", async () => {
                setHedgeResult(
                  await simulateHedge(
                    futuresFile,
                    physicalFile,
                    targetHedgeRatio,
                    contractSizeBbl
                  )
                );
              })
          })}
          description="Uses backend hedge simulation against net exposure buckets."
          eyebrow="Step 6"
          requiredInputs={["Futures Positions CSV", "Physical Cargoes CSV"]}
          status={hedgeStatus}
          title="Simulate Hedge"
        >
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="text-sm text-slate-300">
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
            <label className="text-sm text-slate-300">
              Contract size bbl
              <input
                className="mt-2 w-full rounded-md border border-slate-700 bg-ink-950 px-3 py-2 text-slate-100"
                onChange={(event) => setContractSizeBbl(event.target.value)}
                value={contractSizeBbl}
              />
            </label>
          </div>
          <ValidationIssueList issues={stepIssues.hedge} />
          <ResultMetricGrid
            metrics={[
              {
                label: "Current abs net",
                value: formatBbl(
                  hedgeResult?.hedge_summary?.total_current_absolute_net_exposure_bbl as string | number
                )
              },
              {
                label: "Post-hedge abs",
                value: formatBbl(
                  hedgeResult?.hedge_summary?.total_post_hedge_absolute_net_exposure_bbl as string | number
                )
              },
              {
                label: "Lots",
                value: formatLots(hedgeResult?.hedge_summary?.total_recommended_lots_abs as string | number)
              }
            ]}
          />
          {hedgeResult ? (
            <HedgeSummaryChart summary={hedgeResult.hedge_summary} />
          ) : null}
          <ResultTable
            columns={["hedge_index", "exposure_month", "recommended_direction", "recommended_lots_rounded"]}
            maxRows={8}
            rows={hedgeResult?.hedge_recommendations ?? []}
          />
          <RawJsonDetails data={hedgeResult} />
        </WorkspaceStepCard>

        <WorkspaceStepCard
          action={actionButton({
            disabled: !positionFilesSelected,
            helper: positionFilesSelected
              ? "Ready to run the selected stress scenario."
              : "Select Futures Positions and Physical Cargoes CSVs first.",
            label: "Run stress P&L",
            loading: loading === "stress",
            onClick: () =>
              futuresFile &&
              physicalFile &&
              runStep("stress", async () => {
                setStressResult(await runStress(futuresFile, physicalFile, stressScenario));
              })
          })}
          description="Runs a predefined synthetic backend stress scenario."
          eyebrow="Step 7"
          requiredInputs={["Futures Positions CSV", "Physical Cargoes CSV"]}
          status={stressStatus}
          title="Run Stress P&L"
        >
          <label className="block text-sm text-slate-300">
            Scenario
            <select
              className="mt-2 w-full rounded-md border border-slate-700 bg-ink-950 px-3 py-2 text-slate-100"
              onChange={(event) => setStressScenario(event.target.value as StressScenarioName)}
              value={stressScenario}
            >
              {stressScenarios.map((scenario) => (
                <option key={scenario} value={scenario}>
                  {scenario}
                </option>
              ))}
            </select>
          </label>
          <ValidationIssueList issues={stepIssues.stress} />
          <ResultMetricGrid
            metrics={[
              {
                label: "Total stress P&L",
                value: formatUsd(stressResult?.stress_summary?.total_stress_pnl_usd as string | number)
              },
              {
                label: "Gain buckets",
                value: String(stressResult?.stress_summary?.number_of_gain_buckets ?? "-")
              },
              {
                label: "Loss buckets",
                value: String(stressResult?.stress_summary?.number_of_loss_buckets ?? "-")
              },
              {
                label: "Flat buckets",
                value: String(stressResult?.stress_summary?.number_of_flat_buckets ?? "-")
              }
            ]}
          />
          {stressResult ? (
            <StressPnlChart
              rows={stressResult.stress_bucket_results}
              totalStressPnlUsd={stressResult.stress_summary?.total_stress_pnl_usd}
            />
          ) : null}
          <ResultTable
            columns={["hedge_index", "exposure_month", "price_delta_usd_per_bbl", "stress_pnl_usd", "pnl_direction"]}
            maxRows={8}
            rows={stressResult?.stress_bucket_results ?? []}
          />
          <RawJsonDetails data={stressResult} />
        </WorkspaceStepCard>

        <WorkspaceStepCard
          action={actionButton({
            disabled: !allFilesSelected,
            helper: allFilesSelected
              ? "Ready to generate and download the Excel workbook."
              : "Select all three CSV files first.",
            label: "Generate Excel Report",
            loading: loading === "report",
            onClick: () =>
              marketFile &&
              futuresFile &&
              physicalFile &&
              runStep("report", async () => {
                await generateExcelReport(
                  marketFile,
                  futuresFile,
                  physicalFile,
                  targetHedgeRatio,
                  stressScenario
                );
                setReportMessage("Excel report download started.");
              })
          })}
          description="Calls the existing backend Excel export endpoint and downloads the workbook."
          eyebrow="Step 8"
          requiredInputs={["Market Data CSV", "Futures Positions CSV", "Physical Cargoes CSV"]}
          status={reportStatus}
          title="Generate Excel Report"
        >
          <ResultMetricGrid
            metrics={[
              { label: "Hedge ratio", value: formatPercent(targetHedgeRatio) },
              { label: "Stress scenario", value: stressScenario },
              { label: "Filename", value: "flowdeck_workspace_report.xlsx" }
            ]}
          />
          <ValidationIssueList issues={stepIssues.report} />
          {reportMessage ? (
            <div className="rounded-md border border-emerald-900 bg-emerald-950/30 p-4 text-sm text-emerald-100">
              {reportMessage}
            </div>
          ) : (
            <p className="text-sm text-slate-400">
              The workbook is generated by the backend and downloaded as
              flowdeck_workspace_report.xlsx.
            </p>
          )}
        </WorkspaceStepCard>
      </div>
    </LayoutShell>
  );
}

function actionButton({
  disabled,
  helper,
  label,
  loading,
  onClick
}: {
  disabled: boolean;
  helper: string;
  label: string;
  loading: boolean;
  onClick: () => void;
}) {
  return (
    <div className="max-w-xs">
      <LoadingButton disabled={disabled} loading={loading} onClick={onClick}>
        {label}
      </LoadingButton>
      <div className={`mt-2 text-xs ${disabled ? "text-amber-200" : "text-slate-500"}`}>
        {helper}
      </div>
    </div>
  );
}

function SamplePath({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-slate-800 bg-ink-950 p-3">
      <dt className="text-slate-500">{label}</dt>
      <dd className="mt-1 break-words font-mono text-slate-300">{value}</dd>
    </div>
  );
}

function friendlyError(err: unknown): string {
  if (err instanceof FlowDeckApiError) {
    if (err.message.toLowerCase().includes("failed to fetch")) {
      return "Unable to reach the FlowDeck API. Confirm the backend is running at http://127.0.0.1:8000.";
    }
    return err.message;
  }
  if (err instanceof TypeError && String(err.message).toLowerCase().includes("fetch")) {
    return "Unable to reach the FlowDeck API. Confirm the backend is running at http://127.0.0.1:8000.";
  }
  return err instanceof Error ? err.message : "Workspace request failed.";
}
