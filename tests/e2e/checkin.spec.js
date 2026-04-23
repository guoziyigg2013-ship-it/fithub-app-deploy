const { test, expect } = require("@playwright/test");
const { registerEnthusiast } = require("./helpers");

test("训练者可以切换到室内项目并完成一次打卡", async ({ page }) => {
  await registerEnthusiast(page, { name: "打卡测试用户" });

  await page.getByRole("button", { name: /选择运动|切换项目/ }).click();
  await expect(page.getByText("选择日常运动")).toBeVisible();
  await page.getByRole("button", { name: /传统力量训练/ }).click();
  await page.getByRole("button", { name: "完成选择" }).click();

  await page.getByRole("button", { name: /传统力量训练/ }).click();
  await page.locator('[data-go-workout="1"]').click();

  await expect(page.getByText("正在记录")).toBeVisible();
  await page.locator('[data-pause-workout="1"]').click();
  await expect(page.getByRole("button", { name: "继续" })).toBeVisible();
  await page.locator('[data-pause-workout="1"]').click();
  await page.locator('[data-finish-workout="1"]').click();

  await expect(page.getByText("正在保存打卡")).toBeVisible();
  await expect(page.getByText("最近打卡")).toBeVisible();
});
