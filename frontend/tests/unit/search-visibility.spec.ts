import { expect, test } from "@playwright/test";
import { searchPolicy, PUBLIC_SEARCH_PATHS } from "../../lib/search-visibility";

const enabled = {
  nodeEnv: "production",
  publicDemo: "true",
  allowIndexing: "true",
  siteUrl: "https://flowdeck.example.com",
  vercel: "1",
  vercelEnv: "production",
};

test("indexing is opt-in and limited to the public entry pages", () => {
  expect(searchPolicy({})).toEqual({ origin: null, indexable: false });
  expect(searchPolicy(enabled)).toEqual({
    origin: enabled.siteUrl,
    indexable: true,
  });
  expect(PUBLIC_SEARCH_PATHS).toEqual(["/", "/demo"]);
});

for (const [name, change] of [
  ["local build", { publicDemo: "false" }],
  ["missing public flag", { publicDemo: undefined }],
  ["disabled indexing", { allowIndexing: "false" }],
  ["missing indexing approval", { allowIndexing: undefined }],
  ["invalid truthy value", { allowIndexing: "TRUE" }],
  ["dev server", { nodeEnv: "development" }],
  ["preview deployment", { vercelEnv: "preview" }],
  ["missing Vercel context", { vercelEnv: undefined }],
] as const) {
  test(`does not index ${name}`, () =>
    expect(searchPolicy({ ...enabled, ...change }).indexable).toBe(false));
}

for (const siteUrl of [
  "",
  "http://flowdeck.example.com",
  "https://localhost",
  "https://127.0.0.1",
  "https://[::1]",
  "https://desk.local",
  "https://desk.internal",
  "https://desk.test",
  "https://flowdeck.example.com:3000",
  "https://user:password@flowdeck.example.com",
  "https://flowdeck.example.com/demo",
  "https://flowdeck.example.com/a/..",
  "https://flowdeck.example.com?tracking=x",
  "https://flowdeck.example.com#demo",
  "https://flowdeck.example.com\n",
  "https://*.example.com",
]) {
  test(`rejects canonical origin ${JSON.stringify(siteUrl)}`, () => {
    expect(searchPolicy({ ...enabled, siteUrl })).toEqual({
      origin: null,
      indexable: false,
    });
  });
}

test("self-hosted public production can opt in; canonical origin is normalized", () => {
  expect(
    searchPolicy({
      ...enabled,
      vercel: undefined,
      vercelEnv: undefined,
      siteUrl: "https://FlowDeck.example.com/",
    }),
  ).toEqual({ origin: "https://flowdeck.example.com", indexable: true });
});
