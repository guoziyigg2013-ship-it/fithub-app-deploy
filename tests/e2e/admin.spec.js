const { test, expect } = require("@playwright/test");

const TINY_PNG =
  "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wn0n8kAAAAASUVORK5CYII=";

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

async function seedRiskyAuthor(request) {
  const bootstrap = await expectOk(await request.get("/api/bootstrap"), "bootstrap");
  const sessionId = bootstrap.session.id;
  const phone = `139${String(Date.now()).slice(-8)}`;
  const codePayload = await postJson(request, "/api/auth/send-code", sessionId, {
    phone,
    purpose: "register",
  });
  const registered = await postJson(request, "/api/register", sessionId, {
    role: "enthusiast",
    verificationCode: codePayload.debugCode,
    profile: {
      name: "后台限制作者",
      phone,
      gender: "男",
      heightCm: 176,
      weightKg: 70,
      goal: "测试运营风控",
      intro: "用于后台封禁回归",
    },
  });
  const authorProfileId = registered.session.currentActorProfileId;
  await postJson(request, "/api/post/create", sessionId, {
    profileId: authorProfileId,
    content: "这是一条提醒私下付款的风险动态。",
    meta: "运营后台测试",
    media: [],
  });
  return { authorProfileId };
}

test("运营审核后台可以查看并处理媒体风险队列", async ({ page, request }) => {
  await request.post("/api/media/upload", {
    data: {
      dataUrl: TINY_PNG,
      fileName: "unsafe-adult-admin-demo.png",
      assetType: "image",
      category: "posts"
    }
  });

  await page.goto("/admin.html");
  await expect(page.getByRole("heading", { name: "运营审核后台" })).toBeVisible();
  await page.locator("#adminToken").fill("test-maintenance-token");
  await page.getByRole("button", { name: "加载后台" }).click();

  await expect(page.locator("#adminStatus")).toContainText("后台数据已同步");
  await expect(page.locator("#queueList")).toContainText("成人内容风险");
  await expect(page.locator("#queueList")).toContainText("unsafe-adult-admin-demo.png");

  await page.locator('#queueList [data-status="resolved"]').first().click();
  await expect(page.locator("#adminStatus")).toContainText("已处理完成");
  await expect(page.locator("#queueList")).toContainText("暂时没有待审核内容");
});

test("运营审核后台可以限制并恢复风险内容作者", async ({ page, request }) => {
  await seedRiskyAuthor(request);

  await page.goto("/admin.html");
  await page.locator("#adminToken").fill("test-maintenance-token");
  await page.getByRole("button", { name: "加载后台" }).click();

  await expect(page.locator("#queueList")).toContainText("站外交易风险");
  await page.locator("#queueList [data-profile-moderation][data-status='suspended']").first().click();
  await expect(page.locator("#adminStatus")).toContainText("已限制该账号");
  await expect(page.locator("#suspendedList")).toContainText("后台限制作者");

  await page.locator("#suspendedList [data-profile-moderation][data-status='active']").first().click();
  await expect(page.locator("#adminStatus")).toContainText("已解除账号限制");
  await expect(page.locator("#suspendedList")).toContainText("暂时没有被限制的账号");
});
