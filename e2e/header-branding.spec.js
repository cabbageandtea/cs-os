// @ts-check
const { test, expect } = require("@playwright/test");

test.describe("public header branding", () => {
  test("desktop keeps square icon with readable brand lockup", async ({ page }) => {
    await page.setViewportSize({ width: 1366, height: 768 });
    await page.goto("/", { waitUntil: "domcontentloaded" });

    const brand = page.locator(".public-header .brand");
    const icon = page.locator(".public-header .brand-mark");
    const brandName = page.locator(".public-header .brand-name");

    await expect(brand).toBeVisible();
    await expect(icon).toBeVisible();
    await expect(brandName).toBeVisible();

    const metrics = await icon.evaluate((img) => ({
      naturalWidth: img.naturalWidth,
      naturalHeight: img.naturalHeight,
      renderedWidth: img.clientWidth,
      renderedHeight: img.clientHeight,
    }));

    expect(metrics.naturalWidth).toBeGreaterThan(0);
    expect(metrics.naturalHeight).toBeGreaterThan(0);
    expect(metrics.naturalWidth).toBe(metrics.naturalHeight);
    expect(Math.abs(metrics.renderedWidth - metrics.renderedHeight)).toBeLessThanOrEqual(2);
  });

  test("mobile hides low-priority header items", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto("/", { waitUntil: "domcontentloaded" });

    const brandName = page.locator(".public-header .brand-name");
    const secondaryNav = page.locator(".public-header nav .nav-secondary");
    const cta = page.locator(".public-header .nav-cta");

    await expect(cta).toBeVisible();
    await expect(brandName).toBeHidden();
    await expect(secondaryNav.first()).toBeHidden();
  });
});
