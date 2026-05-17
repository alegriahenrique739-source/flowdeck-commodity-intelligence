interface ErrorBannerProps {
  message: string | null;
  title?: string;
}

export function ErrorBanner({ message, title = "Workspace error" }: ErrorBannerProps) {
  if (!message) {
    return null;
  }

  return (
    <div className="rounded-lg border border-red-900 bg-red-950/40 p-4 text-sm text-red-100">
      <div className="font-medium">{title}</div>
      <div className="mt-1">{message}</div>
    </div>
  );
}
