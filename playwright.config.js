// @ts-check
const baseURL = process.env.BASE_URL || "http://127.0.0.1:8010";
const noServer = process.env.E2E_NO_SERVER === "1";

/** @type {import('@playwright/test').PlaywrightTestConfig} */
module.exports = {
  testDir: "./e2e",
  timeout: 60_000,
  retries: process.env.CI ? 1 : 0,
  use: {
    baseURL,
    trace: "on-first-retry",
  },
  webServer: noServer
    ? undefined
    : {
        command: "python -m uvicorn app.main:app --host 127.0.0.1 --port 8010",
        url: baseURL,
        reuseExistingServer: false,
        timeout: 120_000,
        env: {
          PATH: process.env.PATH || "",
          SYSTEMROOT: process.env.SYSTEMROOT || "",
          DATABASE_URL: "sqlite:///./cs_os_e2e.db",
          OPS_PASSWORD: process.env.OPS_PASSWORD || "csos-local",
          STRIPE_SECRET_KEY: "sk_test_e2e",
          STRIPE_WEBHOOK_SECRET: "whsec_e2e",
          STRIPE_PRICE_FOUNDATION: "price_foundation_e2e",
          STRIPE_PRICE_LAUNCH: "price_launch_e2e",
          STRIPE_PRICE_ACCELERATOR: "price_accelerator_e2e",
          BASE_URL: baseURL,
          INTAKE_TOKEN_PEPPER: "e2e-pepper",
        },
      },
};
