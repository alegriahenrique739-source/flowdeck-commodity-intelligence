import { chromium, expect, test, type Browser, type BrowserContext } from "@playwright/test";
import { fork, type ChildProcess } from "node:child_process";
import { createHash } from "node:crypto";
import { readFileSync, existsSync } from "node:fs";
import { request } from "node:https";
import { resolve, join } from "node:path";

type Harness = { origin: string; api: string; pin: string; ca: string; directory: string };
let setup: Harness;
let server: ChildProcess;
let browser: Browser;
const sentinel = "FD-RUN-20260913-000000-ABCDEF";

test.beforeAll(async () => {
  server = fork(resolve(__dirname, "servers.mjs"), [], {
    cwd: resolve(__dirname, "../.."), silent: true,
    env: {
      ...process.env, FLOWDECK_PUBLIC_TEST_FIXTURE: "true",
      NEXT_PUBLIC_FLOWDECK_PUBLIC_DEMO_MODE: "true",
      NEXT_PUBLIC_FLOWDECK_API_BASE_URL: "https://localhost:8444",
      FLOWDECK_ALLOW_INDEXING: "false", FLOWDECK_ENABLE_PILOT_BROWSER: "true",
    },
  });
  server.stdout?.resume();
  server.stderr?.resume();
  setup = await new Promise<Harness>((done, reject) => {
    const timer = setTimeout(() => reject(new Error("Public fixture timed out")), 90000);
    server.once("message", (value) => {
      clearTimeout(timer);
      if (value && typeof value === "object" && "error" in value) reject(new Error(String(value.error)));
      else done(value as Harness);
    });
    server.once("error", () => { clearTimeout(timer); reject(new Error("Fixture did not start")); });
    server.once("exit", () => { clearTimeout(timer); reject(new Error("Fixture exited")); });
  });
  browser = await chromium.launch({ args: [`--ignore-certificate-errors-spki-list=${setup.pin}`] });
});

test.afterAll(async () => {
  await browser?.close();
  if (server && server.exitCode === null) {
    const exited = new Promise<void>((done) => server.once("exit", () => done()));
    if (server.connected) server.send("stop");
    else server.kill();
    await exited;
  }
  if (setup) expect(existsSync(setup.directory)).toBe(false);
});

async function context(): Promise<BrowserContext> {
  const ctx = await browser.newContext();
  // Fail closed on a stale build pointing at a real deployed API. No API payload mocking.
  await ctx.route("**/*", (route) => {
    const origin = new URL(route.request().url()).origin;
    return [setup.origin, setup.api].includes(origin) ? route.continue() : route.abort();
  });
  return ctx;
}

function api(path: string, method = "GET", origin = setup.origin) {
  return new Promise<{ status: number; headers: import("node:http").IncomingHttpHeaders; body: Buffer }>((done, reject) => {
    const req = request(`${setup.api}${path}`, {
      method, ca: setup.ca, family: 4, headers: { Origin: origin },
    }, (res) => {
      const chunks: Buffer[] = [];
      res.on("data", (chunk) => chunks.push(chunk));
      res.on("end", () => done({ status: res.statusCode!, headers: res.headers, body: Buffer.concat(chunks) }));
      res.on("error", reject);
    });
    req.on("error", reject);
    req.setTimeout(15000, () => req.destroy(new Error("Loopback API timeout")));
    req.end();
  });
}

test("public deployment contract, exact CORS and local-record isolation", async () => {
  const info = await api("/api/info");
  expect(JSON.parse(info.body.toString()).environment).toBe("public_demo");
  expect(info.headers["access-control-allow-origin"]).toBe(setup.origin);
  expect(info.headers["x-robots-tag"]).toBe("noindex, nofollow");
  expect((await api("/health", "GET", "https://unapproved.example")).headers["access-control-allow-origin"]).toBeUndefined();
  const schema = JSON.parse((await api("/openapi.json")).body.toString());
  expect(Object.keys(schema.paths).sort()).toEqual([
    "/health", "/capabilities", "/api/info", "/demo/sample-files", "/demo/run",
    "/runs", "/runs/{run_id}", "/runs/{run_id}/report",
  ].sort());
  expect((await api(`/runs/${sentinel}`)).status).toBe(404);
  expect((await api(`/runs/${sentinel}/report`)).status).toBe(404);
  expect((await api("/runs")).body.toString()).not.toContain(sentinel);
});

test("public entry navigation leads to supported demo and run pages only", async () => {
  const ctx = await context();
  try {
    const page = await ctx.newPage();
    await page.goto(setup.origin);
    await expect(page.getByRole("heading", { name: "FlowDeck", exact: true })).toBeVisible();
    await expect(page.getByRole("link", { name: "Run Public Demo" })).toHaveAttribute("href", "/demo");
    await expect(page.locator('a[href="/workspace"], a[href="/desk"]')).toHaveCount(0);
    await page.locator("nav").getByRole("link", { name: "Demo", exact: true }).click();
    await expect(page.getByRole("button", { name: "Run Sample Demo" })).toBeVisible();
    await expect(page.locator('a[href="/workspace"], a[href="/desk"]')).toHaveCount(0);
    await page.locator("nav").getByRole("link", { name: "Runs", exact: true }).click();
    await expect(page.getByRole("heading", { name: "Runs Dashboard" })).toBeVisible();
    await expect(page.getByRole("combobox", { name: "Status", exact: true })).toBeVisible();
    await expect(page.getByText("No demo runs match this view.", { exact: false })).toBeVisible();
    await expect(page.getByText("python scripts/run_demo_workflow.py", { exact: false })).toHaveCount(0);
  } finally { await ctx.close(); }
});

test("direct upload, private, write and unknown routes are denied by the real API", async () => {
  for (const path of ["/market-data/validate", "/reports/excel", "/intake/prepare", "/portfolio/analyze", "/pricing/review", "/reconciliation/review", "/pilot/runs", "/future-route"]) {
    const response = await api(path, "POST");
    expect(response.status).toBe(403);
    expect(JSON.parse(response.body.toString()).detail.error_code).toBe("PUBLIC_DEMO_ONLY");
    expect(response.headers["x-robots-tag"]).toBe("noindex, nofollow");
  }
});

test("public browser demo, immutable execution summary, limits and exact Excel download", async () => {
  const ctx = await context();
  try {
    const page = await ctx.newPage();
    await page.goto(`${setup.origin}/demo`);
    await expect(page.locator("nav").getByRole("link", { name: "Workspace" })).toHaveCount(0);
    await expect(page.getByText("Uploads are not part of the public demo.", { exact: false })).toBeVisible();
    const response = page.waitForResponse((res) => res.url().startsWith(`${setup.api}/demo/run?`));
    await page.getByRole("button", { name: "Run Sample Demo", exact: true }).click();
    const generated = await response;
    expect(generated.status()).toBe(200);
    expect(generated.headers()["access-control-allow-origin"]).toBe(setup.origin);
    const result = await generated.json();
    expect(result.run_id).toMatch(/^FD-RUN-\d{8}-\d{6}-[A-F0-9]{6}$/);
    await expect(page.getByRole("heading", { name: "Demo run completed", exact: true })).toBeVisible();
    // An immediate second request is limited by the real admission controller.
    const limited = await api("/demo/run", "POST");
    expect(limited.status).toBe(429);
    expect(Number(limited.headers["retry-after"])).toBeGreaterThan(0);
    await page.getByLabel("Target hedge ratio").fill("0.25");
    await page.getByLabel("Stress scenario").selectOption("PARALLEL_UP_5");
    const story = page.getByRole("heading", { name: "What just happened?" }).locator("..");
    await expect(story).toContainText("80.00%");
    await expect(story).toContainText("PARALLEL_DOWN_5");
    const runRoot = join(setup.directory, "runs", "public-demo", result.run_id);
    const stored = JSON.parse(readFileSync(join(runRoot, "run_metadata.json"), "utf8"));
    expect(stored.summary).toEqual(result.summary);
    const downloadEvent = page.waitForEvent("download");
    await page.getByRole("link", { name: "Download Excel Report", exact: true }).click();
    const download = await downloadEvent;
    expect(download.suggestedFilename()).toBe(`flowdeck_report_${result.run_id}.xlsx`);
    const bytes = readFileSync((await download.path())!);
    expect(bytes.subarray(0, 2).toString()).toBe("PK");
    expect(createHash("sha256").update(bytes).digest("hex")).toBe(
      createHash("sha256").update(readFileSync(join(runRoot, "flowdeck_report.xlsx"))).digest("hex"),
    );
    expect((await api(result.report_url)).headers["x-robots-tag"]).toBe("noindex, nofollow");
    await page.getByRole("link", { name: "View Run Detail" }).click();
    await expect(page).toHaveURL(`${setup.origin}/runs/${result.run_id}`);
    await expect(page.getByRole("heading", { name: "Run Detail", exact: true })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Input Files" })).toBeVisible();
    await expect(page.getByRole("link", { name: "Back to Workspace" })).toHaveCount(0);
    await expect(page.getByRole("link", { name: "Download Excel Report" })).toHaveAttribute("href", `${setup.api}${result.report_url}`);
    const listed = JSON.parse((await api("/runs")).body.toString());
    expect(listed.runs.map((run: { run_id: string }) => run.run_id)).toEqual([result.run_id]);
    // The test store cap is one. A later attempt exercises actual capacity failure, no mock.
    await new Promise((done) => setTimeout(done, Number(limited.headers["retry-after"]) * 1000 + 100));
    await page.goto(`${setup.origin}/demo`);
    const full = page.waitForResponse((res) => res.url().startsWith(`${setup.api}/demo/run?`));
    await page.getByRole("button", { name: "Run Sample Demo", exact: true }).click();
    expect((await full).status()).toBe(503);
    await expect(page.getByText("Public demo capacity reached.", { exact: false })).toBeVisible();
    await expect(page.getByText("Confirm the backend is running", { exact: false })).toHaveCount(0);
    expect((await api(result.report_url)).status).toBe(200);
  } finally { await ctx.close(); }
});

test("public frontend cannot activate local uploads or the private session bridge", async () => {
  const ctx = await context();
  try {
    const page = await ctx.newPage();
    for (const path of ["/workspace", "/desk", "/portfolio", "/pricing", "/reconciliation", "/pilot"]) {
      const response = await page.goto(setup.origin + path);
      expect(response?.headers()["x-robots-tag"]).toBe("noindex, nofollow");
      await expect(page.locator('input[type="file"]')).toHaveCount(0);
      await expect(page.getByRole("button", { name: "Sign in with identity provider" })).toHaveCount(0);
    }
    expect(await page.evaluate(async () => (await fetch("/api/pilot/session")).status)).toBe(404);
  } finally { await ctx.close(); }
});
