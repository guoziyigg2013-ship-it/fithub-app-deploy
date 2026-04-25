const { test, expect } = require("@playwright/test");
const { gotoApp, registerEnthusiast, openMyPage } = require("./helpers");

async function followDemoGym(page) {
  await page.evaluate(async () => {
    const sessionId = window.localStorage.getItem("fithub_trial_session_id") || "";
    const response = await fetch("/api/follow/toggle", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sessionId, targetProfileId: "gym-demo-a" }),
    });
    if (!response.ok) {
      throw new Error(await response.text());
    }
  });
}

async function expectLastRenderUnder(page, pageName, budgetMs) {
  const metric = await page.evaluate((name) => {
    const metrics = window.__FITHUB_RENDER_METRICS__ || [];
    return [...metrics].reverse().find((item) => item.page === name) || null;
  }, pageName);
  expect(metric, `${pageName} render metric`).toBeTruthy();
  expect(metric.durationMs, `${pageName} render budget`).toBeLessThan(budgetMs);
}

test("最终验收：核心页面切换和高频互动保持即时反馈", async ({ page }) => {
  await registerEnthusiast(page, { name: "最终验收用户" });
  await followDemoGym(page);
  await gotoApp(page);

  await page.locator('.bottom-nav [data-page="home"]').evaluate((element) => element.click());
  await expect(page.locator('#appView[data-page="home"]')).toBeVisible();
  await expectLastRenderUnder(page, "home", 1600);

  await page.locator('.bottom-nav [data-page="discover"]').evaluate((element) => element.click());
  await expect(page.getByRole("heading", { name: "关注动态" })).toBeVisible();
  await expectLastRenderUnder(page, "discover", 1600);

  const firstPost = page.locator(".timeline-card", { hasText: "模拟健身房 A" }).first();
  await expect(firstPost).toBeVisible();
  const likeButton = firstPost.locator("[data-like-post]").first();
  const likeNumber = likeButton.locator(".post-action-number");
  const favoriteButton = firstPost.locator("[data-favorite-post]").first();
  const favoriteNumber = favoriteButton.locator(".post-action-number");
  const initialLikeCount = Number((await likeNumber.textContent()) || 0);
  const initialFavoriteCount = Number((await favoriteNumber.textContent()) || 0);

  await page.route("**/api/post/like", async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 1200));
    await route.continue();
  });
  await likeButton.click();
  await expect(likeButton).toHaveClass(/is-active/, { timeout: 300 });
  await expect(likeNumber).toHaveText(String(initialLikeCount + 1), { timeout: 300 });
  await expect(likeButton).toBeEnabled();

  await page.route("**/api/post/favorite-toggle", async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 1200));
    await route.continue();
  });
  await favoriteButton.click();
  await expect(favoriteButton).toHaveClass(/is-active/, { timeout: 300 });
  await expect(favoriteNumber).toHaveText(String(Math.max(1, initialFavoriteCount + 1)), { timeout: 300 });
  await expect(favoriteButton).toBeEnabled();

  await page.locator('.bottom-nav [data-page="booking"]').evaluate((element) => element.click());
  await expect(page.getByRole("heading", { name: "预约" })).toBeVisible();
  await expectLastRenderUnder(page, "booking", 1600);

  await openMyPage(page);
  await expectLastRenderUnder(page, "profile", 1600);
  await expect(page.getByText("我的功能")).toBeVisible();
});
