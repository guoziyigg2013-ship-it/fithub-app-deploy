# FitHub 原生设备接入快速开始

## 当前目标

这一阶段的目标不是替代现有网页，而是把这两条“真实设备数据接入”链先跑通：

1. iPhone 通过 `HealthKit / Apple Health` 读取真实身体数据和训练数据
2. Android 通过 `Health Connect` 读取真实身体数据和训练数据

同步入口都已经接到同一个正式服务：

- 正式网址：`https://fithub-app-1btg.onrender.com/`
- 健康同步接口：`/api/health/native-sync`

## 你现在可以直接测试什么

### iPhone 路线

- 用手机号登录现有 FitHub 账户
- 读取 Apple Health 中的：
  - 身高
  - 体重
  - 体脂
  - 静息心率
  - 步数
  - 活跃卡路里
  - 最近训练
- 同步回 FitHub 线上账户

### Android 路线

- 用手机号登录现有 FitHub 账户
- 打开或安装 `Health Connect`
- 授权读取：
  - 身高
  - 体重
  - 体脂
  - 心率
  - 步数
  - 活跃卡路里
  - 训练记录
- 同步回 FitHub 线上账户

## 推荐测试顺序

1. 先跑 iPhone
   原因：你现在主要在 iPhone 上体验 FitHub，联调感知最直接
2. 再跑 Android
   原因：Health Connect 路线和小米设备路线后续都依赖它

## 真机前统一准备

1. 先确认你的 FitHub 正式网页账号能正常登录
2. 准备一个“真实测试手机号”
3. 准备一条可验证的健康数据
   - iPhone：确保 Apple Health 里至少有体重或步数
   - Android：确保 Health Connect 里至少有步数或体重
4. 先不要测试太多身份
   推荐先用 `健身爱好者`

## 文档入口

- iPhone 真机接入清单：
  [native-ios-device-checklist.md](/Users/guoziyi/Documents/gpt/fitness-app-prototype/docs/native-ios-device-checklist.md)
- Android 真机接入清单：
  [native-android-device-checklist.md](/Users/guoziyi/Documents/gpt/fitness-app-prototype/docs/native-android-device-checklist.md)
- 原生健康同步接口说明：
  [native-health-sync-api.md](/Users/guoziyi/Documents/gpt/fitness-app-prototype/docs/native-health-sync-api.md)

## 当前边界

- 网页版里的设备接入按钮仍然只是展示，不是真接入
- 真接入目前只在 `native-ios` 和 `native-android` 目录里推进
- 小米健康云直连暂时仍不是公开可直接接入的路线
  在拿到正式合作权限前，优先走 `Health Connect`

## 成功标准

当下面 4 项都成立，就说明第六步已经真正完成：

1. 原生 App 能登录你的正式 FitHub 账户
2. 原生 App 能读到真实健康数据预览
3. 点击同步后，网页版 FitHub 中能看到同步结果
4. 再次打开网页或刷新后，这些数据仍然存在
