const { test, expect } = require("@playwright/test");
const { gotoApp, registerEnthusiast, openMyPage } = require("./helpers");

const TINY_PNG_BUFFER = Buffer.from(
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wn0n8kAAAAASUVORK5CYII=",
  "base64"
);
const TINY_VIDEO_BUFFER = Buffer.from([0, 0, 0, 0]);

async function expectOk(response, label) {
  expect(response.ok(), `${label}: ${response.status()} ${await response.text()}`).toBeTruthy();
  return response.json();
}

async function postJson(request, path, sessionId, data = {}) {
  return expectOk(
    await request.post(path, {
      data: {
        sessionId,
        ...data,
      },
    }),
    path
  );
}

async function seedAuthorWithMediaPost(request) {
  const bootstrap = await expectOk(await request.get("/api/bootstrap"), "bootstrap");
  const sessionId = bootstrap.session.id;
  const phone = `132${String(Date.now()).slice(-8)}`;
  const codePayload = await postJson(request, "/api/auth/send-code", sessionId, {
    phone,
    purpose: "register",
  });
  const registered = await postJson(request, "/api/register", sessionId, {
    role: "enthusiast",
    verificationCode: codePayload.debugCode,
    profile: {
      name: "媒体作者",
      phone,
      gender: "女",
      heightCm: 168,
      weightKg: 55,
      goal: "分享训练动作",
      intro: "用于媒体流回归的作者账号",
    },
  });
  const authorProfileId = registered.session.currentActorProfileId;
  const dataUrl = `data:image/png;base64,${TINY_PNG_BUFFER.toString("base64")}`;
  const uploaded = await postJson(request, "/api/media/upload", sessionId, {
    dataUrl,
    fileName: "seeded-media.png",
    assetType: "image",
    category: "posts",
    thumbnailDataUrl: dataUrl,
    thumbnailName: "seeded-media-thumb.png",
  });
  const postText = `关注媒体动态 ${Date.now()}`;
  await postJson(request, "/api/post/create", sessionId, {
    profileId: authorProfileId,
    content: postText,
    meta: "媒体作者 · 厦门 · 思明区",
    media: [uploaded.media],
  });
  return { authorProfileId, postText };
}

async function seedAuthorWithTextPost(request) {
  const bootstrap = await expectOk(await request.get("/api/bootstrap"), "bootstrap");
  const sessionId = bootstrap.session.id;
  const phone = `133${String(Date.now()).slice(-8)}`;
  const codePayload = await postJson(request, "/api/auth/send-code", sessionId, {
    phone,
    purpose: "register",
  });
  const registered = await postJson(request, "/api/register", sessionId, {
    role: "enthusiast",
    verificationCode: codePayload.debugCode,
    profile: {
      name: "文字收藏作者",
      phone,
      gender: "男",
      heightCm: 172,
      weightKg: 63,
      goal: "记录训练心得",
      intro: "用于纯文字收藏回归的作者账号",
    },
  });
  const authorProfileId = registered.session.currentActorProfileId;
  const postText = `纯文字收藏动态 ${Date.now()}`;
  await postJson(request, "/api/post/create", sessionId, {
    profileId: authorProfileId,
    content: postText,
    meta: "文字作者 · 厦门 · 思明区",
    media: [],
  });
  return { authorProfileId, postText };
}

async function seedAuthorWithVideoPost(request) {
  const bootstrap = await expectOk(await request.get("/api/bootstrap"), "bootstrap");
  const sessionId = bootstrap.session.id;
  const phone = `136${String(Date.now()).slice(-8)}`;
  const codePayload = await postJson(request, "/api/auth/send-code", sessionId, {
    phone,
    purpose: "register",
  });
  const registered = await postJson(request, "/api/register", sessionId, {
    role: "enthusiast",
    verificationCode: codePayload.debugCode,
    profile: {
      name: "视频内容作者",
      phone,
      gender: "女",
      heightCm: 166,
      weightKg: 54,
      goal: "分享动作讲解视频",
      intro: "用于视频媒体流回归的作者账号",
    },
  });
  const authorProfileId = registered.session.currentActorProfileId;
  const dataUrl = `data:video/mp4;base64,${TINY_VIDEO_BUFFER.toString("base64")}`;
  const posterUrl = `data:image/png;base64,${TINY_PNG_BUFFER.toString("base64")}`;
  const uploaded = await postJson(request, "/api/media/upload", sessionId, {
    dataUrl,
    fileName: "seeded-video.mp4",
    assetType: "video",
    category: "posts",
    thumbnailDataUrl: posterUrl,
    thumbnailName: "seeded-video-poster.png",
  });
  const postText = `视频训练动态 ${Date.now()}`;
  await postJson(request, "/api/post/create", sessionId, {
    profileId: authorProfileId,
    content: postText,
    meta: "视频作者 · 厦门 · 思明区",
    media: [uploaded.media],
  });
  return { authorProfileId, postText };
}

test("训练者可以发布图片动态、收藏媒体，并在刷新后继续打开", async ({ page, request }) => {
  const ownPostText = `媒体回归动态 ${Date.now()}`;
  await registerEnthusiast(page, { name: "媒体测试用户" });

  await page.locator("#fabButton").click();
  await expect(page.locator("#composeForm")).toBeVisible();
  await page.locator('[data-compose-content="1"]').fill(ownPostText);
  await page.locator('input[data-compose-media-input][accept="image/*"]').setInputFiles({
    name: "media-regression.png",
    mimeType: "image/png",
    buffer: TINY_PNG_BUFFER,
  });
  await expect(page.locator(".compose-preview-card")).toBeVisible({ timeout: 10000 });
  await page.locator('#composeForm button[type="submit"]').click();

  const ownMoment = page.locator(".moment-card", { hasText: ownPostText }).first();
  await expect(ownMoment).toBeVisible({ timeout: 10000 });
  await expect(ownMoment.locator(".timeline-media-card")).toBeVisible();

  const seeded = await seedAuthorWithMediaPost(request);
  await page.evaluate(async ({ targetProfileId }) => {
    const sessionId = window.localStorage.getItem("fithub_trial_session_id") || "";
    const response = await fetch("/api/follow/toggle", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sessionId, targetProfileId }),
    });
    if (!response.ok) {
      throw new Error(await response.text());
    }
  }, { targetProfileId: seeded.authorProfileId });

  await gotoApp(page);
  await page.locator('.bottom-nav [data-page="discover"]').evaluate((element) => element.click());
  const postCard = page.locator(".timeline-card", { hasText: seeded.postText }).first();
  await expect(postCard).toBeVisible({ timeout: 10000 });
  const favoriteButton = postCard.locator("[data-favorite-post]");
  const favoriteNumber = favoriteButton.locator(".post-action-number");
  await favoriteButton.click();
  await expect(favoriteButton).toHaveClass(/is-active/);
  await expect(favoriteNumber).toHaveText("1");
  await expect(favoriteButton).toBeEnabled();
  await favoriteButton.click();
  await expect(favoriteButton).not.toHaveClass(/is-active/);
  await expect(favoriteNumber).toHaveText("0");
  await expect(favoriteButton).toBeEnabled();
  await favoriteButton.click();
  await expect(favoriteButton).toHaveClass(/is-active/);
  await expect(favoriteNumber).toHaveText("1");
  await expect(favoriteButton).toBeEnabled();

  await openMyPage(page);
  await page.locator('[data-open-my-feature="collections"]').click();
  const collectionCard = page.locator(".timeline-card", { hasText: seeded.postText }).first();
  await expect(collectionCard).toBeVisible();
  await collectionCard.locator("[data-open-media-detail]").first().click();
  await expect(page.getByText("媒体详情")).toBeVisible();
  await expect(page.getByText("图片", { exact: true })).toBeVisible();
  await page.locator(".close-button").click();

  await gotoApp(page);
  await openMyPage(page);
  await page.locator('[data-open-my-feature="collections"]').click();
  await expect(page.locator(".timeline-card", { hasText: seeded.postText }).first()).toBeVisible();
});

test("探索流首屏动态媒体保持高优先级加载，作者头像不走懒加载", async ({ page, request }) => {
  await registerEnthusiast(page, { name: "媒体性能测试用户" });

  const seeded = await seedAuthorWithMediaPost(request);
  await page.evaluate(async ({ targetProfileId }) => {
    const sessionId = window.localStorage.getItem("fithub_trial_session_id") || "";
    const response = await fetch("/api/follow/toggle", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sessionId, targetProfileId }),
    });
    if (!response.ok) {
      throw new Error(await response.text());
    }
  }, { targetProfileId: seeded.authorProfileId });

  await gotoApp(page);
  await page.locator('.bottom-nav [data-page="discover"]').evaluate((element) => element.click());
  const postCard = page.locator(".timeline-card", { hasText: seeded.postText }).first();
  await expect(postCard).toBeVisible({ timeout: 10000 });

  const mediaImage = postCard.locator("img.timeline-media-image").first();
  await expect(mediaImage).toBeVisible();
  await expect(mediaImage).toHaveAttribute("loading", "eager");
  await expect(mediaImage).toHaveAttribute("fetchpriority", "high");

  const authorAvatar = postCard.locator(".timeline-author img.avatar-image").first();
  await expect(authorAvatar).toBeVisible();
  await expect(authorAvatar).not.toHaveAttribute("loading", "lazy");
});

test("训练者可以收藏纯文字动态，并在收藏页长期可见", async ({ page, request }) => {
  await registerEnthusiast(page, { name: "文字收藏测试用户" });

  const seeded = await seedAuthorWithTextPost(request);
  await page.evaluate(async ({ targetProfileId }) => {
    const sessionId = window.localStorage.getItem("fithub_trial_session_id") || "";
    const response = await fetch("/api/follow/toggle", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sessionId, targetProfileId }),
    });
    if (!response.ok) {
      throw new Error(await response.text());
    }
  }, { targetProfileId: seeded.authorProfileId });

  await gotoApp(page);
  await page.locator('.bottom-nav [data-page="discover"]').evaluate((element) => element.click());
  const postCard = page.locator(".timeline-card", { hasText: seeded.postText }).first();
  await expect(postCard).toBeVisible({ timeout: 10000 });
  await expect(postCard.locator(".timeline-media-card")).toHaveCount(0);

  const favoriteButton = postCard.locator("[data-favorite-post]");
  await favoriteButton.click();
  await expect(favoriteButton).toHaveClass(/is-active/);
  await expect(favoriteButton.locator(".post-action-number")).toHaveText("1");

  await openMyPage(page);
  await page.locator('[data-open-my-feature="collections"]').click();
  const collectionCard = page.locator(".timeline-card", { hasText: seeded.postText }).first();
  await expect(collectionCard).toBeVisible();
  await expect(collectionCard.locator(".timeline-media-card")).toHaveCount(0);
});

test("视频动态在信息流只加载封面，收藏后可打开视频详情", async ({ page, request }) => {
  await registerEnthusiast(page, { name: "视频收藏测试用户" });

  const seeded = await seedAuthorWithVideoPost(request);
  await page.evaluate(async ({ targetProfileId }) => {
    const sessionId = window.localStorage.getItem("fithub_trial_session_id") || "";
    const response = await fetch("/api/follow/toggle", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sessionId, targetProfileId }),
    });
    if (!response.ok) {
      throw new Error(await response.text());
    }
  }, { targetProfileId: seeded.authorProfileId });

  await gotoApp(page);
  await page.locator('.bottom-nav [data-page="discover"]').evaluate((element) => element.click());
  const postCard = page.locator(".timeline-card", { hasText: seeded.postText }).first();
  await expect(postCard).toBeVisible({ timeout: 10000 });
  const mediaCard = postCard.locator(".timeline-media-card--video").first();
  await expect(mediaCard).toBeVisible();
  await expect(mediaCard.locator(".timeline-video-play")).toBeVisible();
  await expect(mediaCard.locator("img.timeline-media-image")).toBeVisible();
  await expect(mediaCard.locator("video.timeline-media-video")).toHaveCount(0);

  const favoriteButton = postCard.locator("[data-favorite-post]");
  await favoriteButton.click();
  await expect(favoriteButton).toHaveClass(/is-active/);
  await expect(favoriteButton.locator(".post-action-number")).toHaveText("1");

  await openMyPage(page);
  await page.locator('[data-open-my-feature="collections"]').click();
  const collectionCard = page.locator(".timeline-card", { hasText: seeded.postText }).first();
  await expect(collectionCard).toBeVisible();
  await expect(collectionCard.locator(".timeline-media-card--video")).toBeVisible();

  await collectionCard.locator("[data-open-media-detail]").first().click();
  await expect(page.getByText("媒体详情")).toBeVisible();
  await expect(page.locator(".media-detail-pill", { hasText: "视频" }).first()).toBeVisible();
  await expect(page.locator("video.media-detail-video")).toBeVisible();
});
