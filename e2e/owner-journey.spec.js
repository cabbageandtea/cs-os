// @ts-check
const { test, expect } = require("@playwright/test");

const OPS_PASSWORD = process.env.OPS_PASSWORD || "csos-local";
const IS_PROD = /doggybagg\.cc|onrender\.com/i.test(process.env.BASE_URL || "");

test.describe("operator journey", () => {
  test.skip(IS_PROD, "Mutating ops tests run locally/CI only");

  test("login → intake → client detail", async ({ page }) => {
    await page.goto("/login");
    await page.fill('input[name="password"]', OPS_PASSWORD);
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/\/dashboard/);

    await page.goto("/intake");
    const stamp = Date.now();
    await page.fill('input[name="name"]', `[E2E] Smoke Client ${stamp}`);
    await page.fill('input[name="email"]', `e2e-${stamp}@example.com`);
    await page.selectOption('select[name="package_slug"]', "foundation");
    await page.fill('input[name="target_role"]', "Junior Software Engineer");
    await page.fill(
      'textarea[name="experience_education"]',
      "BS Computer Science, State University, expected 2027"
    );
    await page.fill(
      'textarea[name="experience_projects"]',
      "Built a task tracker API with FastAPI and SQLite for a capstone course."
    );
    await page.fill(
      'textarea[name="experience_work"]',
      "Campus IT help desk — ticket triage and documentation."
    );
    await page.fill('input[name="skills"]', "Python, JavaScript, SQL, Git");
    await page.fill('input[name="github_url"]', "https://github.com/octocat");
    await page.check('input[name="prerequisites_attestation"]');
    await page.check('input[name="attestation"]');
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL(/\/clients\/\d+/);
    await expect(page.locator("h1")).toContainText("[E2E]");
    await expect(page.getByRole("heading", { name: "Build kit" })).toBeVisible();
  });
});
