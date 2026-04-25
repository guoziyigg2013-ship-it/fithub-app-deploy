const { test, expect } = require("@playwright/test");
const {
  registerCoach,
  registerEnthusiast,
  registerGym,
  gotoApp,
  loginWithPhone,
  openMyPage,
} = require("./helpers");

test("训练者注册后同设备重进会自动恢复，退出后可验证码重新登录", async ({ browser }) => {
  const context = await browser.newContext();
  const page = await context.newPage();

  const account = await registerEnthusiast(page, { name: "自动恢复用户" });

  const secondPage = await context.newPage();
  await gotoApp(secondPage);
  await openMyPage(secondPage);
  await expect(secondPage.getByText("自动恢复用户")).toBeVisible();

  await secondPage.getByRole("button", { name: "切换身份" }).click();
  await secondPage.getByRole("button", { name: "退出登录" }).click();
  await expect(secondPage.getByRole("button", { name: "登录已有账户" })).toBeVisible();

  await loginWithPhone(secondPage, { phone: account.phone, role: "enthusiast" });
  await openMyPage(secondPage);
  await expect(secondPage.getByText("自动恢复用户")).toBeVisible();

  await context.close();
});

test("教练和健身房注册后可跨设备登录回到各自主页", async ({ browser }) => {
  const coachContext = await browser.newContext();
  const coachRegisterPage = await coachContext.newPage();
  const coach = await registerCoach(coachRegisterPage, { name: "跨端测试教练" });
  await coachContext.close();

  const coachLoginContext = await browser.newContext();
  const coachLoginPage = await coachLoginContext.newPage();
  await loginWithPhone(coachLoginPage, { phone: coach.phone, role: "coach" });
  await openMyPage(coachLoginPage);
  await expect(coachLoginPage.getByText("跨端测试教练")).toBeVisible();
  await expect(coachLoginPage.getByText("健身教练").first()).toBeVisible();
  await coachLoginContext.close();

  const gymContext = await browser.newContext();
  const gymRegisterPage = await gymContext.newPage();
  const gym = await registerGym(gymRegisterPage, { name: "跨端测试健身房" });
  await gymContext.close();

  const gymLoginContext = await browser.newContext();
  const gymLoginPage = await gymLoginContext.newPage();
  await loginWithPhone(gymLoginPage, { phone: gym.phone, role: "gym" });
  await openMyPage(gymLoginPage);
  await expect(gymLoginPage.getByText("跨端测试健身房")).toBeVisible();
  await expect(gymLoginPage.getByText("健身房").first()).toBeVisible();
  await gymLoginContext.close();
});
