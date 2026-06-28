// @ts-check
const { test, expect } = require("@playwright/test");

const BANNED_PUBLIC_PHRASES = [
  "student perk",
  "setup fee",
  "perk arbitrage",
  "loss leader",
  "loss-leader",
  "free to you",
  "activate your student dev perks",
  "why pay if github student pack",
  "we charge for setup and delivery — not",
  "perks remain free",
  "INTERNAL_PLAYBOOK",
  "STUDENT_PERK_MODEL",
];

const PUBLIC_ROUTES = [
  "/",
  "/demo",
  "/contact",
  "/checkout",
  "/start",
  "/purchase/return",
  "/purchase/cancelled",
  "/login",
];

const OPS_PASSWORD = process.env.OPS_PASSWORD || "csos-local";

for (const path of PUBLIC_ROUTES) {
  test(`public route ${path} loads and passes content firewall`, async ({ page }) => {
    const response = await page.goto(path, { waitUntil: "domcontentloaded" });
    expect(response?.status()).toBe(200);

    const body = (await page.content()).toLowerCase();
    for (const phrase of BANNED_PUBLIC_PHRASES) {
      expect(body, `${path} leaked ${phrase}`).not.toContain(phrase.toLowerCase());
    }
  });
}

test("operator can sign in and reach dashboard", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Password").fill(OPS_PASSWORD);
  await page.getByRole("button", { name: "Sign in" }).click();
  await page.waitForURL("**/dashboard**");
  await expect(page.getByText(/pipeline|clients|dashboard/i).first()).toBeVisible();
});

test("client start hub links to purchase return", async ({ page }) => {
  await page.goto("/start");
  await expect(page.getByRole("heading", { name: /before intake/i })).toBeVisible();
  const resume = page.getByRole("link", { name: /resume intake/i });
  await expect(resume).toHaveAttribute("href", "/purchase/return");
});

test("purchase return form is usable", async ({ page }) => {
  await page.goto("/purchase/return");
  await expect(page.getByLabel(/payment session/i)).toBeVisible();
  await expect(page.getByRole("button", { name: /continue/i })).toBeVisible();
});

test("checkout shows all packages", async ({ page }) => {
  await page.goto("/checkout");
  const text = await page.locator("body").innerText();
  expect(text).toMatch(/foundation/i);
  expect(text).toMatch(/launch/i);
  expect(text).toMatch(/accelerator/i);
});

test("homepage navigation links work", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveURL(/\/$/);
  await page.getByRole("link", { name: "Begin" }).click();
  await expect(page).toHaveURL(/\/checkout/);
  await page.goto("/");
  await page.getByRole("link", { name: /Start with Launch/ }).first().click();
  await expect(page).toHaveURL(/\/checkout/);
  await page.goto("/");
  await page.getByRole("link", { name: /Discuss fit/ }).click();
  await expect(page).toHaveURL(/\/contact/);
});
