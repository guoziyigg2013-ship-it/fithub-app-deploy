const { expect } = require("@playwright/test");

function buildUniquePhone() {
  const stamp = `${Date.now()}`.slice(-8);
  return `132${stamp}`;
}

function extractCode(text) {
  const match = String(text || "").match(/(\d{6})/);
  if (!match) {
    throw new Error(`未能从文本中解析验证码: ${text}`);
  }
  return match[1];
}

async function gotoApp(page) {
  await page.goto("/");
  await expect(page.locator("body")).toBeVisible();
  await expect(page.locator(".bottom-nav")).toBeVisible();
  await expect(page.getByText("正在连接试用服务")).toHaveCount(0);
  await expect
    .poll(async () => page.evaluate(() => Boolean(window.__FITHUB_READY__)))
    .toBe(true);
  await expect
    .poll(async () =>
      page.evaluate(() =>
        Boolean(window.__FITHUB_BOOTSTRAP_DONE__) ||
        Boolean(document.querySelector('[data-open-role-picker="1"]'))
      )
    )
    .toBe(true);
  await page.waitForTimeout(250);
}

async function waitForBootstrapToSettle(page) {
  await expect
    .poll(async () => page.evaluate(() => Boolean(window.__FITHUB_BOOTSTRAP_DONE__)), {
      timeout: 30000,
      message: "等待应用 bootstrap 完成",
    })
    .toBe(true);
}

async function openRegister(page, role = "enthusiast") {
  await gotoApp(page);
  await waitForBootstrapToSettle(page);
  const registerForm = page.locator("#registerForm");
  const registerCodeButton = page.locator('[data-send-register-code="1"]');
  if (
    (await registerForm.isVisible().catch(() => false)) &&
    (await registerCodeButton.isVisible().catch(() => false))
  ) {
    return;
  }
  if (!(await page.locator(`[data-choose-role="${role}"]`).isVisible().catch(() => false))) {
    await page.locator('[data-open-role-picker="1"]').click();
  }
  await expect(page.locator(`[data-choose-role="${role}"]`)).toBeVisible();
  await page.locator(`[data-choose-role="${role}"]`).click();
  const directOpened = await registerForm
    .waitFor({ state: "visible", timeout: 1500 })
    .then(() => true)
    .catch(() => false);

  if (!directOpened) {
    const authButton = page.getByRole("button", { name: "登录已有账户" });
    if (await authButton.isVisible().catch(() => false)) {
      await authButton.click();
      const registerFromAuth = page.locator(`[data-open-register-from-auth="${role}"]`);
      await expect(registerFromAuth).toBeVisible();
      await registerFromAuth.click();
    }
  }

  await expect(registerForm).toBeVisible();
  await expect(registerCodeButton).toBeVisible();
}

async function sendRegisterCode(page, phone) {
  await page.locator('#registerForm input[name="phone"]').fill(phone);
  await page.locator('[data-send-register-code="1"]').click();
  const helper = page
    .locator('#registerForm input[name="verification_code"]')
    .locator('xpath=ancestor::label[contains(@class,"form-field")]//small[contains(@class,"helper-note")]');
  await expect
    .poll(async () => await helper.textContent(), { message: "等待注册验证码提示出现" })
    .toMatch(/\d{6}/);
  return extractCode(await helper.textContent());
}

async function sendAuthCode(page, phone) {
  await page.locator('[data-auth-phone="1"]').fill(phone);
  await page.locator('[data-send-auth-code="1"]').click();
  const helper = page
    .locator('[data-auth-code="1"]')
    .locator('xpath=ancestor::div[contains(@class,"form-field")]//small[contains(@class,"helper-note")]');
  await expect
    .poll(async () => await helper.textContent(), { message: "等待登录验证码提示出现" })
    .toMatch(/\d{6}/);
  return extractCode(await helper.textContent());
}

async function setHiddenInput(page, selector, value) {
  await page.locator(selector).evaluate((element, nextValue) => {
    element.value = String(nextValue);
  }, value);
}

async function openMyPage(page) {
  await page.locator('.bottom-nav [data-page="profile"]').evaluate((element) => element.click());
  await expect(page.getByText("我的功能")).toBeVisible();
}

async function registerEnthusiast(page, { name = "测试训练者", phone = buildUniquePhone() } = {}) {
  await openRegister(page, "enthusiast");
  await page.locator('#registerForm input[name="name"]').fill(name);
  const code = await sendRegisterCode(page, phone);
  await page.locator('#registerForm input[name="verification_code"]').fill(code);
  await page.locator('#registerForm select[name="gender"]').selectOption("男");
  await setHiddenInput(page, '#registerForm input[name="height_cm"]', 171);
  await setHiddenInput(page, '#registerForm input[name="weight_kg"]', 60);
  await page.locator('#registerForm button[type="submit"]').click();
  await expect(page.locator("#registerForm")).toBeHidden({ timeout: 10000 });
  await openMyPage(page);
  await expect(page.getByText(name)).toBeVisible();
  return { name, phone };
}

async function registerCoach(page, { name = "测试教练", phone = buildUniquePhone() } = {}) {
  await openRegister(page, "coach");
  await page.locator('#registerForm input[name="name"]').fill(name);
  const code = await sendRegisterCode(page, phone);
  await page.locator('#registerForm input[name="verification_code"]').fill(code);
  await page.locator('#registerForm input[name="city"]').fill("厦门");
  await page.locator('#registerForm input[name="location"]').fill("厦门 · 思明区");
  await page.locator('#registerForm textarea[name="specialties"]').fill("力量训练 减脂塑形 私教");
  await page.locator('#registerForm input[name="years"]').fill("5");
  await setHiddenInput(page, '#registerForm input[name="price"]', "¥260/小时");
  await page.locator('#registerForm textarea[name="intro"]').fill("用于教练端注册和跨设备登录回归。");
  await page.locator('#registerForm button[type="submit"]').click();
  await expect(page.locator("#registerForm")).toBeHidden({ timeout: 10000 });
  await openMyPage(page);
  await expect(page.getByText(name)).toBeVisible();
  return { name, phone };
}

async function registerGym(page, { name = "测试健身房", phone = buildUniquePhone() } = {}) {
  await openRegister(page, "gym");
  await page.locator('#registerForm input[name="gym_name"]').fill(name);
  const code = await sendRegisterCode(page, phone);
  await page.locator('#registerForm input[name="verification_code"]').fill(code);
  await page.locator('#registerForm input[name="contact_name"]').fill("测试店长");
  await page.locator('#registerForm input[name="city"]').fill("厦门");
  await page.locator('#registerForm input[name="location"]').fill("厦门 · 思明区");
  await page.locator('#registerForm input[name="hours"]').fill("06:00 - 23:00");
  await page.locator('#registerForm input[name="price"]').fill("¥169/月起");
  await page.locator('#registerForm textarea[name="facilities"]').fill("力量区 跑步机 团课教室 淋浴");
  await page.locator('#registerForm textarea[name="intro"]').fill("用于健身房端注册和跨设备登录回归。");
  await page.locator('#registerForm button[type="submit"]').click();
  await expect(page.locator("#registerForm")).toBeHidden({ timeout: 10000 });
  await openMyPage(page);
  await expect(page.getByText(name)).toBeVisible();
  return { name, phone };
}

async function loginWithPhone(page, { phone, role = "enthusiast" }) {
  await gotoApp(page);
  await waitForBootstrapToSettle(page);
  if (await page.locator("#authForm").isVisible().catch(() => false)) {
    // already open
  } else {
    const existingLoginButton = page.getByRole("button", { name: "登录已有账户" });
    if (await existingLoginButton.isVisible().catch(() => false)) {
      await existingLoginButton.click();
    } else if (!(await page.locator(`[data-auth-role="${role}"]`).isVisible().catch(() => false))) {
      await page.locator('[data-open-role-picker="1"]').click();
      await page.getByRole("button", { name: "登录已有账户" }).click();
    }
  }
  await expect(page.locator("#authForm")).toBeVisible();
  await page.locator(`[data-auth-role="${role}"]`).click();
  const code = await sendAuthCode(page, phone);
  await page.locator('[data-auth-code="1"]').fill(code);
  await page.locator('#authForm button[type="submit"]').click();
  await page.locator("#authForm").waitFor({ state: "hidden", timeout: 3000 }).catch(() => {});
  await expect.poll(async () => await page.locator(".bottom-nav").isVisible()).toBe(true);
}

module.exports = {
  buildUniquePhone,
  gotoApp,
  openMyPage,
  registerEnthusiast,
  registerCoach,
  registerGym,
  loginWithPhone,
};
