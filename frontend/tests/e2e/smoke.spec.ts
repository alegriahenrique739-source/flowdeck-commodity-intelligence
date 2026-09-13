import { expect, test } from "@playwright/test";

const publicDemoMode = process.env.NEXT_PUBLIC_FLOWDECK_PUBLIC_DEMO_MODE === "true";

test.describe("FlowDeck frontend smoke tests", () => {
  test("overview page renders product identity and navigation", async ({ page }) => {
    await page.goto("/");
    const nav = page.getByRole("navigation");

    await expect(page.getByRole("heading", { name: "FlowDeck" })).toBeVisible();
    await expect(page.getByText("API Status")).toBeVisible();
    await expect(nav.getByRole("link", { name: "Demo", exact: true })).toBeVisible();
    await expect(nav.getByRole("link", { name: "Runs", exact: true })).toBeVisible();
    if (publicDemoMode) {
      await expect(
        nav.getByRole("link", { name: "Workspace", exact: true })
      ).toHaveCount(0);
      await expect(page.getByRole("link", { name: "Run Public Demo" })).toBeVisible();
    } else {
      await expect(
        nav.getByRole("link", { name: "Workspace", exact: true })
      ).toBeVisible();
      await expect(page.getByRole("link", { name: "Analytics Workspace" })).toBeVisible();
    }
  });

  test("runs page renders filters without requiring backend data", async ({ page }) => {
    await page.goto("/runs");

    await expect(page.getByRole("heading", { name: "Runs Dashboard" })).toBeVisible();
    await expect(page.getByLabel("Status")).toBeVisible();
    await expect(page.getByLabel("Run type")).toBeVisible();
    await expect(page.getByLabel("Limit")).toBeVisible();
    await expect(page.getByText(/run records displayed|Loading runs|Unable to load runs/i)).toBeVisible();
  });

  test("workspace page renders upload cards and workflow steps", async ({ page }) => {
    await page.goto("/workspace");

    await expect(page.getByRole("heading", { name: "Analytics Workspace" })).toBeVisible();
    if (publicDemoMode) {
      await expect(page.getByText("Local / development only.", { exact: false })).toBeVisible();
      await expect(page.locator('input[type="file"]')).toHaveCount(0);
      return;
    }
    await expect(page.getByRole("heading", { name: "Run Sample Demo" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Market Data CSV" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Futures Positions CSV" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Physical Cargoes CSV" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Validate market data" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Build forward curves" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Analyze Positions" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Compute net exposure" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Simulate hedge" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Run stress P&L" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Generate Excel Report" })).toBeVisible();
  });

  test("demo page renders presentation content and sample demo action", async ({
    page
  }) => {
    await page.goto("/demo");

    await expect(page.getByRole("heading", { name: "FlowDeck Demo" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Run Sample Demo" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Run Sample Demo" })).toBeVisible();
    await expect(page.getByText("Validate market data")).toBeVisible();
    await expect(page.getByRole("heading", { name: "Demo Story" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Data And Safety" })).toBeVisible();
    await expect(
      page.getByRole("heading", { name: "Technical Architecture" })
    ).toBeVisible();
  });

  test("run detail page renders a backend run record", async ({ page }) => {
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
    await expect(page.getByText("Exposure Buckets")).toBeVisible();
    await expect(page.getByRole("heading", { name: "Input Files" })).toBeVisible();
    await expect(
      page.getByRole("link", { name: "Download Excel Report" })
    ).toHaveAttribute("href", /\/runs\/FD-RUN-.*\/report/);
  });

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

  test("top navigation moves between overview, runs, and workspace", async ({ page }) => {
    await page.goto("/");
    const nav = page.getByRole("navigation");

    await nav.getByRole("link", { name: "Demo", exact: true }).click();
    await expect(page).toHaveURL(/\/demo$/);
    await expect(page.getByRole("heading", { name: "FlowDeck Demo" })).toBeVisible();

    await nav.getByRole("link", { name: "Runs", exact: true }).click();
    await expect(page).toHaveURL(/\/runs$/);
    await expect(page.getByRole("heading", { name: "Runs Dashboard" })).toBeVisible();

    if (!publicDemoMode) {
      await nav.getByRole("link", { name: "Workspace", exact: true }).click();
      await expect(page).toHaveURL(/\/workspace$/);
      await expect(page.getByRole("heading", { name: "Analytics Workspace" })).toBeVisible();
    }

    await nav.getByRole("link", { name: "Overview", exact: true }).click();
    await expect(page).toHaveURL(/\/$/);
    await expect(page.getByRole("heading", { name: "FlowDeck" })).toBeVisible();
  });
});
