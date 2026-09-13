import { NextResponse, type NextRequest } from "next/server";
import { PUBLIC_SEARCH_PATHS, searchPolicy } from "@/lib/search-visibility";

export function middleware(request: NextRequest) {
  const response = NextResponse.next();
  const path = request.nextUrl.pathname;
  const publicPage = PUBLIC_SEARCH_PATHS.some(
    (candidate) => candidate === path,
  );
  response.headers.set(
    "X-Robots-Tag",
    searchPolicy().indexable && publicPage
      ? "index, follow"
      : "noindex, nofollow",
  );
  return response;
}

export const config = { matcher: ["/((?!_next/static|_next/image).*)"] };
