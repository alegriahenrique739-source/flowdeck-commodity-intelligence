import { MetricCard } from "./MetricCard";

interface ResultMetric {
  label: string;
  value: string | number;
  detail?: string;
}

export function ResultMetricGrid({ metrics }: { metrics: ResultMetric[] }) {
  if (metrics.length === 0) {
    return null;
  }

  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {metrics.map((metric) => (
        <MetricCard
          detail={metric.detail}
          key={metric.label}
          label={metric.label}
          value={metric.value}
        />
      ))}
    </div>
  );
}

