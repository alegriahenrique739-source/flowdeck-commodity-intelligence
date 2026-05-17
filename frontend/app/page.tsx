import Link from "next/link";
import { ApiStatusCard } from "@/components/ApiStatusCard";
import { LayoutShell } from "@/components/LayoutShell";
import { MetricCard } from "@/components/MetricCard";
import { getApiDocsUrl, getOpenApiUrl } from "@/lib/api";
import { isPublicDemoMode } from "@/lib/config";

const capabilities = [
  ["Market Data", "CSV validation for Brent and WTI futures curves."],
  ["Curves", "Forward curve summaries and calendar spreads."],
  ["Physical + Paper Exposure", "Read-only display of backend exposure results."],
  ["Hedging", "Deterministic hedge simulation outputs."],
  ["Stress P&L", "Synthetic scenario P&L from net exposure."],
  ["Excel Reports", "Run-scoped workbook downloads for desk review."]
];

export default function HomePage() {
  return (
    <LayoutShell>
      <section className="grid gap-6 lg:grid-cols-[1.4fr_0.8fr]">
        <div className="rounded-lg border border-slate-800 bg-ink-900 p-7 shadow-panel">
          <div className="text-sm font-medium uppercase text-teal-200">
            Local Analytics Workbench
          </div>
          <h1 className="mt-3 text-4xl font-semibold tracking-normal text-white">
            FlowDeck
          </h1>
          <p className="mt-3 max-w-3xl text-lg text-slate-300">
            Excel-native Commodity Trading Intelligence for Brent and WTI oil
            desk workflows.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link
              className="rounded-md border border-teal-700 bg-teal-900/30 px-4 py-2 text-sm text-teal-100 hover:border-teal-500"
              href={isPublicDemoMode ? "/demo" : "/workspace"}
            >
              {isPublicDemoMode ? "Run Public Demo" : "Analytics Workspace"}
            </Link>
            <Link
              className="rounded-md border border-slate-700 px-4 py-2 text-sm text-slate-100 hover:border-slate-500"
              href="/runs"
            >
              Runs Dashboard
            </Link>
            <a
              className="rounded-md border border-slate-700 px-4 py-2 text-sm text-slate-100 hover:border-slate-500"
              href={getApiDocsUrl()}
            >
              API Docs
            </a>
            <a
              className="rounded-md border border-slate-700 px-4 py-2 text-sm text-slate-100 hover:border-slate-500"
              href={getOpenApiUrl()}
            >
              OpenAPI JSON
            </a>
          </div>
        </div>

        <ApiStatusCard />
      </section>

      <section className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard label="Scope" value="Brent / WTI" detail="Oil analytics only" />
        <MetricCard label="Mode" value="Local" detail="CSV, JSON and Excel files" />
        <MetricCard label="Execution" value="Read-only UI" detail="No trade execution" />
        <MetricCard label="Backend" value="FastAPI" detail="Financial logic source" />
      </section>

      <section className="mt-6">
        <div className="mb-3 flex items-end justify-between gap-4">
          <div>
            <h2 className="text-xl font-semibold text-white">Capabilities</h2>
            <p className="mt-1 text-sm text-slate-400">
              The frontend displays backend results without duplicating
              financial calculations.
            </p>
          </div>
        </div>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {capabilities.map(([title, detail]) => (
            <div
              className="rounded-lg border border-slate-800 bg-ink-900 p-5"
              key={title}
            >
              <h3 className="font-semibold text-white">{title}</h3>
              <p className="mt-2 text-sm text-slate-400">{detail}</p>
            </div>
          ))}
        </div>
      </section>
    </LayoutShell>
  );
}
