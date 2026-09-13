import type { Metadata } from "next";

type SearchEnvironment = {
  nodeEnv?: string;
  publicDemo?: string;
  allowIndexing?: string;
  siteUrl?: string;
  vercel?: string;
  vercelEnv?: string;
};

export const PUBLIC_SEARCH_PATHS = ["/", "/demo"] as const;

export function searchPolicy(
  env: SearchEnvironment = {
    nodeEnv: process.env.NODE_ENV,
    publicDemo: process.env.NEXT_PUBLIC_FLOWDECK_PUBLIC_DEMO_MODE,
    allowIndexing: process.env.FLOWDECK_ALLOW_INDEXING,
    siteUrl: process.env.FLOWDECK_PUBLIC_SITE_URL,
    vercel: process.env.VERCEL,
    vercelEnv: process.env.VERCEL_ENV,
  },
) {
  let origin: string | null = null;
  const value = env.siteUrl || "";
  try {
    const url = new URL(value);
    if (
      value === value.trim() &&
      !/[\u0000-\u0020\u007f@\\]/.test(value) &&
      /^https:\/\/[^/?#\\\s]+\/?$/.test(value) &&
      !url.username &&
      !url.password &&
      !url.port &&
      /^[a-z0-9-]+(?:\.[a-z0-9-]+)+$/.test(url.hostname) &&
      !/^[\d.]+$/.test(url.hostname) &&
      !/(?:^|\.)(?:localhost|local|internal|test|invalid)$/.test(url.hostname)
    )
      origin = url.origin;
  } catch {
    /* Unconfigured/invalid sites remain non-indexable. */
  }
  const indexable = Boolean(
    origin &&
    env.nodeEnv === "production" &&
    env.publicDemo === "true" &&
    env.allowIndexing === "true" &&
    (!env.vercelEnv || env.vercelEnv === "production") &&
    (!env.vercel || env.vercelEnv === "production"),
  );
  return { origin, indexable };
}

export function publicPageMetadata(
  path: (typeof PUBLIC_SEARCH_PATHS)[number],
): Metadata {
  const { origin, indexable } = searchPolicy();
  const title =
    path === "/"
      ? "FlowDeck | Brent & WTI Commodity Trading Intelligence"
      : "FlowDeck Demo | Oil Exposure Analytics & Excel Reports";
  const description =
    path === "/"
      ? "Excel-native Brent/WTI analytics: forward curves, physical and futures exposure, hedge simulation and stress P&L. Synthetic demo; no trade execution."
      : "Try FlowDeck with synthetic Brent/WTI data. Review exposure, simulate a hedge, stress-test P&L and download an Excel report. No trade execution.";
  const verification = process.env.FLOWDECK_GOOGLE_SITE_VERIFICATION || "";
  // Never inherit a public page canonical or index directive into workspace/run pages.
  return {
    title,
    description,
    robots: { index: indexable, follow: indexable },
    ...(indexable && origin
      ? {
          alternates: { canonical: new URL(path, origin).href },
          openGraph: {
            title,
            description,
            type: "website",
            siteName: "FlowDeck",
            url: new URL(path, origin).href,
            locale: "en_US",
          },
          twitter: { card: "summary", title, description },
          ...(path === "/" && /^[A-Za-z0-9_-]{10,256}$/.test(verification)
            ? { verification: { google: verification } }
            : {}),
        }
      : {}),
  };
}
