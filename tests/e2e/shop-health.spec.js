const { test, expect } = require("@playwright/test");
const { registerEnthusiast, openMyPage } = require("./helpers");

test("训练者可以打开商城、切换分类并进入商品咨询", async ({ page }) => {
  await registerEnthusiast(page, { name: "商城测试用户" });

  await page.locator('[data-open-my-feature="shop"]').click();
  await expect(page.locator(".shop-feature")).toBeVisible();
  await expect(page.getByText("FitHub Market")).toBeVisible();
  await expect(page.getByText("燃炼六角哑铃 10kg")).toBeVisible();

  await page.locator('[data-shop-category="wearable"]').click();
  await expect(page.locator(".shop-category-chip.is-active", { hasText: "智能穿戴" })).toBeVisible();
  await expect(page.getByText("智能体脂秤")).toBeVisible();
  await expect(page.getByText("训练表带快拆款")).toBeVisible();

  await page.getByRole("button", { name: "咨询购买" }).first().click();
  await expect(page.getByText("私信", { exact: true })).toBeVisible();
  await expect(page.getByPlaceholder("输入私信内容，约课或咨询都可以")).toBeVisible();
});

test("训练者健康中心可以同步设备并切换趋势视图", async ({ page }) => {
  await registerEnthusiast(page, { name: "健康测试用户" });

  await openMyPage(page);
  await page.locator('[data-open-my-feature="health"]').click();
  await expect(page.locator(".health-center")).toBeVisible();
  await expect(page.getByText("身体数据", { exact: true })).toBeVisible();
  await expect(page.getByText("步数", { exact: true })).toBeVisible();
  await expect(page.getByText("Apple Watch", { exact: true })).toBeVisible();

  await page.locator('[data-sync-health-device="apple-watch"]').click();
  await expect(page.locator(".device-row", { hasText: "Apple Watch" }).getByText("已连接")).toBeVisible();
  await expect(page.getByText("Apple Watch 已同步", { exact: true })).toBeVisible();

  await page.locator('[data-set-health-view="all"]').first().click();
  await expect(page.getByText("总运动趋势", { exact: true })).toBeVisible();
  await expect(page.getByText("跑步", { exact: true })).toBeVisible();
  await expect(page.getByText("瑜伽", { exact: true })).toBeVisible();
});
