"use client";

interface FileUploadCardProps {
  title: string;
  description: string;
  samplePath: string;
  file: File | null;
  status?: string;
  onChange: (file: File | null) => void;
}

export function FileUploadCard({
  title,
  description,
  samplePath,
  file,
  status,
  onChange
}: FileUploadCardProps) {
  const csvWarning = file && !file.name.toLowerCase().endsWith(".csv");

  return (
    <div className="rounded-lg border border-slate-800 bg-ink-900 p-5 shadow-panel">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="font-semibold text-white">{title}</h3>
          <p className="mt-1 text-sm text-slate-400">{description}</p>
        </div>
        {status ? (
          <span className="rounded-full border border-slate-700 px-2 py-1 text-xs text-slate-300">
            {status}
          </span>
        ) : null}
      </div>
      <label className="mt-4 block">
        <span className="sr-only">{title}</span>
        <input
          accept=".csv,text/csv"
          className="block w-full rounded-md border border-slate-700 bg-ink-950 px-3 py-2 text-sm text-slate-200 file:mr-3 file:rounded-md file:border-0 file:bg-slate-700 file:px-3 file:py-2 file:text-sm file:text-white"
          onChange={(event) => onChange(event.target.files?.[0] ?? null)}
          type="file"
        />
      </label>
      <div className="mt-3 text-xs text-slate-500">
        Selected:{" "}
        <span className="font-mono text-slate-300">{file?.name || "None"}</span>
      </div>
      {csvWarning ? (
        <div className="mt-2 text-xs text-red-200">
          This file does not look like a CSV. The backend accepts `.csv` uploads only.
        </div>
      ) : null}
      <div className="mt-2 break-words font-mono text-xs text-slate-500">
        {samplePath}
      </div>
    </div>
  );
}
