const { test, expect } = require("@playwright/test");

const TINY_PNG =
  "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wn0n8kAAAAASUVORK5CYII=";

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
