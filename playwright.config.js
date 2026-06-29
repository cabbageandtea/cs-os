// @ts-check
const port = process.env.E2E_PORT || "8012";
const baseURL = process.env.BASE_URL || `http://127.0.0.1:${port}`;
const noServer = process.env.E2E_NO_SERVER === "1";
const isProdTarget = /doggybagg\.cc|onrender\.com/i.test(baseURL);

/** @type {import('@playwright/test').PlaywrightTestConfig} */
module.exports = {
  testDir: "./e2e",
  timeout: 90_000,
  retries: process.env.CI ? 1 : 0,
  use: {
    baseURL,
    trace: "on-first-retry",
  },
  webServer:
    noServer || isProdTarget
      ? undefined
      : {
        command: `python -m uvicorn app.main:app --host 127.0.0.1 --port ${port}`,
        url: baseURL,
        reuseExistingServer: !process.env.CI,
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
          BASE_URL: `http://127.0.0.1:${port}`,
          INTAKE_TOKEN_PEPPER: "e2e-pepper",
        },
      },
};
