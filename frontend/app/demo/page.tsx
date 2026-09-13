import Link from "next/link";
import { isPublicDemoMode } from "@/lib/config";
import { DemoRunPanel } from "@/components/DemoRunPanel";
import { LayoutShell } from "@/components/LayoutShell";
import { publicPageMetadata } from "@/lib/search-visibility";

export function generateMetadata() {
  return publicPageMetadata("/demo");
}

const demoBullets = [
  "Validate market data",
  "Build forward curves",
  "Combine physical + futures exposure",
  "Simulate hedge",
  "Stress-test P&L",
  "Generate Excel report"
];

const storySteps = [
  "Backend loads synthetic Brent/WTI sample data.",
  "FlowDeck builds curves and calendar spreads.",
  "It combines physical cargoes with futures positions.",
  "It calculates hedgeable net exposure.",
  "It simulates a deterministic hedge.",
  "It runs synthetic stress P&L.",
  "It exports a trader-ready Excel workbook."
];

const architectureItems = [
  {
    label: "FastAPI backend",
    detail: "Owns validation, analytics, demo orchestration, and run metadata."
  },
  {
    label: "Next.js frontend",
    detail: "Displays backend outputs without duplicating financial logic."
  },
  {
    label: "Excel reports",
    detail: "Produces desk-ready workbooks for review and presentation."
  },
  {
    label: "Run metadata",
    detail: "Stores local JSON records and report paths for repeatable demos."
  },
  {
    label: "Test coverage",
    detail: "Uses pytest for backend services and Playwright for frontend flows."
  }
];

export default function DemoPage() {
  return (
    <LayoutShell>
      <section className="rounded-lg border border-slate-800 bg-ink-900 p-8 shadow-panel">
        <div className="grid gap-8 lg:grid-cols-[1fr_360px]">
          <div>
            <div className="text-sm font-semibold uppercase text-teal-200">
              Presentation mode
            </div>
            <h1 className="mt-3 text-4xl font-semibold tracking-normal text-white">
              FlowDeck Demo
            </h1>
            <p className="mt-4 max-w-3xl text-base text-slate-300">
              Run a complete Brent/WTI commodity trading intelligence workflow
              using synthetic sample data.
            </p>
            <div className="mt-6 flex flex-wrap gap-2">
              {demoBullets.map((item) => (
                <span
                  className="rounded-md border border-slate-700 bg-ink-950 px-3 py-2 text-sm text-slate-200"
                  key={item}
                >
                  {item}
                </span>
              ))}
            </div>
          </div>

          <div className="rounded-lg border border-teal-900/60 bg-teal-950/20 p-5">
            <h2 className="text-lg font-semibold text-white">Demo objective</h2>
            <p className="mt-2 text-sm text-slate-300">
              Show how FlowDeck turns backend-owned synthetic market, futures,
              and physical position data into curves, exposure, hedge impact,
              stress P&L, run metadata, and an Excel report.
            </p>
            {!isPublicDemoMode && <Link
              className="mt-4 inline-flex rounded-md border border-teal-700 bg-teal-500/10 px-3 py-2 text-sm font-semibold text-teal-100 hover:border-teal-400"
              href="/workspace"
            >
              Manual Workspace
            </Link>}
          </div>
        </div>
      </section>

      <div className="mt-6">
        <DemoRunPanel />
      </div>

      <section className="mt-6 grid gap-6 lg:grid-cols-[1fr_1fr]">
        <div className="rounded-lg border border-slate-800 bg-ink-900 p-6 shadow-panel">
          <h2 className="text-xl font-semibold text-white">Demo Story</h2>
          <ol className="mt-4 space-y-3">
            {storySteps.map((step, index) => (
              <li
                className="grid grid-cols-[32px_1fr] gap-3 text-sm text-slate-300"
                key={step}
              >
                <span className="flex h-8 w-8 items-center justify-center rounded-md border border-slate-700 bg-ink-950 text-slate-200">
                  {index + 1}
                </span>
                <span className="pt-1.5">{step}</span>
              </li>
            ))}
          </ol>
        </div>

        <div className="space-y-6">
          <section className="rounded-lg border border-slate-800 bg-ink-900 p-6 shadow-panel">
            <h2 className="text-xl font-semibold text-white">Data And Safety</h2>
            <ul className="mt-4 space-y-2 text-sm text-slate-300">
              <li>Synthetic demo data only.</li>
              <li>No licensed market data redistribution.</li>
              <li>No trade execution.</li>
              <li>Analytics only; hedge outputs require human review.</li>
              <li>The backend remains the source of truth.</li>
            </ul>
          </section>

          <section className="rounded-lg border border-slate-800 bg-ink-900 p-6 shadow-panel">
            <h2 className="text-xl font-semibold text-white">
              Technical Architecture
            </h2>
            <div className="mt-4 grid gap-3">
              {architectureItems.map((item) => (
                <div
                  className="rounded-md border border-slate-800 bg-ink-950 p-3"
                  key={item.label}
                >
                  <div className="text-sm font-semibold text-slate-100">
                    {item.label}
                  </div>
                  <div className="mt-1 text-xs text-slate-400">
                    {item.detail}
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>
      </section>
    </LayoutShell>
  );
}
