// @ts-check
const { test, expect } = require("@playwright/test");
const { execSync } = require("child_process");
const path = require("path");

const baseURL = process.env.BASE_URL || "http://127.0.0.1:8012";
const IS_PROD = /doggybagg\.cc|onrender\.com/i.test(baseURL);
const OPS_PASSWORD = process.env.OPS_PASSWORD || "csos-local";

function seedPaidPurchase(packageSlug = "foundation") {
  const repoRoot = path.resolve(__dirname, "..");
  const raw = execSync(
    `python scripts/e2e_seed_paid_purchase.py --package ${packageSlug}`,
    {
      cwd: repoRoot,
      env: {
        ...process.env,
        DATABASE_URL: process.env.DATABASE_URL || "sqlite:///./cs_os_e2e.db",
        STRIPE_WEBHOOK_SECRET: process.env.STRIPE_WEBHOOK_SECRET || "whsec_e2e",
        INTAKE_TOKEN_PEPPER: process.env.INTAKE_TOKEN_PEPPER || "e2e-pepper",
        OPS_PASSWORD,
        BASE_URL: baseURL,
      },
    }
  ).toString();
  const line = raw.trim().split("\n").pop();
  return JSON.parse(line);
}

async function fillTokenIntake(page, { name, targetRole }) {
  await page.fill('input[name="name"]', name);
  await page.fill('input[name="target_role"]', targetRole);
  await page.fill(
    'textarea[name="experience_education"]',
    "BS Computer Science, State University, expected 2027"
  );
  await page.fill(
    'textarea[name="experience_projects"]',
    "Task tracker API with FastAPI and SQLite — 200 weekly active users in pilot."
  );
  await page.fill(
    'textarea[name="experience_work"]',
    "Campus IT help desk — ticket triage and documentation."
  );
  await page.fill('input[name="skills"]', "Python, JavaScript, SQL, Git");
  await page.fill('input[name="github_url"]', "https://github.com/octocat");
  await page.check('input[name="prerequisites_attestation"]');
  await page.check('input[name="attestation"]');
}

test.describe("revenue loop", () => {
  test.skip(IS_PROD, "Full mutating loop runs locally/CI only (prod uses prod-launch.spec.js)");

  test("webhook → brief → ops dashboard", async ({ page }) => {
    const fixture = seedPaidPurchase("foundation");
    const clientName = `[E2E] Revenue ${fixture.email.split("@")[0]}`;

    await page.goto(`/purchase/success?session_id=${encodeURIComponent(fixture.session_id)}`);
    await page.waitForURL(/\/intake\//, { timeout: 30_000 });

    await fillTokenIntake(page, {
      name: clientName,
      targetRole: "Software Engineer Intern",
    });
    await page.click('button[type="submit"]');
    await expect(page.locator("h1")).toContainText(/brief received/i);

    await page.goto("/login");
    await page.fill('input[name="password"]', OPS_PASSWORD);
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/\/dashboard/);

    await expect(page.getByText(clientName, { exact: false })).toBeVisible({ timeout: 15_000 });
  });

  test("purchase status API returns intake URL after webhook", async ({ request }) => {
    const fixture = seedPaidPurchase("launch");
    const response = await request.get(
      `/purchase/status?session_id=${encodeURIComponent(fixture.session_id)}`
    );
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.status).toBe("paid");
    expect(data.ready).toBe(true);
    expect(data.intake_url).toMatch(/\/intake\//);
    expect(data.package_slug).toBe("launch");
  });
});
