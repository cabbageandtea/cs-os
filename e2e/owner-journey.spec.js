// @ts-check
/** Owner-level QA — full client + operator journeys */
const { test, expect } = require("@playwright/test");

const OPS_PASSWORD = process.env.OPS_PASSWORD || "csos-local";

test.describe("Client journey", () => {
  test("landing → packages anchor → checkout → stripe handoff", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();

    await page.getByRole("link", { name: "Packages" }).click();
    await expect(page).toHaveURL(/\/#packages/);
    await expect(page.locator("#packages")).toBeVisible();

    await page.getByRole("link", { name: "Begin" }).click();
    await expect(page).toHaveURL(/\/checkout/);

    const stripeBtn = page.getByRole("button", { name: /continue to stripe/i }).first();
    await expect(stripeBtn).toBeEnabled();

    const [response] = await Promise.all([
      page.waitForResponse((r) => r.url().includes("/checkout/create") && r.request().method() === "POST"),
      stripeBtn.click(),
    ]);
    expect([303, 302, 200]).toContain(response.status());
    await page.waitForURL(/stripe\.com|\/checkout/, { timeout: 15000 });
  });

  test("contact form submits and confirms", async ({ page }) => {
    const email = `owner-qa-${Date.now()}@example.com`;
    await page.goto("/contact");
    await page.getByLabel("Full name").fill("Owner QA");
    await page.getByLabel("Email").fill(email);
    await page.getByLabel("Target role").fill("Software Engineer Intern");
    await page.getByLabel("Current status").fill("Student");
    await page.getByLabel("Package interest").selectOption("launch");
    await page.getByRole("button", { name: /send message/i }).click();
    await expect(page.getByText(/thank you, owner qa/i)).toBeVisible();
  });

  test("start guide and purchase return flow", async ({ page }) => {
    await page.goto("/start");
    await page.getByRole("link", { name: /resume intake/i }).click();
    await expect(page).toHaveURL(/\/purchase\/return/);

    await page.getByLabel(/payment session/i).fill("cs_test_invalid");
    await page.getByRole("button", { name: /continue/i }).click();
    await page.waitForLoadState("networkidle");
    expect(page.url()).toMatch(/purchase\/(success|return)/);
  });

  test("checkout cancelled page is on-brand", async ({ page }) => {
    await page.goto("/purchase/cancelled");
    await expect(page.locator("body")).toHaveClass(/page-public/);
    await expect(page.getByRole("link", { name: /back to packages|view packages/i })).toBeVisible();
  });

  test("demo and footer links work", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("navigation").getByRole("link", { name: "Process" }).click();
    await expect(page).toHaveURL(/\/demo/);
    await page.getByRole("contentinfo").getByRole("link", { name: "Contact" }).click();
    await expect(page).toHaveURL(/\/contact/);
    await page.goto("/");
    await page.getByRole("contentinfo").getByRole("link", { name: "Client guide" }).click();
    await expect(page).toHaveURL(/\/start/);
  });
});

test.describe("Operator journey", () => {
  test("login failure then success", async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel("Password").fill("wrong-password");
    await page.getByRole("button", { name: "Sign in" }).click();
    await expect(page.getByText(/incorrect password/i)).toBeVisible();

    await page.getByLabel("Password").fill(OPS_PASSWORD);
    await page.getByRole("button", { name: "Sign in" }).click();
    await page.waitForURL("**/dashboard**");
    await expect(page.getByText(/operations dashboard|pipeline/i).first()).toBeVisible();
  });

  test("dashboard protected without session", async ({ page }) => {
    await page.context().clearCookies();
    await page.goto("/dashboard");
    await page.waitForURL("**/login**");
    expect(page.url()).toMatch(/\/login/);
  });

  test("checkout reachable from ops nav", async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel("Password").fill(OPS_PASSWORD);
    await page.getByRole("button", { name: "Sign in" }).click();
    await page.waitForURL("**/dashboard**");
    await page.getByRole("link", { name: "Checkout" }).click();
    await expect(page).toHaveURL(/\/checkout/);
    await expect(page.locator("body")).toHaveClass(/page-public/);
  });
});

test.describe("Mobile viewport", () => {
  test.use({ viewport: { width: 390, height: 844 } });

  test("nav links remain reachable", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("link", { name: "Packages" })).toBeVisible();
    await page.getByRole("link", { name: "Packages" }).click();
    await expect(page).toHaveURL(/#packages/);
    await page.getByRole("link", { name: "Begin" }).click();
    await expect(page).toHaveURL(/\/checkout/);
  });
});
