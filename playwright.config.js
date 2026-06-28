// @ts-check
const { defineConfig } = require("@playwright/test");

const baseURL = process.env.BASE_URL || "http://127.0.0.1:8003";

module.exports = defineConfig({
  testDir: "e2e",
  timeout: 30_000,
  retries: process.env.CI ? 1 : 0,
  use: {
    baseURL,
    trace: "on-first-retry",
  },
  webServer: process.env.E2E_NO_SERVER
    ? undefined
    : {
        command: ".venv\\Scripts\\uvicorn.exe app.main:app --host 127.0.0.1 --port 8003",
        url: baseURL,
        reuseExistingServer: true,
        cwd: __dirname,
      },
});
