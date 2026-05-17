import { expect, test } from "@playwright/test";
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
const nonCsvFixture = path.join(projectRoot, "frontend/tests/fixtures/not-a-csv.txt");

test.describe("Workspace upload flow", () => {
  test("runs the backend-owned sample demo from the Demo page", async ({
    page
  }) => {
    await page.goto("/demo");

    await page.getByRole("button", { name: "Run Sample Demo" }).click();

    await expect(
      page.getByText(/Demo run completed/i)
    ).toBeVisible({ timeout: 20_000 });
    await expect(page.getByText(/FD-RUN-/)).toBeVisible();
    await expect(
      page.getByText("Net exposure buckets", { exact: true })
    ).toBeVisible();
    await expect(
      page.getByRole("link", { name: "Download Excel Report" })
    ).toHaveAttribute("href", /\/runs\/FD-RUN-.*\/report/);
    await expect(
      page.getByRole("link", { name: "View Run Detail" })
    ).toHaveAttribute("href", /\/runs\/FD-RUN-/);
  });

  test("opens a generated run detail page after sample demo", async ({
    page
  }) => {
    await page.goto("/demo");

    await page.getByRole("button", { name: "Run Sample Demo" }).click();
    await expect(
      page.getByText(/Demo run completed/i)
    ).toBeVisible({ timeout: 20_000 });

    const runId = (await page.getByText(/FD-RUN-/).first().textContent()) || "";
    await page.getByRole("link", { name: "View Run Detail" }).click();

    await expect(page).toHaveURL(/\/runs\/FD-RUN-/);
    await expect(page.getByRole("heading", { name: "Run Detail" })).toBeVisible({
      timeout: 15_000
    });
    await expect(page.getByText(runId).first()).toBeVisible();
    await expect(page.getByText("Exposure Buckets")).toBeVisible();
    await expect(page.getByText("Total Net")).toBeVisible();
    await expect(
      page.getByRole("link", { name: "Download Excel Report" })
    ).toHaveAttribute("href", /\/runs\/FD-RUN-.*\/report/);
  });

  test("runs the backend-owned sample demo from the Workspace", async ({
    page
  }) => {
    await page.goto("/workspace");

    await page.getByRole("button", { name: "Run Sample Demo" }).click();

    await expect(
      page.getByText(/Demo run completed/i)
    ).toBeVisible({ timeout: 20_000 });
    await expect(page.getByText(/FD-RUN-/)).toBeVisible();
    await expect(
      page.getByText("Net exposure buckets", { exact: true })
    ).toBeVisible();
    await expect(page.getByText("Total net exposure", { exact: true })).toBeVisible();
    await expect(
      page.getByRole("link", { name: "View Run Detail" })
    ).toHaveAttribute("href", /\/runs\/FD-RUN-/);
    await expect(
      page.getByRole("link", { name: "Download Excel Report" })
    ).toHaveAttribute("href", /\/runs\/FD-RUN-.*\/report/);
  });

  test("runs the full analytics flow and downloads the Excel report", async ({
    page
  }) => {
    await page.goto("/workspace");

    await page.getByLabel("Market Data CSV").setInputFiles(marketDataCsv);
    await page.getByLabel("Futures Positions CSV").setInputFiles(futuresCsv);
    await page.getByLabel("Physical Cargoes CSV").setInputFiles(physicalCsv);

    await page.getByRole("button", { name: "Validate market data" }).click();
    await expect(page.getByRole("cell", { name: "BRTM26" })).toBeVisible({
      timeout: 15_000
    });
    await expect(page.getByText("Rows", { exact: true }).first()).toBeVisible();

    await page.getByRole("button", { name: "Build forward curves" }).click();
    await expect(page.getByRole("img", { name: "Forward Curves" })).toBeVisible({
      timeout: 15_000
    });
    await expect(page.getByRole("cell", { name: "BACKWARDATION" }).first()).toBeVisible({
      timeout: 15_000
    });

    await page.getByRole("button", { name: "Analyze futures" }).click();
    await expect(page.getByText("Futures net")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByText(/6,000 bbl|6,000/)).toBeVisible();

    await page.getByRole("button", { name: "Analyze physical" }).click();
    await expect(page.getByText("Physical net")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByText(/400,000 bbl|400,000/)).toBeVisible();

    await page.getByRole("button", { name: "Compute net exposure" }).click();
    await expect(page.getByLabel("Net Exposure by Bucket chart")).toBeVisible({
      timeout: 15_000
    });
    await expect(page.getByText("Gross component")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByRole("cell", { name: "Crude Alpha" }).first()).toBeVisible();

    await page.getByRole("button", { name: "Simulate hedge" }).click();
    await expect(page.getByLabel("Hedge Impact chart")).toBeVisible({
      timeout: 15_000
    });
    await expect(page.getByText("Post-hedge abs", { exact: true })).toBeVisible({
      timeout: 15_000
    });
    await expect(page.getByRole("cell", { name: "SELL" }).first()).toBeVisible();

    await page.getByRole("button", { name: "Run stress P&L" }).click();
    await expect(page.getByLabel("Stress P&L by Bucket chart")).toBeVisible({
      timeout: 15_000
    });
    await expect(page.getByText("Total stress P&L", { exact: true }).first()).toBeVisible({
      timeout: 15_000
    });
    await expect(page.getByText("Gain buckets")).toBeVisible();

    const downloadPromise = page.waitForEvent("download");
    await page.getByRole("button", { name: "Generate Excel Report" }).click();
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toBe("flowdeck_workspace_report.xlsx");
    await expect(page.getByText("Excel report download started.")).toBeVisible();
  });

  test("shows disabled action guidance before files are selected", async ({ page }) => {
    await page.goto("/workspace");

    await expect(
      page.getByRole("button", { name: "Validate market data" })
    ).toBeDisabled();
    await expect(
      page.getByRole("button", { name: "Compute net exposure" })
    ).toBeDisabled();
    await expect(page.getByText("Select Market Data CSV first.").first()).toBeVisible();
    await expect(
      page.getByText("Select Futures Positions and Physical Cargoes CSVs first.").first()
    ).toBeVisible();
  });

  test("shows a clear warning for a non-CSV upload", async ({ page }) => {
    await page.goto("/workspace");

    await page.getByLabel("Market Data CSV").setInputFiles(nonCsvFixture);

    await expect(
      page.getByText("The backend accepts `.csv` uploads only.")
    ).toBeVisible();
  });
});
