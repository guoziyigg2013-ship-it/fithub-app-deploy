const { test, expect } = require("@playwright/test");
const { registerEnthusiast, loginWithPhone } = require("./helpers");

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

async function seedCoachProvider(request) {
  const bootstrap = await expectOk(await request.get("/api/bootstrap"), "bootstrap");
  const sessionId = bootstrap.session.id;
  const phone = `139${String(Date.now()).slice(-8)}`;
  const name = `预约测试教练 ${String(Date.now()).slice(-4)}`;
  const codePayload = await postJson(request, "/api/auth/send-code", sessionId, {
    phone,
    purpose: "register",
  });
  const registered = await postJson(request, "/api/register", sessionId, {
    role: "coach",
    verificationCode: codePayload.debugCode,
    profile: {
      name,
      phone,
      city: "厦门",
      locationLabel: "厦门 · 思明区",
      intro: "用于预约回归测试的一对一私教。",
      specialties: "力量 减脂 私教",
      years: "6",
      price: "¥260/小时",
      pricingPlans: [
        { title: "私教体验课", detail: "60 分钟动作评估与训练计划", price: "¥260/小时" },
      ],
    },
  });
  return {
    phone,
    name,
    sessionId,
    profileId: registered.session.currentActorProfileId,
  };
}

test("训练者可以预约教练，教练端能看到别人给我的预约", async ({ page, context, request }) => {
  const coach = await seedCoachProvider(request);
  const availability = await postJson(request, "/api/availability/create", coach.sessionId, {
    profileId: coach.profileId,
    date: "2030-05-20",
    time: "18:30",
    durationMinutes: 60,
    note: "预约回归测试时段",
  });
  const coachProfile = availability.profiles.find((profile) => profile.id === coach.profileId);
  const slot = coachProfile.availabilitySlots.find((item) => item.date === "2030-05-20" && item.time === "18:30");
  expect(slot).toBeTruthy();

  const buyer = await registerEnthusiast(page, { name: "预约测试学员" });

  await page.locator('.bottom-nav [data-page="home"]').evaluate((element) => element.click());
  await page.locator('[data-home-tab="coach"]').click();
  await page.locator('[data-search-input="1"]').fill(coach.name);

  const coachCard = page.locator(".card", { hasText: coach.name }).first();
  await expect(coachCard).toBeVisible();
  await coachCard.locator("h3").click();
  await expect(page.getByText(coach.name)).toBeVisible();
  await expect(page.getByText("可预约时间")).toBeVisible();

  await page.locator(`[data-create-booking="${coach.profileId}"][data-availability-slot="${slot.id}"]`).first().click();
  await expect(page.getByRole("heading", { name: "预约", exact: true })).toBeVisible();
  const outgoingBooking = page.locator(".booking-card", { hasText: coach.name }).first();
  await expect(outgoingBooking).toBeVisible();
  await expect(outgoingBooking).toContainText("已预约");
  await expect(outgoingBooking).toContainText("¥260/小时");
  await expect(outgoingBooking).toContainText("18:30");

  const coachPage = await context.newPage();
  await loginWithPhone(coachPage, { phone: coach.phone, role: "coach" });
  await coachPage.locator('.bottom-nav [data-page="booking"]').evaluate((element) => element.click());
  await expect(coachPage.getByRole("heading", { name: "预约", exact: true })).toBeVisible();

  const incomingBooking = coachPage.locator(".booking-card", { hasText: buyer.name }).first();
  await expect(incomingBooking).toBeVisible();
  await expect(incomingBooking).toContainText("已预约");
  await expect(incomingBooking).toContainText("健身爱好者");
  await expect(incomingBooking).toContainText("18:30");
  await coachPage.close();
});
