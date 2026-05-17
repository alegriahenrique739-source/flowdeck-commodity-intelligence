import type { ApiRecord } from "@/lib/types";
import { formatBbl, formatDateTime, formatLots, formatUsd, formatUsdPerBbl } from "@/lib/format";

interface ResultTableProps {
  rows: ApiRecord[];
  columns: string[];
  emptyText?: string;
  maxRows?: number;
}

export function ResultTable({
  rows,
  columns,
  emptyText = "No rows to display.",
  maxRows = 8
}: ResultTableProps) {
  const visibleRows = rows.slice(0, maxRows);

  if (visibleRows.length === 0) {
    return (
      <div className="rounded-md border border-slate-800 bg-ink-950 p-4 text-sm text-slate-400">
        {emptyText}
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-md border border-slate-800">
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-xs">
          <thead className="bg-slate-900 text-slate-400">
            <tr>
              {columns.map((column) => (
                <th className="whitespace-nowrap px-3 py-2 uppercase" key={column}>
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800 text-slate-200">
            {visibleRows.map((row, index) => (
              <tr key={index}>
                {columns.map((column) => (
                  <td className="whitespace-nowrap px-3 py-2" key={column}>
                    {formatCell(column, row[column])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {rows.length > maxRows ? (
        <div className="border-t border-slate-800 px-3 py-2 text-xs text-slate-500">
          Showing first {maxRows} of {rows.length} rows.
        </div>
      ) : null}
    </div>
  );
}

function formatCell(column: string, value: unknown): string {
  if (value === null || value === undefined || value === "") {
    return "-";
  }
  const normalized = column.toLowerCase();
  if (normalized.includes("date") || normalized.includes("created_at") || normalized.includes("completed_at")) {
    return formatDateTime(String(value));
  }
  if (normalized.includes("lots")) {
    return formatLots(value as string | number);
  }
  if (normalized.includes("bbl") || normalized.includes("exposure")) {
    return formatBbl(value as string | number);
  }
  if (normalized.includes("price") || normalized.includes("usd_per_bbl")) {
    return formatUsdPerBbl(value as string | number);
  }
  if (normalized.includes("pnl") || normalized.includes("usd")) {
    return formatUsd(value as string | number);
  }
  if (typeof value === "object") {
    return JSON.stringify(value);
  }
  return String(value);
}
