import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/public-demo",
  testMatch: "*.spec.ts",
  workers: 1,
  retries: 0,
  timeout: 120_000,
  reporter: "list",
  outputDir: "test-results/public-demo",
  use: { trace: "off", screenshot: "off", video: "off" },
});
