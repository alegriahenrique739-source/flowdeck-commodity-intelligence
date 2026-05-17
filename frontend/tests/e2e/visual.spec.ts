import { expect, test, type Page } from "@playwright/test";
import path from "path";

const projectRoot = path.resolve(__dirname, "../../..");
const marketDataCsv = path.join(
  projectRoot,
  "data/sample/market_data/valid_brent_wti_futures.csv"
);
const futuresCsv = path.join(
  projectRoot,
  "data/sample/positions/valid_futures_positions.csv"
);
const physicalCsv = path.join(
  projectRoot,
  "data/sample/positions/valid_physical_cargoes.csv"
);

test.use({
  viewport: { width: 1440, height: 1200 }
});

test.describe("FlowDeck visual regression screenshots", () => {
  test.describe.configure({ mode: "serial" });

  test.beforeEach(async ({ page }) => {
    await mockStableApiStatus(page);
  });

  test("overview page", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: "FlowDeck" })).toBeVisible();

    await expect(page).toHaveScreenshot("overview-page.png", screenshotOptions());
  });

  test("runs dashboard empty state", async ({ page }) => {
    await page.route(/http:\/\/127\.0\.0\.1:8000\/runs.*/, (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ runs: [], count: 0 })
      })
    );

    await page.goto("/runs");
    await expect(page.getByRole("heading", { name: "Runs Dashboard" })).toBeVisible();
    await expect(page.getByText("0 run records displayed")).toBeVisible();

    await expect(page).toHaveScreenshot("runs-dashboard-empty.png", screenshotOptions());
  });

  test("demo page", async ({ page }) => {
    await page.goto("/demo");
    await expect(page.getByRole("heading", { name: "FlowDeck Demo" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Run Sample Demo" })).toBeVisible();

    await expect(page).toHaveScreenshot("demo-page.png", screenshotOptions());
  });

  test("run detail page", async ({ page }) => {
    const runId = "FD-RUN-20260515-140000-ABC123";
    await page.route(`http://127.0.0.1:8000/runs/${runId}`, (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(mockRun(runId))
      })
    );

    await page.goto(`/runs/${runId}`);
    await expect(page.getByRole("heading", { name: "Run Detail" })).toBeVisible();
    await expect(page.getByText(runId).first()).toBeVisible();
    await expect(page.getByText("No errors recorded for this run.")).toBeVisible();

    await expect(page).toHaveScreenshot("run-detail-page.png", screenshotOptions());
  });

  test("workspace empty state", async ({ page }) => {
    await page.goto("/workspace");
    await expect(page.getByRole("heading", { name: "Analytics Workspace" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Validate market data" })).toBeDisabled();
    await expect(page.getByText("valid_physical_cargoes.csv").first()).toBeVisible();

    await expect(page).toHaveScreenshot("workspace-empty-state.png", screenshotOptions());
  });

  test("workspace analytics state with charts", async ({ page }) => {
    await page.goto("/workspace");

    await page.getByLabel("Market Data CSV").setInputFiles(marketDataCsv);
    await page.getByLabel("Futures Positions CSV").setInputFiles(futuresCsv);
    await page.getByLabel("Physical Cargoes CSV").setInputFiles(physicalCsv);

    await page.getByRole("button", { name: "Validate market data" }).click();
    await expect(page.getByRole("cell", { name: "BRTM26" })).toBeVisible({
      timeout: 15_000
    });

    await page.getByRole("button", { name: "Build forward curves" }).click();
    await expect(page.getByRole("img", { name: "Forward Curves" })).toBeVisible({
      timeout: 15_000
    });

    await page.getByRole("button", { name: "Analyze futures" }).click();
    await expect(page.getByText("Futures net")).toBeVisible({
      timeout: 15_000
    });

    await page.getByRole("button", { name: "Analyze physical" }).click();
    await expect(page.getByText("Physical net")).toBeVisible({
      timeout: 15_000
    });

    await page.getByRole("button", { name: "Compute net exposure" }).click();
    await expect(page.getByLabel("Net Exposure by Bucket chart")).toBeVisible({
      timeout: 15_000
    });

    await page.getByRole("button", { name: "Simulate hedge" }).click();
    await expect(page.getByLabel("Hedge Impact chart")).toBeVisible({
      timeout: 15_000
    });

    await page.getByRole("button", { name: "Run stress P&L" }).click();
    await expect(page.getByLabel("Stress P&L by Bucket chart")).toBeVisible({
      timeout: 15_000
    });

    await expect(page).toHaveScreenshot(
      "workspace-analytics-charts.png",
      screenshotOptions()
    );
  });
});

async function mockStableApiStatus(page: Page) {
  await page.route("**/health", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        status: "ok",
        service: "FlowDeck API",
        version: "0.1.0"
      })
    })
  );
  await page.route("**/api/info", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        service: "FlowDeck API",
        version: "0.1.0",
        environment: "local",
        docs_url: "/docs",
        openapi_url: "/openapi.json",
        frontend_expected_origin_examples: [
          "http://localhost:3000",
          "http://127.0.0.1:3000"
        ]
      })
    })
  );
  await page.route("**/demo/sample-files", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        market_data_file: "data/sample/market_data/valid_brent_wti_futures.csv",
        futures_positions_file:
          "data/sample/positions/valid_futures_positions.csv",
        physical_cargoes_file:
          "data/sample/positions/valid_physical_cargoes.csv",
        descriptions: {
          market_data_file: "Synthetic Brent/WTI futures curve market data.",
          futures_positions_file: "Synthetic oil futures positions.",
          physical_cargoes_file: "Synthetic simplified physical cargoes."
        },
        note: "Synthetic demo files only. No real trade or licensed market data."
      })
    })
  );
}

function mockRun(runId: string) {
  return {
    run_id: runId,
    run_type: "DEMO_WORKFLOW",
    status: "SUCCESS",
    created_at: "2026-05-15T14:00:00Z",
    completed_at: "2026-05-15T14:00:03Z",
    input_files: {
      market_data_file: "data/sample/market_data/valid_brent_wti_futures.csv",
      futures_positions_file:
        "data/sample/positions/valid_futures_positions.csv",
      physical_cargoes_file:
        "data/sample/positions/valid_physical_cargoes.csv"
    },
    output_files: {
      excel_report_path: `runs/${runId}/flowdeck_report.xlsx`
    },
    summary: {
      number_of_curves: 2,
      number_of_net_exposure_buckets: 6,
      total_net_exposure_bbl: "406000",
      total_post_hedge_absolute_exposure_bbl: "83000",
      total_stress_pnl_usd: "-2030000"
    },
    errors: [],
    notes: "Backend-powered synthetic sample demo workflow."
  };
}

function screenshotOptions() {
  return {
    animations: "disabled" as const,
    caret: "hide" as const,
    fullPage: true,
    maxDiffPixelRatio: 0.02
  };
}
