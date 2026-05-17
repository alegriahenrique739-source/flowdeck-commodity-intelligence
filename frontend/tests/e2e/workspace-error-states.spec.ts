import { expect, test } from "@playwright/test";
import path from "path";

const projectRoot = path.resolve(__dirname, "../../..");
const validMarketDataCsv = path.join(
  projectRoot,
  "data/sample/market_data/valid_brent_wti_futures.csv"
);
const invalidMarketDataCsv = path.join(
  projectRoot,
  "data/sample/market_data/invalid_negative_price.csv"
);
const futuresCsv = path.join(
  projectRoot,
  "data/sample/positions/valid_futures_positions.csv"
);
const physicalCsv = path.join(
  projectRoot,
  "data/sample/positions/valid_physical_cargoes.csv"
);
const nonCsvFixture = path.join(projectRoot, "frontend/tests/fixtures/not-a-csv.txt");

test.describe("Workspace and API error states", () => {
  test("shows a clear offline state on overview and workspace", async ({ page }) => {
    await page.route("**/health", (route) => route.abort());
    await page.route("**/api/info", (route) => route.abort());

    await page.goto("/");
    await expect(page.getByText("API Status")).toBeVisible();
    await expect(page.getByText("Offline")).toBeVisible();
    await expect(page.getByText("check backend")).toBeVisible();
    await expect(
      page.getByText("Unable to reach the FlowDeck API. Confirm the backend is running")
    ).toBeVisible();

    await page.goto("/workspace");
    await expect(page.getByRole("heading", { name: "Analytics Workspace" })).toBeVisible();
    await expect(page.getByText("Offline")).toBeVisible();
    await expect(page.getByText("check backend")).toBeVisible();
  });

  test("keeps file-dependent actions disabled with clear helper text", async ({
    page
  }) => {
    await page.goto("/workspace");

    await expect(
      page.getByRole("button", { name: "Validate market data" })
    ).toBeDisabled();
    await expect(
      page.getByRole("button", { name: "Build forward curves" })
    ).toBeDisabled();
    await expect(
      page.getByRole("button", { name: "Analyze futures" })
    ).toBeDisabled();
    await expect(
      page.getByRole("button", { name: "Analyze physical" })
    ).toBeDisabled();
    await expect(
      page.getByRole("button", { name: "Compute net exposure" })
    ).toBeDisabled();
    await expect(
      page.getByRole("button", { name: "Generate Excel Report" })
    ).toBeDisabled();

    await expect(page.getByText("Select Market Data CSV first.").first()).toBeVisible();
    await expect(page.getByText("Select Futures Positions CSV first.")).toBeVisible();
    await expect(page.getByText("Select Physical Cargoes CSV first.")).toBeVisible();
    await expect(page.getByText("Select all three CSV files first.")).toBeVisible();
  });

  test("warns when a selected upload does not look like a CSV", async ({ page }) => {
    await page.goto("/workspace");

    await page.getByLabel("Market Data CSV").setInputFiles(nonCsvFixture);

    await expect(
      page.getByText("The backend accepts `.csv` uploads only.")
    ).toBeVisible();
  });

  test("renders backend validation errors as a readable issue list", async ({
    page
  }) => {
    await page.goto("/workspace");

    await page.getByLabel("Market Data CSV").setInputFiles(invalidMarketDataCsv);
    await page.getByRole("button", { name: "Validate market data" }).click();

    await expect(page.getByText("Workspace error")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByText("Validation failed.")).toBeVisible();
    await expect(page.getByRole("heading", { name: "Validation issues" })).toBeVisible();
    await expect(page.getByText("Row 2: price must be positive.")).toBeVisible();
    await expect(page.locator("pre").filter({ hasText: "invalid_price" })).toHaveCount(0);
  });

  test("shows a clean report generation failure", async ({ page }) => {
    await page.route("**/reports/excel", (route) =>
      route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({
          detail: {
            error_code: "REPORT_GENERATION_FAILED",
            message: "Report generation failed during the browser test."
          }
        })
      })
    );

    await page.goto("/workspace");
    await page.getByLabel("Market Data CSV").setInputFiles(validMarketDataCsv);
    await page.getByLabel("Futures Positions CSV").setInputFiles(futuresCsv);
    await page.getByLabel("Physical Cargoes CSV").setInputFiles(physicalCsv);

    await page.getByRole("button", { name: "Generate Excel Report" }).click();

    await expect(page.getByText("Workspace error")).toBeVisible({ timeout: 15_000 });
    await expect(
      page.getByText("Report generation failed during the browser test.")
    ).toBeVisible();
    await expect(page.getByText("Excel report download started.")).toHaveCount(0);
  });

  test("shows a clean sample demo failure", async ({ page }) => {
    await page.route("**/demo/run*", (route) =>
      route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({
          detail: {
            error_code: "DEMO_RUN_FAILED",
            message: "Sample demo failed during the browser test."
          }
        })
      })
    );

    await page.goto("/workspace");
    await page.getByRole("button", { name: "Run Sample Demo" }).click();

    await expect(
      page.getByText("Sample demo failed during the browser test.")
    ).toBeVisible({ timeout: 15_000 });
    await expect(
      page.getByText(/Demo run completed/i)
    ).toHaveCount(0);
  });

  test("shows a clean run detail error for an unknown run", async ({ page }) => {
    await page.goto("/runs/UNKNOWN_RUN_ID");

    await expect(page.getByText("Unable to load run.")).toBeVisible({
      timeout: 15_000
    });
    await expect(page.getByText("Invalid run_id.")).toBeVisible();
    await expect(page.getByRole("link", { name: "Back to Runs" })).toBeVisible();
  });
});
