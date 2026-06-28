// @ts-check
const { test, expect } = require("@playwright/test");

const EXAMPLES = [
  {
    slug: "alex-rivera",
    name: "Alex Rivera",
    domain: "alexrivera.me",
    repoProject: "campus-dining",
    repoCta: /view code/i,
    demoProject: "healthcare-wait",
    demoCta: /live dashboard/i,
    caseStudyCta: /case study/i,
  },
  {
    slug: "jordan-kim",
    name: "Jordan Kim",
    domain: "jordankim.me",
    repoProject: "inventory-anomaly",
    repoCta: /open notebook/i,
    demoProject: "shiftsync",
    demoCta: /live demo/i,
    caseStudyCta: /case study/i,
  },
];

test.describe("example portfolio mock click-through", () => {
  for (const ex of EXAMPLES) {
    test(`${ex.slug} suite nav links work`, async ({ page }) => {
      const response = await page.goto(`/example/${ex.slug}`, {
        waitUntil: "domcontentloaded",
      });
      expect(response?.status()).toBe(200);
      await expect(page.getByRole("heading", { level: 1, name: ex.name })).toBeVisible();
      await expect(page.locator(".example-suite-nav")).toBeVisible();

      await page.locator(".example-suite-nav").getByRole("link", { name: "GitHub" }).click();
      await expect(page).toHaveURL(new RegExp(`/example/${ex.slug}/github`));

      await page.locator(".example-suite-nav").getByRole("link", { name: "Resume" }).click();
      await expect(page).toHaveURL(new RegExp(`/example/${ex.slug}/resume`));

      await page.locator(".example-suite-nav").getByRole("link", { name: "LinkedIn" }).click();
      await expect(page).toHaveURL(new RegExp(`/example/${ex.slug}/linkedin`));
      await expect(page.getByRole("heading", { name: "Education" })).toBeVisible();

      await page.locator(".example-suite-nav").getByRole("link", { name: "Portfolio" }).click();
      await expect(page).toHaveURL(new RegExp(`/example/${ex.slug}/?$`));

      expect(await page.content()).not.toContain('href="https://github.com"');
    });

    test(`${ex.slug} project repo and demo buttons work`, async ({ page }) => {
      await page.goto(`/example/${ex.slug}#projects`, { waitUntil: "domcontentloaded" });
      const projects = page.locator("#projects");

      await projects.getByRole("link", { name: ex.repoCta }).first().click();
      await expect(page).toHaveURL(
        new RegExp(`/example/${ex.slug}/repo/${ex.repoProject}`)
      );

      await page.goto(`/example/${ex.slug}#projects`);
      await projects.getByRole("link", { name: ex.demoCta }).first().click();
      await expect(page).toHaveURL(
        new RegExp(`/example/${ex.slug}/demo/${ex.demoProject}`)
      );
      await expect(page.getByText("Live preview (demo)")).toBeVisible();
    });
  }

  test("alex case study → project → repo chain", async ({ page }) => {
    await page.goto("/example/alex-rivera#projects");
    await page
      .locator("#projects")
      .getByRole("link", { name: /case study/i })
      .first()
      .click();
    await expect(page).toHaveURL(/\/example\/alex-rivera\/projects\/campus-dining/);
    await page.getByRole("link", { name: /view code/i }).click();
    await expect(page).toHaveURL(/\/example\/alex-rivera\/repo\/campus-dining/);
    await expect(page.getByRole("heading", { name: /Campus Dining/i })).toBeVisible();
  });

  test("resume PDF returns valid file", async ({ request }) => {
    const response = await request.get("/example/alex-rivera/resume.pdf");
    expect(response.ok()).toBeTruthy();
    expect(response.headers()["content-type"]).toContain("application/pdf");
    const body = await response.body();
    expect(body.slice(0, 4).toString()).toBe("%PDF");
  });

  test("landing proof opens example mocks in new tab", async ({ page, context }) => {
    await page.goto("/", { waitUntil: "domcontentloaded" });

    const linkedinPopup = context.waitForEvent("page");
    await page.getByRole("link", { name: /sample linkedin/i }).first().click();
    const linkedinPage = await linkedinPopup;
    await linkedinPage.waitForLoadState("domcontentloaded");
    await expect(linkedinPage).toHaveURL(/\/example\/alex-rivera\/linkedin/);

    const sitePopup = context.waitForEvent("page");
    await page.getByRole("link", { name: /view example site/i }).first().click();
    const sitePage = await sitePopup;
    await sitePage.waitForLoadState("domcontentloaded");
    await expect(sitePage).toHaveURL(/\/example\/alex-rivera\/?$/);
    await expect(sitePage.locator(".example-suite-nav")).toBeVisible();
  });
});
