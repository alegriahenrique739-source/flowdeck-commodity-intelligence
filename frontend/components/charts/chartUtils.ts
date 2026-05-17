import type { ApiRecord } from "@/lib/types";

export function toNumber(value: unknown): number | null {
  if (value === null || value === undefined || value === "") {
    return null;
  }
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : null;
}

export function stringValue(value: unknown, fallback = "-"): string {
  if (value === null || value === undefined || value === "") {
    return fallback;
  }
  return String(value);
}

export function bucketLabel(row: ApiRecord): string {
  const explicitLabel = stringValue(row.label, "");
  if (explicitLabel) {
    return explicitLabel;
  }

  const hedgeIndex = stringValue(row.hedge_index, "Index");
  const exposureMonth = stringValue(row.exposure_month, "Month");
  const book = stringValue(row.book, "Book");
  return `${hedgeIndex} ${exposureMonth} / ${book}`;
}

export function topByAbsoluteValue(
  rows: ApiRecord[],
  valueKey: string,
  limit = 10
): ApiRecord[] {
  return [...rows]
    .sort((left, right) => {
      const leftValue = Math.abs(toNumber(left[valueKey]) ?? 0);
      const rightValue = Math.abs(toNumber(right[valueKey]) ?? 0);
      return rightValue - leftValue;
    })
    .slice(0, limit);
}
