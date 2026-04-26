const { test, expect } = require("@playwright/test");
const { buildUniquePhone, gotoApp, registerCoach, registerEnthusiast, registerGym, openMyPage } = require("./helpers");

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

test("推荐关注点击后立即移出推荐区，慢网络不会诱导重复关注", async ({ page }) => {
  await registerEnthusiast(page, { name: "即时关注反馈用户" });

  await page.locator('.bottom-nav [data-page="discover"]').evaluate((element) => element.click());
  await expect(page.getByRole("heading", { name: "推荐关注" })).toBeVisible();

  const firstCard = page.locator(".discover-avatar-card").first();
  const targetName = (await firstCard.locator("strong").textContent()).trim();
  const targetProfileId = await firstCard.locator("[data-toggle-follow]").getAttribute("data-toggle-follow");
  let releaseFollow;
  let markFollowRequestStarted;
  const followCanContinue = new Promise((resolve) => {
    releaseFollow = resolve;
  });
  const followRequestStarted = new Promise((resolve) => {
    markFollowRequestStarted = resolve;
  });

  await page.route("**/api/follow/toggle", async (route) => {
    markFollowRequestStarted();
    await followCanContinue;
    await route.continue();
  });

  const renderCountBefore = await page.evaluate(() => window.__FITHUB_RENDER_METRICS__?.length || 0);
  await firstCard.locator("[data-toggle-follow]").click();
  await followRequestStarted;
  await expect(page.locator(`.discover-avatar-card[data-profile-id="${targetProfileId}"]`)).toHaveCount(0, { timeout: 300 });
  await expect
    .poll(async () => page.evaluate(() => window.__FITHUB_RENDER_METRICS__?.length || 0), {
      timeout: 300,
      message: "关注点击应局部反馈，不应整页重绘导致闪动",
    })
    .toBe(renderCountBefore);

  releaseFollow();
  await openMyPage(page);
  await page.locator('[data-open-my-feature="favorites"]').click();
  await expect(page.getByText(targetName)).toBeVisible();
});

test("健身房身份关注推荐对象也会立即反馈并移出推荐区", async ({ page }) => {
  await registerGym(page, { name: "即时关注反馈场馆" });

  await page.locator('.bottom-nav [data-page="discover"]').evaluate((element) => element.click());
  await expect(page.getByRole("heading", { name: "推荐关注" })).toBeVisible();

  const firstCard = page.locator(".discover-avatar-card").first();
  await expect(firstCard).toBeVisible();
  const targetName = (await firstCard.locator("strong").textContent()).trim();
  const targetProfileId = await firstCard.locator("[data-toggle-follow]").getAttribute("data-toggle-follow");
  let releaseFollow;
  let markFollowRequestStarted;
  const followCanContinue = new Promise((resolve) => {
    releaseFollow = resolve;
  });
  const followRequestStarted = new Promise((resolve) => {
    markFollowRequestStarted = resolve;
  });

  let followPayload = null;
  await page.route("**/api/follow/toggle", async (route) => {
    followPayload = route.request().postDataJSON();
    markFollowRequestStarted();
    await followCanContinue;
    await route.continue();
  });

  const renderCountBefore = await page.evaluate(() => window.__FITHUB_RENDER_METRICS__?.length || 0);
  await firstCard.locator("[data-toggle-follow]").click();
  await followRequestStarted;
  await expect(page.locator(`.discover-avatar-card[data-profile-id="${targetProfileId}"]`)).toHaveCount(0, { timeout: 300 });
  expect(followPayload).toMatchObject({
    compact: true,
    targetProfileId,
    desiredFollowing: true,
    selectedRole: "gym",
  });
  expect(followPayload.sourceProfileId).toBeTruthy();
  await expect
    .poll(async () => page.evaluate(() => window.__FITHUB_RENDER_METRICS__?.length || 0), {
      timeout: 300,
      message: "健身房关注点击应局部反馈，不应整页重绘导致闪动",
    })
    .toBe(renderCountBefore);

  releaseFollow();
  await openMyPage(page);
  await page.locator('[data-open-my-feature="favorites"]').click();
  await expect(page.getByText(targetName)).toBeVisible();
});

test("教练身份关注推荐对象也会立即反馈并移出推荐区", async ({ page }) => {
  await registerCoach(page, { name: "即时关注反馈教练" });

  await page.locator('.bottom-nav [data-page="discover"]').evaluate((element) => element.click());
  await expect(page.getByRole("heading", { name: "推荐关注" })).toBeVisible();

  const firstCard = page.locator(".discover-avatar-card").first();
  await expect(firstCard).toBeVisible();
  const targetName = (await firstCard.locator("strong").textContent()).trim();
  const targetProfileId = await firstCard.locator("[data-toggle-follow]").getAttribute("data-toggle-follow");
  let releaseFollow;
  let markFollowRequestStarted;
  const followCanContinue = new Promise((resolve) => {
    releaseFollow = resolve;
  });
  const followRequestStarted = new Promise((resolve) => {
    markFollowRequestStarted = resolve;
  });

  let followPayload = null;
  await page.route("**/api/follow/toggle", async (route) => {
    followPayload = route.request().postDataJSON();
    markFollowRequestStarted();
    await followCanContinue;
    await route.continue();
  });

  const renderCountBefore = await page.evaluate(() => window.__FITHUB_RENDER_METRICS__?.length || 0);
  await firstCard.locator("[data-toggle-follow]").click();
  await followRequestStarted;
  await expect(page.locator(`.discover-avatar-card[data-profile-id="${targetProfileId}"]`)).toHaveCount(0, { timeout: 300 });
  expect(followPayload).toMatchObject({
    compact: true,
    targetProfileId,
    desiredFollowing: true,
    selectedRole: "coach",
  });
  expect(followPayload.sourceProfileId).toBeTruthy();
  await expect
    .poll(async () => page.evaluate(() => window.__FITHUB_RENDER_METRICS__?.length || 0), {
      timeout: 300,
      message: "教练关注点击应局部反馈，不应整页重绘导致闪动",
    })
    .toBe(renderCountBefore);

  releaseFollow();
  await openMyPage(page);
  await page.locator('[data-open-my-feature="favorites"]').click();
  await expect(page.getByText(targetName)).toBeVisible();
});

test("多身份切换先本地即时反馈，再后台同步", async ({ page }) => {
  const phone = buildUniquePhone();
  await registerEnthusiast(page, { name: "身份切换训练者", phone });
  await registerCoach(page, { name: "身份切换教练", phone });

  await openMyPage(page);
  await expect(page.getByText("身份切换教练")).toBeVisible();

  let releaseSelect;
  let markSelectStarted;
  const selectCanContinue = new Promise((resolve) => {
    releaseSelect = resolve;
  });
  const selectStarted = new Promise((resolve) => {
    markSelectStarted = resolve;
  });

  await page.route("**/api/session/select", async (route) => {
    markSelectStarted();
    await selectCanContinue;
    await route.continue();
  });

  await page
    .locator(".managed-strip--dashboard [data-switch-managed]")
    .filter({ hasText: "健身爱好者" })
    .click();
  await selectStarted;
  await expect(page.getByText("身份切换训练者")).toBeVisible({ timeout: 300 });

  releaseSelect();
  await expect(page.getByText("身份切换训练者")).toBeVisible();
});

test("同一账号的教练身份可以关注自己的训练者身份", async ({ page }) => {
  const phone = buildUniquePhone();
  const enthusiast = await registerEnthusiast(page, { name: "自我关注训练者", phone });
  await registerCoach(page, { name: "自我关注教练", phone });

  const ids = await page.evaluate(async () => {
    const sessionId = window.localStorage.getItem("fithub_trial_session_id") || "";
    const payload = await fetch(`/api/bootstrap?session_id=${encodeURIComponent(sessionId)}`).then((response) => response.json());
    return {
      enthusiastId: payload.profiles.find((profile) => profile.name === "自我关注训练者")?.id || "",
      coachId: payload.profiles.find((profile) => profile.name === "自我关注教练")?.id || "",
    };
  });
  expect(ids.enthusiastId).toBeTruthy();
  expect(ids.coachId).toBeTruthy();

  await page.evaluate((profileId) => {
    const button = document.createElement("button");
    button.dataset.openProfile = profileId;
    button.type = "button";
    document.querySelector("#appView").appendChild(button);
    button.click();
    button.remove();
  }, ids.enthusiastId);

  await expect(page.getByRole("heading", { name: enthusiast.name })).toBeVisible();
  const followButton = page.locator(`[data-toggle-follow="${ids.enthusiastId}"]`).first();
  await expect(followButton).toBeVisible();
  await followButton.click();
  await expect(followButton).toHaveText("已关注");

  await openMyPage(page);
  await page.locator('[data-open-my-feature="favorites"]').click();
  await expect(page.getByText("自我关注训练者")).toBeVisible();
});

test("其他身份有新私信时，顶部身份栏显示提醒角标", async ({ page }) => {
  const phone = buildUniquePhone();
  await registerEnthusiast(page, { name: "角标训练者", phone });
  await registerCoach(page, { name: "角标教练", phone });

  const ids = await page.evaluate(async () => {
    const sessionId = window.localStorage.getItem("fithub_trial_session_id") || "";
    const payload = await fetch(`/api/bootstrap?session_id=${encodeURIComponent(sessionId)}`).then((response) => response.json());
    return {
      sessionId,
      enthusiastId: payload.profiles.find((profile) => profile.name === "角标训练者")?.id || "",
      coachId: payload.profiles.find((profile) => profile.name === "角标教练")?.id || "",
    };
  });
  expect(ids.enthusiastId).toBeTruthy();
  expect(ids.coachId).toBeTruthy();

  await page.evaluate(async ({ sessionId, enthusiastId, coachId }) => {
    await fetch("/api/follow/toggle", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sessionId,
        sourceProfileId: enthusiastId,
        selectedRole: "enthusiast",
        targetProfileId: coachId,
        desiredFollowing: true,
      }),
    });
    await fetch("/api/message/send", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sessionId,
        targetProfileId: coachId,
        text: "教练身份提醒角标测试",
      }),
    });
  }, ids);

  await gotoApp(page);
  await openMyPage(page);
  const coachChip = page.locator(".managed-strip--dashboard [data-switch-managed]").filter({ hasText: "健身教练" });
  await expect(coachChip.locator(".managed-chip-badge")).toHaveText("1");
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
