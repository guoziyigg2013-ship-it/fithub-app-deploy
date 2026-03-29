## FitHub Native iOS

这是一套给 FitHub 预留的原生 iOS 骨架，用来接入：

- Apple Health / HealthKit
- Apple Watch 训练数据
- 未来的原生登录与健康同步链路

当前目标不是替代现有网页，而是把“真实设备接入”这条链先搭通：

1. iPhone 原生 App 通过 `HealthKit` 读取身高、体重、体脂、静息心率、步数、活跃卡路里和最近训练。
2. Apple Watch 记录的训练会先进入 Apple Health，再由 iPhone App 统一读取。
3. App 把这些数据上传到 FitHub 现有后端 `/api/health/native-sync`。
4. 网页端继续负责展示、社交、预约和打卡结果。

### 目录说明

- `project.yml`
  XcodeGen 工程描述文件。
- `Config/Info.plist`
  iOS 配置模板。
- `Config/FitHubNative.entitlements`
  HealthKit capability 模板。
- `Sources/`
  SwiftUI 页面、网络层、HealthKit 服务和模型。

### 打开工程

当前目录已经附带：

- `FitHubNative.xcodeproj`
- `project.yml`

如果你的机器已经装了 Xcode，可以先直接打开：

```bash
open FitHubNative.xcodeproj
```

更适合直接照着跑的联调文档在这里：

- [native-device-quickstart.md](/Users/guoziyi/Documents/gpt/fitness-app-prototype/docs/native-device-quickstart.md)
- [native-ios-device-checklist.md](/Users/guoziyi/Documents/gpt/fitness-app-prototype/docs/native-ios-device-checklist.md)
- [native-ios-xcode-runbook.md](/Users/guoziyi/Documents/gpt/fitness-app-prototype/docs/native-ios-xcode-runbook.md)

如果后面你想继续用 XcodeGen 重生工程，再走下面这套：

1. 安装完整 Xcode。
2. 执行：

```bash
xcode-select -s /Applications/Xcode.app/Contents/Developer
brew install xcodegen
cd native-ios
xcodegen generate
open FitHubNative.xcodeproj
```

### 第一步能做到什么

- 用手机号 + 身份登录现有 FitHub 账户
- 请求 Apple Health 权限
- 读取近 30 天训练和关键身体指标
- 上传到现有线上服务

### Xiaomi 路线说明

小米手表 / 小米体脂秤的“真接入”不建议直接走网页。后续更稳的路线是：

- iOS：如果数据已进入 Apple Health，则仍通过 HealthKit 读取
- Android：优先接 `Health Connect`
- 小米健康云官方合作接口：仅在具备正式合作权限后再接
