interface RawJsonDetailsProps {
  data: unknown;
  title?: string;
}

export function RawJsonDetails({ data, title = "Show raw JSON" }: RawJsonDetailsProps) {
  if (data === null || data === undefined) {
    return null;
  }

  return (
    <details className="rounded-md border border-slate-800 bg-ink-950 p-3">
      <summary className="cursor-pointer text-sm text-slate-300">{title}</summary>
      <pre className="mt-3 max-h-80 overflow-auto whitespace-pre-wrap text-xs text-slate-400">
        {JSON.stringify(data, null, 2)}
      </pre>
    </details>
  );
}

