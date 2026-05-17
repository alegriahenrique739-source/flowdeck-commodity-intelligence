import type { RunStatus } from "./types";

const numberFormatter = new Intl.NumberFormat("en-US", {
  maximumFractionDigits: 0
});

const usdFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0
});

export function formatBbl(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === "") {
    return "-";
  }
  const numeric = Number(value);
  return Number.isFinite(numeric) ? `${numberFormatter.format(numeric)} bbl` : "-";
}

export function formatNumber(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === "") {
    return "-";
  }
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numberFormatter.format(numeric) : "-";
}

export function formatUsd(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === "") {
    return "-";
  }
  const numeric = Number(value);
  return Number.isFinite(numeric) ? usdFormatter.format(numeric) : "-";
}

export function formatUsdPerBbl(value: string | number | null | undefined): string {
  const formatted = formatUsd(value);
  return formatted === "-" ? formatted : `${formatted}/bbl`;
}

export function formatPercent(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === "") {
    return "-";
  }
  const numeric = Number(value);
  return Number.isFinite(numeric) ? `${(numeric * 100).toFixed(2)}%` : "-";
}

export function formatLots(value: string | number | null | undefined): string {
  const formatted = formatNumber(value);
  return formatted === "-" ? formatted : `${formatted} lots`;
}

export function formatDateTime(value: string | null | undefined): string {
  if (!value) {
    return "-";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString();
}

export function formatStatus(status: string | null | undefined): string {
  if (!status) {
    return "-";
  }
  return status.replaceAll("_", " ");
}

export function statusClass(status: string | null | undefined): string {
  const normalized = status as RunStatus | undefined;
  if (normalized === "SUCCESS") {
    return "border-emerald-500/30 bg-emerald-500/12 text-emerald-200";
  }
  if (normalized === "FAILED") {
    return "border-red-500/30 bg-red-500/12 text-red-200";
  }
  if (normalized === "RUNNING") {
    return "border-amber-500/30 bg-amber-500/12 text-amber-200";
  }
  return "border-slate-500/30 bg-slate-500/12 text-slate-200";
}
