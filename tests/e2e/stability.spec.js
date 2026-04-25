const { test, expect } = require("@playwright/test");

test("后端唤醒较慢时显示轻提示并在同步完成后自动消失", async ({ page }) => {
  let delayed = false;
  await page.route("**/api/bootstrap**", async (route) => {
    if (!delayed) {
      delayed = true;
      await new Promise((resolve) => setTimeout(resolve, 3100));
    }
    await route.continue();
  });

  await page.goto("/");
  const notice = page.locator(".connection-notice");
  await expect(notice).toContainText("正在唤醒 FitHub 服务");
  await expect
    .poll(async () => page.evaluate(() => Boolean(window.__FITHUB_BOOTSTRAP_DONE__)))
    .toBe(true);
  await expect(notice).toHaveCount(0);
});
