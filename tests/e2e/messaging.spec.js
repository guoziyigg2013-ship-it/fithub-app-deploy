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

test("私信网络未返回时仍可继续输入和发送下一条", async ({ page }) => {
  await registerEnthusiast(page, { name: "私信连发测试用户" });

  await page.locator('.bottom-nav [data-page="discover"]').evaluate((element) => element.click());
  await expect(page.getByRole("heading", { name: "推荐关注" })).toBeVisible();

  const firstCard = page.locator(".discover-avatar-card").first();
  await firstCard.locator(".discover-avatar-button").click();
  await expect(page.getByRole("heading", { name: "主页", exact: true })).toBeVisible();

  await page.locator('[data-toggle-follow]').first().click();
  await page.locator('[data-open-chat]').first().click();

  let releaseMessages;
  let firstMessageRequestStarted;
  const messagesCanContinue = new Promise((resolve) => {
    releaseMessages = resolve;
  });
  const messageRequestStarted = new Promise((resolve) => {
    firstMessageRequestStarted = resolve;
  });
  let requestCount = 0;

  await page.route("**/api/message/send", async (route) => {
    requestCount += 1;
    if (requestCount === 1) {
      firstMessageRequestStarted();
    }
    await messagesCanContinue;
    await route.continue();
  });

  const firstMessage = `第一条即时私信 ${Date.now()}`;
  const secondMessage = `第二条即时私信 ${Date.now()}`;
  const input = page.locator('[data-chat-input="1"]');
  const submit = page.locator('#chatForm button[type="submit"]');

  await input.fill(firstMessage);
  await submit.click();
  await messageRequestStarted;
  await expect(page.locator(".chat-thread")).toContainText(firstMessage, { timeout: 300 });
  await expect(input).toBeEnabled();

  await input.fill(secondMessage);
  await submit.click();
  await expect(page.locator(".chat-thread")).toContainText(secondMessage, { timeout: 300 });

  releaseMessages();
  await expect(page.locator(".chat-thread")).toContainText(firstMessage);
  await expect(page.locator(".chat-thread")).toContainText(secondMessage);
});
