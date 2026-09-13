import type { MetadataRoute } from "next";
import { PUBLIC_SEARCH_PATHS, searchPolicy } from "@/lib/search-visibility";

export default function sitemap(): MetadataRoute.Sitemap {
  const { origin, indexable } = searchPolicy();
  if (!indexable || !origin) return [];
  // No run IDs, inputs, report links, fabricated modification dates or private routes.
  return PUBLIC_SEARCH_PATHS.map((path) => ({
    url: new URL(path, origin).href,
  }));
}
