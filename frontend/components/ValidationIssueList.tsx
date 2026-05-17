interface ValidationIssueListProps {
  issues: unknown[] | undefined;
}

export function ValidationIssueList({ issues }: ValidationIssueListProps) {
  if (!issues || issues.length === 0) {
    return null;
  }

  return (
    <div className="rounded-md border border-red-900 bg-red-950/30 p-4">
      <h3 className="text-sm font-medium text-red-100">Validation issues</h3>
      <ul className="mt-3 space-y-2 text-sm text-red-100">
        {issues.map((issue, index) => (
          <li className="rounded border border-red-900/60 bg-red-950/30 p-2" key={index}>
            {formatIssue(issue)}
          </li>
        ))}
      </ul>
    </div>
  );
}

function formatIssue(issue: unknown): string {
  if (typeof issue === "string") {
    return issue;
  }
  if (issue && typeof issue === "object") {
    const record = issue as Record<string, unknown>;
    if (typeof record.message === "string") {
      return record.message;
    }
    if (typeof record.msg === "string") {
      return record.msg;
    }
    return JSON.stringify(record);
  }
  return String(issue);
}

