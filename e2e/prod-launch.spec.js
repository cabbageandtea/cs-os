// @ts-check
const { test, expect } = require("@playwright/test");

const base = process.env.BASE_URL || "";
const IS_PROD =
  process.env.E2E_PROD === "1" || /doggybagg\.cc|onrender\.com/i.test(base);

test.describe("production launch gates", () => {
  test.skip(!IS_PROD, "Set BASE_URL=https://doggybagg.cc and E2E_NO_SERVER=1");

  test("health reports collect-money ready", async ({ request }) => {
    const response = await request.get("/health");
    expect(response.ok()).toBeTruthy();
    const health = await response.json();
    expect(health.status).toBe("ok");
    expect(health.stripe_mode).toBe("live");
    expect(health.email_configured).toBe(true);
    expect(health.collect_money_ready).toBe(true);
    expect(health.checks.database).toBe(true);
    expect(health.checks.stripe_webhook).toBe(true);
    expect(health.checks.base_url).toBe(true);
    expect(health.checks.email_resend).toBe(true);
  });

  test("status page shows operational checks", async ({ page }) => {
    await page.goto("/status", { waitUntil: "domcontentloaded" });
    await expect(page.locator("body")).toContainText(/stripe/i);
    await expect(page.locator("body")).toContainText(/email/i);
    const body = (await page.content()).toLowerCase();
    expect(body).toMatch(/grade|score/);
  });

  test("checkout opens Stripe hosted page", async ({ page }) => {
    await page.goto("/checkout", { waitUntil: "domcontentloaded" });
    const form = page.locator('form[action="/checkout/create"]').first();
    await form.locator('input[name="terms_accepted"]').check();
    await Promise.all([
      page.waitForURL(/checkout\.stripe\.com/i, { timeout: 45_000 }),
      form.locator('button[type="submit"]').click(),
    ]);
  });

  test("ops login gate works", async ({ page }) => {
    const password = process.env.PROD_OPS_PASSWORD;
    test.skip(!password, "Set PROD_OPS_PASSWORD to verify ops login on production");

    await page.goto("/login");
    await page.fill('input[name="password"]', password);
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/\/dashboard/, { timeout: 15_000 });
    await expect(page.locator("body")).toContainText(/pipeline|client/i);
  });
});
