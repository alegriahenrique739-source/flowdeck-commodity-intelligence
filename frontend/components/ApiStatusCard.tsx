"use client";

import { useEffect, useState } from "react";
import { getApiInfo, getHealth } from "@/lib/api";
import type { ApiInfoResponse, HealthResponse } from "@/lib/types";

export function ApiStatusCard() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [info, setInfo] = useState<ApiInfoResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function load() {
      try {
        const [healthResult, infoResult] = await Promise.all([
          getHealth(),
          getApiInfo()
        ]);
        if (isMounted) {
          setHealth(healthResult);
          setInfo(infoResult);
          setError(null);
        }
      } catch (err) {
        if (isMounted) {
          setError(apiStatusErrorMessage(err));
        }
      }
    }

    load();
    return () => {
      isMounted = false;
    };
  }, []);

  const connected = Boolean(health && !error);

  return (
    <section className="rounded-lg border border-slate-800 bg-ink-900 p-5 shadow-panel">
      <div className="flex items-center justify-between gap-4">
        <div>
          <div className="text-sm font-medium uppercase text-slate-500">
            API Status
          </div>
          <div className="mt-2 text-xl font-semibold text-white">
            {connected ? "Connected" : "Offline"}
          </div>
        </div>
        <div
          className={`rounded-full border px-3 py-1 text-sm ${
            connected
              ? "border-emerald-500/30 bg-emerald-500/12 text-emerald-200"
              : "border-red-500/30 bg-red-500/12 text-red-200"
          }`}
        >
          {connected ? "ok" : "check backend"}
        </div>
      </div>

      {error ? <p className="mt-4 text-sm text-red-200">{error}</p> : null}

      {info ? (
        <dl className="mt-5 grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
          <div>
            <dt className="text-slate-500">Service</dt>
            <dd className="text-slate-200">{info.service}</dd>
          </div>
          <div>
            <dt className="text-slate-500">Version</dt>
            <dd className="text-slate-200">{info.version}</dd>
          </div>
          <div>
            <dt className="text-slate-500">Environment</dt>
            <dd className="text-slate-200">{info.environment}</dd>
          </div>
          <div>
            <dt className="text-slate-500">Docs</dt>
            <dd className="text-slate-200">{info.docs_url}</dd>
          </div>
        </dl>
      ) : null}
    </section>
  );
}

function apiStatusErrorMessage(err: unknown): string {
  if (
    err instanceof TypeError ||
    (err instanceof Error && err.message.toLowerCase().includes("fetch"))
  ) {
    return "Unable to reach the FlowDeck API. Confirm the backend is running at http://127.0.0.1:8000.";
  }
  return err instanceof Error ? err.message : "FlowDeck API is offline.";
}
