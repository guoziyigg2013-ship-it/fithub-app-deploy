const { defineConfig, devices } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./tests/e2e",
  timeout: 45_000,
  expect: {
    timeout: 10_000
  },
  fullyParallel: false,
  workers: 1,
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    baseURL: "http://127.0.0.1:4173",
    browserName: "chromium",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    ...devices["iPhone 13"]
  },
  webServer: {
    command: "python3 scripts/run_test_server.py --port 4173",
    url: "http://127.0.0.1:4173/healthz",
    reuseExistingServer: !process.env.CI,
    timeout: 30_000
  }
});
