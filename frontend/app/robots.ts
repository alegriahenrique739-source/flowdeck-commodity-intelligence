import type { MetadataRoute } from "next";
import { searchPolicy } from "@/lib/search-visibility";

export default function robots(): MetadataRoute.Robots {
  const { origin, indexable } = searchPolicy();
  if (!indexable || !origin)
    return { rules: { userAgent: "*", disallow: "/" } };
  return {
    // Let crawlers see noindex on tool/run pages. Robots exclusions are not access control.
    rules: { userAgent: "*", allow: "/", disallow: "/api/" },
    sitemap: `${origin}/sitemap.xml`,
  };
}
