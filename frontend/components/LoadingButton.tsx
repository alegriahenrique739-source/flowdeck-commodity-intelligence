"use client";

import type { ButtonHTMLAttributes, ReactNode } from "react";

interface LoadingButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  loading?: boolean;
  children: ReactNode;
}

export function LoadingButton({
  loading = false,
  children,
  disabled,
  className = "",
  ...props
}: LoadingButtonProps) {
  return (
    <button
      className={`rounded-md border border-teal-700 bg-teal-900/30 px-4 py-2 text-sm text-teal-100 hover:border-teal-500 disabled:cursor-not-allowed disabled:border-slate-800 disabled:bg-slate-900 disabled:text-slate-500 ${className}`}
      disabled={disabled || loading}
      type="button"
      {...props}
    >
      {loading ? "Working..." : children}
    </button>
  );
}

