const { test, expect } = require("@playwright/test");
const { loginWithPhone, openMyPage } = require("./helpers");

function uniquePhone(prefix = "132") {
  const randomPart = Math.floor(10000000 + Math.random() * 90000000);
  return `${prefix}${randomPart}`.slice(0, 11);
}

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

async function registerApiEnthusiast(request, { name, phone }) {
  const bootstrap = await expectOk(await request.get("/api/bootstrap"), `bootstrap ${name}`);
  const sessionId = bootstrap.session.id;
  const codePayload = await postJson(request, "/api/auth/send-code", sessionId, {
    phone,
    purpose: "register",
  });
  const registered = await postJson(request, "/api/register", sessionId, {
    role: "enthusiast",
    verificationCode: codePayload.debugCode,
    profile: {
      name,
      phone,
      gender: "女",
      heightCm: 166,
      weightKg: 54,
      goal: "记录训练生活",
      intro: "用于消息中心回归测试的账号",
    },
  });

  return {
    name,
    phone,
    sessionId,
    profileId: registered.session.currentActorProfileId,
    handle:
      registered.profiles.find((profile) => profile.id === registered.session.currentActorProfileId)?.handle || "",
  };
}

async function seedMessageCenterScenario(request) {
  const unique = Date.now();
  const author = await registerApiEnthusiast(request, {
    name: `消息作者${String(unique).slice(-4)}`,
    phone: uniquePhone("132"),
  });
  const actor = await registerApiEnthusiast(request, {
    name: `互动用户${String(unique).slice(-4)}`,
    phone: uniquePhone("133"),
  });

  const postText = `消息中心动态 ${unique}`;
  const createdPost = await postJson(request, "/api/post/create", author.sessionId, {
    profileId: author.profileId,
    content: postText,
    meta: "训练分享 · 厦门 · 思明区",
    media: [],
  });
  const post = createdPost.profiles
    .flatMap((profile) => profile.posts || [])
    .find((item) => item.content === postText);
  expect(post, "seeded post should exist").toBeTruthy();

  await postJson(request, "/api/post/like", actor.sessionId, {
    postId: post.id,
  });

  const commentText = `消息中心评论 ${String(unique).slice(-5)}`;
  await postJson(request, "/api/post/comment", actor.sessionId, {
    postId: post.id,
    text: commentText,
  });

  const mentionText = `${author.handle} 今天一起练肩吗 ${String(unique).slice(-5)}`;
  await postJson(request, "/api/post/create", actor.sessionId, {
    profileId: actor.profileId,
    content: mentionText,
    meta: "@我回归 · 厦门 · 思明区",
    media: [],
  });

  await postJson(request, "/api/follow/toggle", actor.sessionId, {
    targetProfileId: author.profileId,
  });

  const directMessage = `消息中心私信 ${String(unique).slice(-5)}`;
  await postJson(request, "/api/message/send", actor.sessionId, {
    targetProfileId: author.profileId,
    text: directMessage,
  });

  return {
    author,
    actor,
    postText,
    commentText,
    mentionText,
    directMessage,
  };
}

test("消息中心能集中显示赞、评论和私信咨询", async ({ page, request }) => {
  const scenario = await seedMessageCenterScenario(request);

  await loginWithPhone(page, {
    phone: scenario.author.phone,
    role: "enthusiast",
  });

  await openMyPage(page);
  await page.locator('[data-open-my-feature="messages"]').click();

  await expect(page.getByRole("heading", { name: "消息", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "互动消息" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "私信咨询" })).toBeVisible();

  const likeNotification = page
    .locator(".feature-follow-item", { hasText: "赞了你的动态" })
    .filter({ hasText: scenario.actor.name })
    .first();
  await expect(likeNotification).toBeVisible();
  await expect(likeNotification.locator(".status-pill")).toContainText("赞");

  const commentNotification = page
    .locator(".feature-follow-item", { hasText: scenario.commentText })
    .filter({ hasText: scenario.actor.name })
    .first();
  await expect(commentNotification).toBeVisible();
  await expect(commentNotification.locator(".status-pill")).toContainText("评论");

  const mentionNotification = page
    .locator(".feature-follow-item", { hasText: scenario.mentionText })
    .filter({ hasText: scenario.actor.name })
    .first();
  await expect(mentionNotification).toBeVisible();
  await expect(mentionNotification.locator(".status-pill")).toContainText("@我");

  const messageThread = page
    .locator(".feature-follow-item", { hasText: scenario.directMessage })
    .filter({ hasText: scenario.actor.name })
    .first();
  await expect(messageThread).toBeVisible();
  await expect(messageThread.locator(".avatar-unread-badge")).toBeVisible();

  await messageThread.locator("[data-open-chat]").click();
  await expect(page.locator(".chat-thread")).toContainText(scenario.directMessage);
});
