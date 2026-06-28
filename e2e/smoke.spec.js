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

for (const path of PUBLIC_ROUTES) {
  test(`public ${path} loads and passes content firewall`, async ({ page }) => {
    const response = await page.goto(path, { waitUntil: "domcontentloaded" });
    expect(response?.status()).toBe(200);

    const body = (await page.content()).toLowerCase();
    for (const phrase of BANNED_PUBLIC_PHRASES) {
      expect(body, `${path} leaked ${phrase}`).not.toContain(phrase.toLowerCase());
    }
  });
}

test("health endpoint reports status", async ({ request }) => {
  const response = await request.get("/health");
  expect(response.ok()).toBeTruthy();
  const payload = await response.json();
  expect(payload.status).toMatch(/^(ok|degraded|unhealthy)$/);
  expect(payload.version).toBeTruthy();
  expect(payload.checks).toBeTruthy();
  expect(payload.checks.database).toBe(true);
});

test("ops routes redirect unauthenticated users to login", async ({ page }) => {
  const response = await page.goto("/dashboard", { waitUntil: "domcontentloaded" });
  expect(response?.url()).toContain("/login");
});
