const { test, expect } = require("@playwright/test");
const { gotoApp, registerEnthusiast, openMyPage } = require("./helpers");

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

test("动态点赞和取消点赞会立即反馈，连续点击不锁按钮", async ({ page }) => {
  await registerEnthusiast(page, { name: "点赞反馈测试用户" });

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
  await gotoApp(page);
  await page.locator('.bottom-nav [data-page="discover"]').evaluate((element) => element.click());

  const firstPost = page.locator(".timeline-card", { hasText: "模拟健身房 A" }).first();
  await expect(firstPost).toBeVisible();
  const likeButton = firstPost.locator("[data-like-post]").first();
  const likeNumber = likeButton.locator(".post-action-number");
  const initialCount = Number((await likeNumber.textContent()) || 0);

  await likeButton.click();
  await expect(likeButton).toHaveClass(/is-active/);
  await expect(likeNumber).toHaveText(String(initialCount + 1));
  await expect(likeButton).toBeEnabled();

  await likeButton.click();
  await expect(likeButton).not.toHaveClass(/is-active/);
  await expect(likeNumber).toHaveText(String(initialCount));
  await expect(likeButton).toBeEnabled();

  await likeButton.click();
  await expect(likeButton).toHaveClass(/is-active/);
  await expect(likeNumber).toHaveText(String(initialCount + 1));
  await expect(likeButton).toBeEnabled();
});

test("动态评论在网络确认前也会立即出现", async ({ page }) => {
  await registerEnthusiast(page, { name: "评论反馈测试用户" });

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

  await gotoApp(page);
  await page.locator('.bottom-nav [data-page="discover"]').evaluate((element) => element.click());

  let releaseComment;
  let markCommentRequestStarted;
  const commentCanContinue = new Promise((resolve) => {
    releaseComment = resolve;
  });
  const commentRequestStarted = new Promise((resolve) => {
    markCommentRequestStarted = resolve;
  });

  await page.route("**/api/post/comment", async (route) => {
    markCommentRequestStarted();
    await commentCanContinue;
    await route.continue();
  });

  const firstPost = page.locator(".timeline-card", { hasText: "模拟健身房 A" }).first();
  await expect(firstPost).toBeVisible();
  const commentText = `即时评论 ${Date.now()}`;
  await firstPost.locator("[data-comment-input]").fill(commentText);
  await firstPost.locator("[data-comment-post]").click();
  await commentRequestStarted;

  await expect(firstPost.locator(".post-comment-list")).toContainText(commentText, { timeout: 300 });
  await expect(firstPost.locator(".post-action-button--count .post-action-number")).toContainText(/[1-9]/);

  releaseComment();
  await expect(firstPost.locator(".post-comment-list")).toContainText(commentText);
});
