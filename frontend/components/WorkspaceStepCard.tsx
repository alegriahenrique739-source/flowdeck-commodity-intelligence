import type { ReactNode } from "react";

interface WorkspaceStepCardProps {
  title: string;
  eyebrow: string;
  status?: "Not started" | "Ready" | "Running" | "Complete" | "Error";
  description?: string;
  requiredInputs?: string[];
  action?: ReactNode;
  children?: ReactNode;
}

export function WorkspaceStepCard({
  title,
  eyebrow,
  status = "Not started",
  description,
  requiredInputs = [],
  action,
  children
}: WorkspaceStepCardProps) {
  return (
    <section className="rounded-lg border border-slate-800 bg-ink-900 p-5 shadow-panel">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <div className="text-xs font-medium uppercase text-slate-500">
            {eyebrow}
          </div>
          <div className="mt-2 flex flex-wrap items-center gap-3">
            <h2 className="text-lg font-semibold text-white">{title}</h2>
            <span className={`rounded-full border px-2 py-1 text-xs ${statusClass(status)}`}>
              {status}
            </span>
          </div>
          {description ? (
            <p className="mt-1 text-sm text-slate-400">{description}</p>
          ) : null}
          {requiredInputs.length > 0 ? (
            <p className="mt-2 text-xs text-slate-500">
              Required: {requiredInputs.join(", ")}
            </p>
          ) : null}
        </div>
        {action ? <div className="shrink-0">{action}</div> : null}
      </div>
      {children ? <div className="mt-5 space-y-4">{children}</div> : null}
    </section>
  );
}

function statusClass(status: WorkspaceStepCardProps["status"]): string {
  if (status === "Complete") {
    return "border-emerald-500/30 bg-emerald-500/12 text-emerald-200";
  }
  if (status === "Error") {
    return "border-red-500/30 bg-red-500/12 text-red-200";
  }
  if (status === "Running") {
    return "border-amber-500/30 bg-amber-500/12 text-amber-200";
  }
  if (status === "Ready") {
    return "border-teal-500/30 bg-teal-500/12 text-teal-200";
  }
  return "border-slate-500/30 bg-slate-500/12 text-slate-300";
}
