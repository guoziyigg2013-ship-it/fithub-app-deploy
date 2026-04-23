const { test, expect } = require("@playwright/test");
const { registerEnthusiast, openMyPage } = require("./helpers");

test("训练者可以关注推荐对象，并在我关注的列表里看到对方", async ({ page }) => {
  await registerEnthusiast(page, { name: "关注测试用户" });

  await page.locator('.bottom-nav [data-page="discover"]').evaluate((element) => element.click());
  await expect(page.getByRole("heading", { name: "推荐关注" })).toBeVisible();

  const firstCard = page.locator(".discover-avatar-card").first();
  const targetName = (await firstCard.locator("strong").textContent()).trim();
  await firstCard.locator('[data-toggle-follow]').click();

  await openMyPage(page);
  await page.locator('[data-open-my-feature="favorites"]').click();

  await expect(page.getByText("我关注的")).toBeVisible();
  await expect(page.getByText(targetName)).toBeVisible();
});
