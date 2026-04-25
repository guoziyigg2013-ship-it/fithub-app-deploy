const { test, expect } = require("@playwright/test");
const { registerEnthusiast } = require("./helpers");

async function mockOutdoorGps(page) {
  await page.addInitScript(() => {
    const baseTime = Date.now() - 90000;
    const routePoints = [
      { latitude: 24.4812, longitude: 118.0911, accuracy: 8, altitude: 12, timestamp: baseTime },
      { latitude: 24.48122, longitude: 118.09113, accuracy: 7, altitude: 12.8, timestamp: baseTime + 20000 },
      { latitude: 24.48125, longitude: 118.09117, accuracy: 6, altitude: 14.1, timestamp: baseTime + 42000 },
      { latitude: 24.48129, longitude: 118.09122, accuracy: 6, altitude: 15, timestamp: baseTime + 65000 }
    ];
    let watchId = 0;
    const watchTimers = new Map();
    const toPosition = (point) => ({
      coords: {
        latitude: point.latitude,
        longitude: point.longitude,
        accuracy: point.accuracy,
        altitude: point.altitude,
        altitudeAccuracy: 4,
        heading: null,
        speed: null
      },
      timestamp: point.timestamp
    });

    Object.defineProperty(navigator, "geolocation", {
      configurable: true,
      value: {
        getCurrentPosition(success) {
          window.setTimeout(() => success(toPosition(routePoints[0])), 20);
        },
        watchPosition(success) {
          const id = ++watchId;
          const timers = routePoints.slice(1).map((point, index) =>
            window.setTimeout(() => success(toPosition(point)), 160 * (index + 1))
          );
          watchTimers.set(id, timers);
          return id;
        },
        clearWatch(id) {
          (watchTimers.get(id) || []).forEach((timer) => window.clearTimeout(timer));
          watchTimers.delete(id);
        }
      }
    });
  });
}

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

test("户外行走可以采集真实 GPS 点并打开轨迹详情", async ({ page }) => {
  await mockOutdoorGps(page);
  await registerEnthusiast(page, { name: "户外轨迹测试用户" });

  await page.locator('[data-open-my-feature="checkin"]').first().click();
  await expect(page.getByText("选择日常运动")).toBeVisible();
  await page.locator('[data-toggle-common-sport="outdoor-walk"]').click();
  await page.locator('[data-save-common-sports="1"]').click();

  await expect(page.locator('[data-select-workout-sport="outdoor-walk"]')).toBeVisible();
  await page.locator('[data-select-workout-sport="outdoor-walk"]').click();
  await page.locator('[data-go-workout="1"]').click();

  await expect(page.getByText("正在记录")).toBeVisible();
  await expect(page.getByText(/已记录 [2-9] 个定位点/)).toBeVisible({ timeout: 5000 });
  await page.locator('[data-finish-workout="1"]').click();

  await expect(page.getByText("正在保存打卡")).toBeVisible();
  await expect(page.getByText("点开地图，查看更完整的轨迹详情")).toBeVisible({ timeout: 10000 });

  await page.locator("[data-open-route-map-detail]").first().click();
  await expect(page.getByRole("heading", { name: "轨迹地图" })).toBeVisible();
  await expect(page.getByText("定位点", { exact: true })).toBeVisible();
  await expect(page.getByText("这张地图正在直接使用你本次运动采集到的真实定位点。")).toBeVisible();
});
