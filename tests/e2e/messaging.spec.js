const { test, expect } = require("@playwright/test");
const { registerEnthusiast } = require("./helpers");

test("训练者关注后可以私信，并且消息会即时出现在聊天气泡里", async ({ page }) => {
  await registerEnthusiast(page, { name: "私信测试用户" });

  await page.locator('.bottom-nav [data-page="discover"]').evaluate((element) => element.click());
  await expect(page.getByRole("heading", { name: "推荐关注" })).toBeVisible();

  const firstCard = page.locator(".discover-avatar-card").first();
  await firstCard.locator(".discover-avatar-button").click();
  await expect(page.getByRole("heading", { name: "主页", exact: true })).toBeVisible();

  const followButton = page.locator('[data-toggle-follow]').first();
  await followButton.click();
  await page.locator('[data-open-chat]').first().click();

  const message = "Playwright 私信测试消息";
  await page.locator('[data-chat-input="1"]').fill(message);
  const submit = page.locator('#chatForm button[type="submit"]');
  await expect(submit).toBeEnabled();
  await submit.click();

  await expect(page.locator(".chat-thread")).toContainText(message);
});
