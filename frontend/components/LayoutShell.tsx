import Link from "next/link";
import type { ReactNode } from "react";
import { isPublicDemoMode } from "@/lib/config";

export function LayoutShell({ children }: { children: ReactNode }) {
  return (
    <main className="min-h-screen bg-ink-950">
      <div className="border-b border-slate-800 bg-ink-900/85">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <Link href="/" className="flex items-baseline gap-3">
            <span className="text-xl font-semibold tracking-normal text-white">
              FlowDeck
            </span>
            <span className="text-sm text-slate-400">
              Commodity Trading Intelligence
            </span>
          </Link>
          <nav className="flex items-center gap-2 text-sm text-slate-300">
            <Link
              className="rounded-md border border-slate-700 px-3 py-2 hover:border-slate-500 hover:text-white"
              href="/"
            >
              Overview
            </Link>
            <Link
              className={
                isPublicDemoMode
                  ? "rounded-md border border-teal-600 bg-teal-500/15 px-3 py-2 font-semibold text-teal-50 hover:border-teal-300"
                  : "rounded-md border border-slate-700 px-3 py-2 hover:border-slate-500 hover:text-white"
              }
              href="/demo"
            >
              Demo
            </Link>
            <Link
              className="rounded-md border border-slate-700 px-3 py-2 hover:border-slate-500 hover:text-white"
              href="/runs"
            >
              Runs
            </Link>
            {isPublicDemoMode ? null : (
              <Link
                className="rounded-md border border-slate-700 px-3 py-2 hover:border-slate-500 hover:text-white"
                href="/workspace"
              >
                Workspace
              </Link>
            )}
          </nav>
        </div>
      </div>
      <div className="mx-auto max-w-7xl px-6 py-8">{children}</div>
    </main>
  );
}
