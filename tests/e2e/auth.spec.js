const { test, expect } = require("@playwright/test");
const { registerEnthusiast, gotoApp, loginWithPhone, openMyPage } = require("./helpers");

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
